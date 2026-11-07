from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
SOURCES = PROJECT / "sources" / "work_chunks" / "sto_let_tomu_vpered"
STRUCTURE = PROJECT / "structure"
STATE = PROJECT / "state"
EVIDENCE = PROJECT / "evidence"
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
OLLAMA_RETRY_DELAY_SEC = int(os.environ.get("ALINA_OLLAMA_RETRY_DELAY_SEC", "15"))
OLLAMA_TIMEOUT_STEP_SEC = int(os.environ.get("ALINA_OLLAMA_TIMEOUT_STEP_SEC", "300"))

SYSTEM = r"""
Ты ALINA Analyst. Анализируй ТОЛЬКО данный фрагмент литературного источника.

КРИТИЧЕСКИЕ ПРАВИЛА:
1. Не объединяй персонажей между фрагментами.
2. Имя вроде "Коля" — это только локальное упоминание (mention), а не глобальный entity_id.
3. Пиши нормализованные факты по-русски.
4. SOURCE_CANON разрешён только для факта, прямо поддержанного текстом.
5. Для КАЖДОГО SOURCE_CANON обязательно дай короткую ДОСЛОВНУЮ цитату из входного фрагмента.
6. Не переводи цитату и не пересказывай её.
7. Если факт является выводом, ставь DERIVED.
8. Если не уверен — HYPOTHESIS.
9. Не используй кино/сериал/внешние знания.
10. Не создавай "правила мира" из обычных бытовых наблюдений.

Верни СТРОГО JSON без markdown:

{
  "mentions": [
    {
      "surface": "",
      "entity_type": "CHARACTER|LOCATION|OBJECT|ORGANIZATION|SPECIES|CREATURE|TECHNOLOGY|OTHER",
      "aliases": [],
      "claims": [
        {
          "predicate": "",
          "value": "",
          "provenance": "SOURCE_CANON|DERIVED|HYPOTHESIS",
          "confidence": "CONFIRMED|PROBABLE|POSSIBLE",
          "quote": ""
        }
      ]
    }
  ],
  "events": [
    {
      "event": "",
      "participants": [],
      "location": "",
      "claims": [
        {
          "predicate": "",
          "value": "",
          "provenance": "SOURCE_CANON|DERIVED|HYPOTHESIS",
          "confidence": "CONFIRMED|PROBABLE|POSSIBLE",
          "quote": ""
        }
      ]
    }
  ],
  "terms": [
    {
      "term": "",
      "category": "TECHNOLOGY|DEVICE|ORGANIZATION|LOCATION|PROFESSION|SCIENCE|CREATURE|SPECIES|TRANSPORT|INSTITUTION|TIME_TRAVEL|SOCIAL_CONCEPT|WORLD_RULE|OTHER",
      "definition_claim": {
        "predicate": "definition",
        "value": "",
        "provenance": "SOURCE_CANON|DERIVED|HYPOTHESIS",
        "confidence": "CONFIRMED|PROBABLE|POSSIBLE",
        "quote": ""
      }
    }
  ],
  "unresolved": [
    {"question": "", "reason": ""}
  ]
}

Цитата должна быть максимально короткой, но достаточной для доказательства claim.
"""

def ollama_available() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False

def call_ollama(prompt: str, timeout_sec: int) -> dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.05},
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as r:
        payload = json.loads(r.read().decode("utf-8"))
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

def thermal_gate(chunk_id: str) -> None:
    temp = gpu_temperature_c()
    if temp is None:
        print(f"THERMAL {chunk_id}: sensor unavailable")
        return
    print(f"THERMAL {chunk_id}: {temp}C")
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

def call_with_retry(prompt: str, chunk_id: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            if attempt > 1:
                thermal_gate(chunk_id)
            timeout_sec = OLLAMA_TIMEOUT_SEC + (attempt - 1) * OLLAMA_TIMEOUT_STEP_SEC
            print(f"OLLAMA {chunk_id}: attempt {attempt}/{OLLAMA_RETRIES}, timeout={timeout_sec}s")
            return call_ollama(prompt, timeout_sec)
        except Exception as e:
            last_error = e
            print(f"WARN {chunk_id}: attempt {attempt} failed: {type(e).__name__}: {e}")
            if attempt < OLLAMA_RETRIES:
                delay = OLLAMA_RETRY_DELAY_SEC * attempt
                print(f"RETRY {chunk_id}: sleeping {delay}s")
                time.sleep(delay)
    assert last_error is not None
    raise last_error

def norm(s: str) -> str:
    s = (s or "").replace("ё", "е").replace("Ё", "Е")
    s = s.replace("«", '"').replace("»", '"').replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().casefold()

def locate_quote(paragraphs: list[str], quote: str, absolute_start: int) -> tuple[int, int] | None:
    q = norm(quote)
    if not q:
        return None
    for i in range(len(paragraphs)):
        for width in (1, 2, 3):
            j = i + width
            if j > len(paragraphs):
                continue
            candidate = norm(" ".join(paragraphs[i:j]))
            if q in candidate:
                return absolute_start + i, absolute_start + j - 1
    return None

def validate_claim(
    claim: dict[str, Any],
    paragraphs: list[str],
    absolute_start: int,
    chunk_id: str,
    claim_no: int,
) -> dict[str, Any]:
    provenance = str(claim.get("provenance", "HYPOTHESIS")).upper()
    if provenance not in {"SOURCE_CANON", "DERIVED", "HYPOTHESIS"}:
        provenance = "HYPOTHESIS"

    confidence = str(claim.get("confidence", "POSSIBLE")).upper()
    if confidence not in {"CONFIRMED", "PROBABLE", "POSSIBLE"}:
        confidence = "POSSIBLE"

    quote = str(claim.get("quote", "") or "").strip()
    loc = locate_quote(paragraphs, quote, absolute_start) if quote else None

    if provenance == "SOURCE_CANON":
        acceptance = "SUPPORTED" if loc else "UNSUPPORTED"
    elif provenance == "DERIVED":
        acceptance = "DERIVED_REVIEW"
    else:
        acceptance = "HYPOTHESIS_REVIEW"

    evidence = []
    if loc:
        evidence.append({
            "chunk_id": chunk_id,
            "paragraph_start": loc[0],
            "paragraph_end": loc[1],
            "quote": quote,
            "quote_verified": True,
        })
    elif quote:
        evidence.append({
            "chunk_id": chunk_id,
            "paragraph_start": None,
            "paragraph_end": None,
            "quote": quote,
            "quote_verified": False,
        })

    return {
        "claim_id": f"{chunk_id}-c-{claim_no:04d}",
        "predicate": str(claim.get("predicate", "")).strip(),
        "value": str(claim.get("value", "")).strip(),
        "provenance": provenance,
        "confidence": confidence,
        "acceptance": acceptance,
        "evidence": evidence,
    }

def validate_chunk(raw: dict[str, Any], text: str, meta: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    chunk_id = meta["chunk_id"]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    claim_no = 0
    mention_no = 0
    supported = unsupported = derived = hypotheses = 0

    def convert_claim(claim: dict[str, Any]) -> dict[str, Any]:
        nonlocal claim_no, supported, unsupported, derived, hypotheses
        claim_no += 1
        out = validate_claim(claim, paragraphs, meta["start_paragraph"], chunk_id, claim_no)
        if out["acceptance"] == "SUPPORTED":
            supported += 1
        elif out["acceptance"] == "UNSUPPORTED":
            unsupported += 1
        elif out["acceptance"] == "DERIVED_REVIEW":
            derived += 1
        else:
            hypotheses += 1
        return out

    mentions = []
    for item in raw.get("mentions", []):
        surface = str(item.get("surface", "")).strip()
        if not surface:
            continue
        mention_no += 1
        mentions.append({
            "mention_id": f"{chunk_id}-m-{mention_no:04d}",
            "surface": surface,
            "entity_type": str(item.get("entity_type", "OTHER")).upper(),
            "aliases": [str(x).strip() for x in item.get("aliases", []) if str(x).strip()],
            "claims": [convert_claim(c) for c in item.get("claims", []) if isinstance(c, dict)],
        })

    events = []
    for idx, item in enumerate(raw.get("events", []), 1):
        events.append({
            "event_id": f"{chunk_id}-e-{idx:04d}",
            "event": str(item.get("event", "")).strip(),
            "participants": [str(x).strip() for x in item.get("participants", []) if str(x).strip()],
            "location": str(item.get("location", "")).strip(),
            "claims": [convert_claim(c) for c in item.get("claims", []) if isinstance(c, dict)],
        })

    terms = []
    for idx, item in enumerate(raw.get("terms", []), 1):
        dc = item.get("definition_claim") if isinstance(item.get("definition_claim"), dict) else {}
        terms.append({
            "term_id": f"{chunk_id}-t-{idx:04d}",
            "term": str(item.get("term", "")).strip(),
            "category": str(item.get("category", "OTHER")).upper(),
            "definition_claim": convert_claim(dc) if dc else None,
        })

    validated = {
        "schema_version": "2.0",
        "work_id": "sto_let_tomu_vpered",
        "chunk_id": chunk_id,
        "start_paragraph": meta["start_paragraph"],
        "end_paragraph": meta["end_paragraph"],
        "mentions": mentions,
        "events": events,
        "terms": terms,
        "unresolved": raw.get("unresolved", []),
    }
    stats = {
        "claims_total": claim_no,
        "source_supported": supported,
        "source_unsupported": unsupported,
        "derived": derived,
        "hypotheses": hypotheses,
        "mentions": len(mentions),
        "events": len(events),
        "terms": len(terms),
    }
    return validated, stats

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2 CLAIM-LEVEL CANON ANALYZER ===")
    if not ollama_available():
        print(f"FAIL ollama_not_available: {OLLAMA}")
        return 1

    index_path = STRUCTURE / "primary_work_chunk_index.json"
    if not index_path.exists():
        print("FAIL primary_work_chunk_index_missing")
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))
    if MAX_CHUNKS > 0:
        index = index[:MAX_CHUNKS]
        print(f"MODE: LIMITED {len(index)} chunks")
    else:
        print(f"MODE: FULL {len(index)} chunks")

    print(f"MODEL: {MODEL}")
    print(f"THERMAL POLICY: pause >= {THERMAL_PAUSE_C}C, resume <= {THERMAL_RESUME_C}C")
    print(
        f"OLLAMA POLICY: base_timeout={OLLAMA_TIMEOUT_SEC}s, "
        f"timeout_step={OLLAMA_TIMEOUT_STEP_SEC}s, retries={OLLAMA_RETRIES}"
    )

    for d in (STATE, EVIDENCE, REPORTS, RUNS):
        d.mkdir(parents=True, exist_ok=True)
    partial_dir = EVIDENCE / "chunk_claims_v2"
    partial_dir.mkdir(parents=True, exist_ok=True)

    aggregate = {
        "schema_version": "2.0",
        "work_id": "sto_let_tomu_vpered",
        "model": MODEL,
        "chunks_analyzed": 0,
        "mentions": [],
        "events": [],
        "terms": [],
        "unresolved": [],
    }
    totals = {
        "claims_total": 0,
        "source_supported": 0,
        "source_unsupported": 0,
        "derived": 0,
        "hypotheses": 0,
        "mentions": 0,
        "events": 0,
        "terms": 0,
    }

    for i, meta in enumerate(index, 1):
        chunk_id = meta["chunk_id"]
        chunk_path = SOURCES / f"{chunk_id}.txt"
        out_path = partial_dir / f"{chunk_id}.json"
        if not chunk_path.exists():
            print(f"FAIL source_chunk_missing: {chunk_path}")
            return 1

        if out_path.exists():
            package = json.loads(out_path.read_text(encoding="utf-8"))
            validated = package["validated"]
            stats = package["stats"]
            print(f"[{i}/{len(index)}] REUSE {chunk_id}")
        else:
            thermal_gate(chunk_id)
            text = chunk_path.read_text(encoding="utf-8")
            prompt = (
                f"WORK: Сто лет тому вперед (Гостья из будущего)\n"
                f"CHUNK: {chunk_id}\n"
                f"PARAGRAPHS: {meta['start_paragraph']}..{meta['end_paragraph']}\n\n"
                f"{text}"
            )
            print(f"[{i}/{len(index)}] ANALYZE {chunk_id}")
            try:
                raw = call_with_retry(prompt, chunk_id)
                validated, stats = validate_chunk(raw, text, meta)
            except Exception as e:
                print(f"FAIL chunk_analysis {chunk_id}: {type(e).__name__}: {e}")
                return 1

            out_path.write_text(
                json.dumps({"validated": validated, "stats": stats}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        aggregate["mentions"].extend(validated.get("mentions", []))
        aggregate["events"].extend(validated.get("events", []))
        aggregate["terms"].extend(validated.get("terms", []))
        aggregate["unresolved"].extend(validated.get("unresolved", []))
        aggregate["chunks_analyzed"] += 1
        for key in totals:
            totals[key] += int(stats.get(key, 0))

    aggregate["validation_summary"] = totals
    (STATE / "literary_claims_raw_v2.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    result = {
        "stage": "MVP-14B2_CLAIM_LEVEL_CANON",
        "result": "PASS",
        "work_id": "sto_let_tomu_vpered",
        "chunks_analyzed": aggregate["chunks_analyzed"],
        "model": MODEL,
        **totals,
    }
    (RUNS / "mvp14b2_claim_level_canon.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2 Claim-Level Canon Analysis",
        "",
        f"- Model: {MODEL}",
        f"- Chunks analyzed: {aggregate['chunks_analyzed']}",
        f"- Mentions: {totals['mentions']}",
        f"- Events: {totals['events']}",
        f"- Terms: {totals['terms']}",
        f"- Claims total: {totals['claims_total']}",
        f"- SOURCE_CANON supported: {totals['source_supported']}",
        f"- SOURCE_CANON unsupported: {totals['source_unsupported']}",
        f"- DERIVED: {totals['derived']}",
        f"- HYPOTHESIS: {totals['hypotheses']}",
        "",
        "Execution status: PASS.",
        "Semantic acceptance is deferred to MVP-14C entity resolution and contradiction review.",
    ]
    (REPORTS / "MVP14B2_CLAIM_LEVEL_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"PASS chunks_analyzed: {aggregate['chunks_analyzed']}")
    print(f"PASS claims_total: {totals['claims_total']}")
    print(f"PASS source_supported: {totals['source_supported']}")
    print(f"CHECK source_unsupported: {totals['source_unsupported']}")
    print(f"PASS mentions: {totals['mentions']}")
    print(f"PASS terms: {totals['terms']}")
    print("=== ALINA BOOK 2 MVP-14B2 CLAIM-LEVEL CANON: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
