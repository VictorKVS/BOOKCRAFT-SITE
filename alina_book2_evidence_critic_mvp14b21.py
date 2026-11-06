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
OLLAMA_TIMEOUT_SEC = int(os.environ.get("ALINA_OLLAMA_TIMEOUT_SEC", "600"))
OLLAMA_RETRIES = int(os.environ.get("ALINA_OLLAMA_RETRIES", "3"))
OLLAMA_RETRY_DELAY_SEC = int(os.environ.get("ALINA_OLLAMA_RETRY_DELAY_SEC", "10"))

SYSTEM = """
Ты Evidence Critic.
Тебе дают claim и дословную цитату из литературного источника.
Нужно определить, ДОКАЗЫВАЕТ ли именно эта цитата данный claim.

Не добавляй внешние знания.
Не додумывай владение, причинность, отношения, возраст, профессию или мотивы.
Если цитата лишь совместима с claim, но прямо его не подтверждает — PARTIAL или NOT_SUPPORTED.

Верни строго JSON:
{
  "verdict": "SUPPORTED|PARTIAL|NOT_SUPPORTED",
  "reason": "кратко по-русски"
}
"""

ALLOWED_TERM_CATEGORIES = {
    "TECHNOLOGY","DEVICE","ORGANIZATION","LOCATION","PROFESSION","SCIENCE",
    "CREATURE","SPECIES","TRANSPORT","INSTITUTION","TIME_TRAVEL",
    "SOCIAL_CONCEPT","WORLD_RULE","OTHER"
}

def call_ollama(prompt: str) -> dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "options": {"temperature": 0.0}
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        data=body,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as r:
        payload = json.loads(r.read().decode("utf-8"))
    return json.loads(payload["message"]["content"])

def call_retry(prompt: str) -> dict[str, Any]:
    last = None
    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            return call_ollama(prompt)
        except Exception as e:
            last = e
            if attempt < OLLAMA_RETRIES:
                time.sleep(OLLAMA_RETRY_DELAY_SEC * attempt)
    raise last

def norm_participant(x: Any) -> str:
    if isinstance(x, dict):
        for key in ("name","surface","character","entity"):
            if x.get(key):
                return str(x[key]).strip()
        return ""
    return str(x).strip()

def iter_claims(validated: dict[str, Any]):
    for mention in validated.get("mentions", []):
        for claim in mention.get("claims", []):
            yield "mention", mention.get("surface",""), claim
    for event in validated.get("events", []):
        for claim in event.get("claims", []):
            yield "event", event.get("event",""), claim
    for term in validated.get("terms", []):
        dc = term.get("definition_claim")
        if isinstance(dc, dict):
            yield "term", term.get("term",""), dc

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.1 EVIDENCE CRITIC ===")
    files = sorted(EVIDENCE.glob("primary-*.json"))
    if MAX_CHUNKS > 0:
        files = files[:MAX_CHUNKS]
    if not files:
        print("FAIL no_claim_files")
        return 1

    total = supported = partial = rejected = schema_fixes = 0

    for idx, path in enumerate(files, 1):
        package = json.loads(path.read_text(encoding="utf-8"))
        validated = package["validated"]

        # Normalize event participants.
        for event in validated.get("events", []):
            original = event.get("participants", [])
            normalized = [norm_participant(x) for x in original]
            normalized = [x for x in normalized if x]
            if normalized != original:
                event["participants"] = normalized
                schema_fixes += 1

        # Normalize term categories.
        for term in validated.get("terms", []):
            cat = str(term.get("category","OTHER")).upper()
            if cat not in ALLOWED_TERM_CATEGORIES:
                term["category_original"] = cat
                term["category"] = "OTHER"
                term["category_validation"] = "INVALID_CATEGORY_NORMALIZED"
                schema_fixes += 1

        print(f"[{idx}/{len(files)}] CRITIC {path.stem}")

        for scope, subject, claim in iter_claims(validated):
            if claim.get("provenance") != "SOURCE_CANON":
                continue
            if claim.get("acceptance") != "SUPPORTED":
                continue
            evs = claim.get("evidence", [])
            if not evs or not evs[0].get("quote_verified"):
                continue

            quote = evs[0].get("quote","")
            prompt = (
                f"SCOPE: {scope}\n"
                f"SUBJECT: {subject}\n"
                f"PREDICATE: {claim.get('predicate','')}\n"
                f"VALUE: {claim.get('value','')}\n"
                f"QUOTE: {quote}\n"
            )
            result = call_retry(prompt)
            verdict = str(result.get("verdict","NOT_SUPPORTED")).upper()
            if verdict not in {"SUPPORTED","PARTIAL","NOT_SUPPORTED"}:
                verdict = "NOT_SUPPORTED"

            claim["entailment"] = {
                "verdict": verdict,
                "reason": str(result.get("reason","")).strip(),
                "model": MODEL
            }
            total += 1
            if verdict == "SUPPORTED":
                claim["acceptance"] = "SUPPORTED_ENTAILED"
                supported += 1
            elif verdict == "PARTIAL":
                claim["acceptance"] = "PARTIAL_REVIEW"
                partial += 1
            else:
                claim["acceptance"] = "REJECTED_BY_EVIDENCE_CRITIC"
                rejected += 1

        package["validated"] = validated
        package["critic_stats"] = {
            "claims_checked": total,
            "supported_entailed": supported,
            "partial_review": partial,
            "rejected": rejected,
            "schema_fixes": schema_fixes
        }
        path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    result = {
        "stage": "MVP-14B2_1_EVIDENCE_CRITIC",
        "result": "PASS",
        "files_checked": len(files),
        "claims_checked": total,
        "supported_entailed": supported,
        "partial_review": partial,
        "rejected": rejected,
        "schema_fixes": schema_fixes,
        "model": MODEL
    }
    (RUNS / "mvp14b2_1_evidence_critic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.1 Evidence Critic",
        "",
        f"- Files checked: {len(files)}",
        f"- Claims checked: {total}",
        f"- SUPPORTED_ENTAILED: {supported}",
        f"- PARTIAL_REVIEW: {partial}",
        f"- REJECTED_BY_EVIDENCE_CRITIC: {rejected}",
        f"- Schema fixes: {schema_fixes}",
        "",
        "Only SUPPORTED_ENTAILED claims are eligible for later canon acceptance."
    ]
    (REPORTS / "MVP14B2_1_EVIDENCE_CRITIC_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS claims_checked: {total}")
    print(f"PASS supported_entailed: {supported}")
    print(f"CHECK partial_review: {partial}")
    print(f"CHECK rejected: {rejected}")
    print(f"PASS schema_fixes: {schema_fixes}")
    print("=== ALINA BOOK 2 MVP-14B2.1 EVIDENCE CRITIC: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
