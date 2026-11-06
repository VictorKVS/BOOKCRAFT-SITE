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
SOURCES = PROJECT / "sources" / "work_chunks" / "sto_let_tomu_vpered"
STRUCTURE = PROJECT / "structure"
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
Ты Final Canon Precision Gate. Работай КОНСЕРВАТИВНО: лучше отправить claim в REVIEW, чем принять неподтверждённый факт.

Проверь CLAIM по:
1) точной цитате,
2) окружающему контексту,
3) субъекту,
4) предикату,
5) режиму повествования.

ЖЁСТКИЕ ПРАВИЛА:
- конкретная идентичность должна быть прямо установлена текстом;
- "похож на X", "то ли X", "как X" НЕ означает, что это X;
- "одноклассник/знакомый" НЕ означает "друг";
- "взял/использовал/увидел" НЕ означает "владеет";
- воображаемое, условное, мысленное и процитированное внутри рассказа НЕ является фактом текущего мира;
- если claim использует более сильный предикат, чем текст, ставь REJECT или REVIEW;
- если существительное/отношение добавлено моделью и не установлено контекстом, ставь IDENTITY_OVERREACH или RELATIONSHIP_OVERREACH;
- если сомневаешься, выбирай REVIEW, не FINAL_CANON_CANDIDATE.

ЗАПРЕЩЕНО:
- превращать догадку/фантазию/аналогию в факт мира;
- приписывать владение из факта использования;
- приписывать дружбу из факта знакомства/одноклассничества;
- давать объекту/существу более точную идентичность, чем установлено текстом;
- считать модельную интерпретацию каноном.

Верни строго JSON:
{
  "verdict": "FINAL_CANON_CANDIDATE|REVIEW|REJECT",
  "reason": "кратко по-русски",
  "error_type": "NONE|NARRATIVE_MODE|SUBJECT_MISMATCH|PREDICATE_OVERREACH|IDENTITY_OVERREACH|RELATIONSHIP_OVERREACH|CONTEXT_MISMATCH|OTHER"
}
"""

def call(prompt: str) -> dict[str, Any]:
    body=json.dumps({
        "model":MODEL,
        "stream":False,
        "format":"json",
        "messages":[
            {"role":"system","content":SYSTEM},
            {"role":"user","content":prompt}
        ],
        "options":{"temperature":0.0}
    },ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(
        OLLAMA+"/api/chat",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req,timeout=OLLAMA_TIMEOUT_SEC) as r:
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
    thermal_gate("precision-gate")
    last=None
    for attempt in range(1,OLLAMA_RETRIES+1):
        try:
            return call(prompt)
        except Exception as e:
            last=e
            if attempt<OLLAMA_RETRIES:
                time.sleep(10*attempt)
    raise last

def iter_claims(validated: dict[str, Any]):
    for mention in validated.get("mentions",[]):
        for claim in mention.get("claims",[]):
            yield "mention",mention.get("surface",""),claim
    for event in validated.get("events",[]):
        for claim in event.get("claims",[]):
            yield "event",event.get("event",""),claim
    for term in validated.get("terms",[]):
        claim=term.get("definition_claim")
        if isinstance(claim,dict):
            yield "term",term.get("term",""),claim

def context_for(chunk_id: str, claim: dict[str,Any], meta: dict[str,Any]) -> str:
    path=SOURCES/f"{chunk_id}.txt"
    if not path.exists():
        return ""
    paragraphs=[p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    evs=claim.get("evidence",[])
    if not evs:
        return ""
    ps=evs[0].get("paragraph_start")
    pe=evs[0].get("paragraph_end")
    if ps is None or pe is None:
        return ""
    rel_start=max(0,int(ps)-int(meta["start_paragraph"])-2)
    rel_end=min(len(paragraphs)-1,int(pe)-int(meta["start_paragraph"])+2)
    return "\n\n".join(paragraphs[rel_start:rel_end+1])

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.3 CANON PRECISION GATE ===")
    index=json.loads((STRUCTURE/"primary_work_chunk_index.json").read_text(encoding="utf-8"))
    meta_by_id={x["chunk_id"]:x for x in index}

    files=sorted(EVIDENCE.glob("primary-*.json"))
    if MAX_CHUNKS>0:
        files=files[:MAX_CHUNKS]
    if not files:
        print("FAIL no_claim_files")
        return 1

    checked=final_ok=review=rejected=0
    errors={}

    for i,path in enumerate(files,1):
        package=json.loads(path.read_text(encoding="utf-8"))
        validated=package["validated"]
        chunk_id=validated["chunk_id"]
        meta=meta_by_id[chunk_id]
        print(f"[{i}/{len(files)}] PRECISION {chunk_id}")

        for scope,subject,claim in iter_claims(validated):
            entailment = claim.get("entailment") or {}
            narrative = claim.get("narrative_mode") or {}
            if str(entailment.get("verdict","")).upper() != "SUPPORTED":
                continue
            if narrative.get("canon_eligible") is not True:
                continue
            evs=claim.get("evidence",[])
            quote=evs[0].get("quote","") if evs else ""
            context=context_for(chunk_id,claim,meta)
            prompt=(
                f"SCOPE: {scope}\n"
                f"SUBJECT: {subject}\n"
                f"PREDICATE: {claim.get('predicate','')}\n"
                f"VALUE: {claim.get('value','')}\n"
                f"QUOTE: {quote}\n"
                f"ENTAILMENT: {json.dumps(entailment,ensure_ascii=False)}\n"
                f"NARRATIVE: {json.dumps(narrative,ensure_ascii=False)}\n"
                f"CONTEXT:\n{context}"
            )
            result=retry(prompt)
            verdict=str(result.get("verdict","REJECT")).upper()
            if verdict not in {"FINAL_CANON_CANDIDATE","REVIEW","REJECT"}:
                verdict="REJECT"
            err=str(result.get("error_type","OTHER")).upper()
            if verdict == "REJECT" and err == "NONE":
                err = "OTHER"
            if verdict == "REVIEW" and err == "NONE":
                err = "OTHER"
            claim["precision_gate"]={
                "verdict":verdict,
                "reason":str(result.get("reason","")).strip(),
                "error_type":err,
                "model":MODEL
            }
            checked+=1
            errors[err]=errors.get(err,0)+1
            if verdict=="FINAL_CANON_CANDIDATE":
                claim["acceptance"]="FINAL_CANON_CANDIDATE"
                final_ok+=1
            elif verdict=="REVIEW":
                claim["acceptance"]="FINAL_REVIEW"
                review+=1
            else:
                claim["acceptance"]="REJECTED_BY_PRECISION_GATE"
                rejected+=1

        path.write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding="utf-8")

    if checked==0:
        print("FAIL zero_canon_eligible_claims_checked")
        return 1

    result={
        "stage":"MVP-14B2_3_CANON_PRECISION_GATE",
        "result":"PASS",
        "files_checked":len(files),
        "claims_checked":checked,
        "final_canon_candidates":final_ok,
        "review":review,
        "rejected":rejected,
        "error_types":errors,
        "model":MODEL
    }
    RUNS.mkdir(parents=True,exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)
    (RUNS/"mvp14b2_3_canon_precision_gate.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"
    )

    lines=[
        "# MVP-14B2.3 Canon Precision Gate","",
        f"- Files checked: {len(files)}",
        f"- Claims checked: {checked}",
        f"- FINAL_CANON_CANDIDATE: {final_ok}",
        f"- FINAL_REVIEW: {review}",
        f"- REJECTED: {rejected}","",
        "## Error types"
    ]
    for k,v in sorted(errors.items()):
        lines.append(f"- {k}: {v}")
    (REPORTS/"MVP14B2_3_CANON_PRECISION_GATE_SUMMARY.md").write_text(
        "\n".join(lines),encoding="utf-8"
    )

    print(f"PASS claims_checked: {checked}")
    print(f"PASS final_canon_candidates: {final_ok}")
    print(f"CHECK final_review: {review}")
    print(f"CHECK rejected: {rejected}")
    print("=== ALINA BOOK 2 MVP-14B2.3 CANON PRECISION GATE: PASS ===")
    return 0

if __name__=="__main__":
    sys.exit(main())
