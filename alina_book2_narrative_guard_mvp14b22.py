from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
EVIDENCE = PROJECT / "evidence" / "chunk_claims_v2"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

MODEL = os.environ.get("ALINA_CANON_MODEL", "qwen2.5:7b")
OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MAX_CHUNKS = int(os.environ.get("ALINA_MAX_CHUNKS", "0"))
THERMAL_PAUSE_C = int(os.environ.get("ALINA_THERMAL_PAUSE_C", "90"))
THERMAL_RESUME_C = int(os.environ.get("ALINA_THERMAL_RESUME_C", "75"))
THERMAL_POLL_SEC = int(os.environ.get("ALINA_THERMAL_POLL_SEC", "10"))
OLLAMA_TIMEOUT_SEC = int(os.environ.get("ALINA_OLLAMA_TIMEOUT_SEC", "600"))
OLLAMA_RETRIES = int(os.environ.get("ALINA_OLLAMA_RETRIES", "3"))

SYSTEM = """
Ты Narrative/Epistemic Mode Guard для литературного анализа.

Тебе дают SUBJECT, CLAIM и SOURCE QUOTE.
Определи, в каком режиме существует утверждение в тексте.

Режимы:
NARRATOR_FACT — рассказчик сообщает факт мира/событие;
CHARACTER_SPEECH — персонаж это говорит;
CHARACTER_THOUGHT — персонаж это думает;
CHARACTER_BELIEF — убеждение/предположение персонажа;
HYPOTHETICAL_SCENARIO — воображаемое "если/а что если/представил";
DREAM — сон;
ANALOGY — сравнение/образ;
FICTION_WITHIN_FICTION — содержание другой книги/рассказа/легенды внутри текста;
UNKNOWN — нельзя уверенно определить.

Также реши CANON_ELIGIBLE:
true только если quote подтверждает реальный факт текущего мира/события.
Мысль, гипотеза, сон, аналогия и fiction-within-fiction НЕ являются фактом мира сами по себе.

Верни строго JSON:
{
  "mode": "...",
  "canon_eligible": true,
  "reason": "кратко по-русски"
}
"""

def call(prompt: str) -> dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role":"system","content":SYSTEM},
            {"role":"user","content":prompt}
        ],
        "options":{"temperature":0.0}
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as r:
        payload=json.loads(r.read().decode("utf-8"))
    return json.loads(payload["message"]["content"])

def gpu_temperature_c() -> int | None:
    import subprocess
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return int(p.stdout.strip().splitlines()[0].strip())
    except Exception:
        return None

def thermal_gate(label: str) -> None:
    temp = gpu_temperature_c()
    if temp is None:
        print(f"THERMAL {label}: sensor unavailable")
        return
    print(f"THERMAL {label}: {temp}C")
    if temp < THERMAL_PAUSE_C:
        return
    print(f"THERMAL_GATE: PAUSE at {temp}C; resume <= {THERMAL_RESUME_C}C")
    while True:
        time.sleep(THERMAL_POLL_SEC)
        temp = gpu_temperature_c()
        if temp is None:
            print("THERMAL_GATE: sensor unavailable during cooldown")
            return
        print(f"THERMAL_COOLDOWN: {temp}C")
        if temp <= THERMAL_RESUME_C:
            print(f"THERMAL_GATE: RESUME at {temp}C")
            return

def retry(prompt: str) -> dict[str, Any]:
    thermal_gate("narrative-guard")
    last=None
    for attempt in range(1, OLLAMA_RETRIES+1):
        try:
            return call(prompt)
        except Exception as e:
            last=e
            if attempt < OLLAMA_RETRIES:
                time.sleep(10*attempt)
    raise last

def iter_claims(validated: dict[str, Any]):
    for mention in validated.get("mentions", []):
        for claim in mention.get("claims", []):
            yield "mention", mention.get("surface",""), claim
    for event in validated.get("events", []):
        for claim in event.get("claims", []):
            yield "event", event.get("event",""), claim
    for term in validated.get("terms", []):
        claim=term.get("definition_claim")
        if isinstance(claim, dict):
            yield "term", term.get("term",""), claim

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.2 NARRATIVE MODE GUARD ===")
    files=sorted(EVIDENCE.glob("primary-*.json"))
    if MAX_CHUNKS>0:
        files=files[:MAX_CHUNKS]
    if not files:
        print("FAIL no_claim_files")
        return 1

    checked=eligible=blocked=0
    candidate_claims=0
    modes={}

    for i,path in enumerate(files,1):
        package=json.loads(path.read_text(encoding="utf-8"))
        validated=package["validated"]
        print(f"[{i}/{len(files)}] NARRATIVE {path.stem}")

        for scope,subject,claim in iter_claims(validated):
            entailment = claim.get("entailment") or {}
            if str(entailment.get("verdict","")).upper() != "SUPPORTED":
                continue
            candidate_claims += 1
            evs=claim.get("evidence",[])
            if not evs:
                continue
            quote=evs[0].get("quote","")
            prompt=(
                f"SCOPE: {scope}\n"
                f"SUBJECT: {subject}\n"
                f"PREDICATE: {claim.get('predicate','')}\n"
                f"VALUE: {claim.get('value','')}\n"
                f"ENTAILMENT_REASON: {entailment.get('reason','')}\n"
                f"QUOTE: {quote}\n\n"
                "Важно: классифицируй статус САМОГО CLAIM в мире рассказа, "
                "а не просто грамматическую форму цитаты. "
                "Если рассказчик сообщает, что персонаж что-то сказал/попросил/увидел, "
                "сам факт этого действия может быть NARRATOR_FACT."
            )
            result=retry(prompt)
            mode=str(result.get("mode","UNKNOWN")).upper()
            canon_eligible=bool(result.get("canon_eligible",False))
            claim["narrative_mode"]={
                "mode":mode,
                "canon_eligible":canon_eligible,
                "reason":str(result.get("reason","")).strip(),
                "model":MODEL
            }
            checked+=1
            modes[mode]=modes.get(mode,0)+1
            if canon_eligible:
                claim["acceptance"]="CANON_ELIGIBLE"
                eligible+=1
            else:
                claim["acceptance"]="BLOCKED_BY_NARRATIVE_MODE"
                blocked+=1

        path.write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding="utf-8")

    REPORTS.mkdir(parents=True,exist_ok=True)
    RUNS.mkdir(parents=True,exist_ok=True)

    if candidate_claims > 0 and checked == 0:
        print(f"FAIL zero_claims_checked_with_candidates: {candidate_claims}")
        return 1

    result={
        "stage":"MVP-14B2_2_NARRATIVE_MODE_GUARD",
        "result":"PASS",
        "candidate_claims":candidate_claims,
        "files_checked":len(files),
        "claims_checked":checked,
        "canon_eligible":eligible,
        "blocked_by_narrative_mode":blocked,
        "modes":modes,
        "model":MODEL
    }
    (RUNS/"mvp14b2_2_narrative_mode_guard.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"
    )

    lines=[
        "# MVP-14B2.2 Narrative Mode Guard","",
        f"- Files checked: {len(files)}",
        f"- Candidate claims: {candidate_claims}",
        f"- Claims checked: {checked}",
        f"- CANON_ELIGIBLE: {eligible}",
        f"- BLOCKED_BY_NARRATIVE_MODE: {blocked}","",
        "## Modes"
    ]
    for k,v in sorted(modes.items()):
        lines.append(f"- {k}: {v}")
    (REPORTS/"MVP14B2_2_NARRATIVE_MODE_GUARD_SUMMARY.md").write_text(
        "\n".join(lines),encoding="utf-8"
    )

    print(f"PASS candidate_claims: {candidate_claims}")
    print(f"PASS claims_checked: {checked}")
    print(f"PASS canon_eligible: {eligible}")
    print(f"CHECK blocked_by_narrative_mode: {blocked}")
    print("=== ALINA BOOK 2 MVP-14B2.2 NARRATIVE MODE GUARD: PASS ===")
    return 0

if __name__=="__main__":
    sys.exit(main())
