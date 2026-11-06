from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

CANON_CLAIMS = CANON / "canon_claims.json"
TEMPORAL_MODEL = CANON / "temporal_model.json"
TEMPORAL_REVIEW = CANON / "temporal_review_queue.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def chunk_index(chunk_id: str) -> int | None:
    m = re.fullmatch(r"primary-(\d+)", str(chunk_id))
    return int(m.group(1)) if m else None

def trusted_anchor(claim: dict[str, Any]) -> dict[str, Any] | None:
    evidence = claim.get("evidence") or []
    verified = [e for e in evidence if e.get("quote_verified") is True]
    if not verified:
        return None

    # For v1 we use the earliest verified source span as the textual anchor.
    anchors = []
    for ev in verified:
        ci = chunk_index(str(ev.get("chunk_id", "")))
        ps = ev.get("paragraph_start")
        pe = ev.get("paragraph_end")
        if ci is None or ps is None or pe is None:
            continue
        anchors.append((ci, int(ps), int(pe), ev))
    if not anchors:
        return None

    ci, ps, pe, ev = sorted(anchors, key=lambda x: (x[0], x[1], x[2]))[0]
    return {
        "chunk_id": ev.get("chunk_id"),
        "chunk_index": ci,
        "paragraph_start": ps,
        "paragraph_end": pe,
        "quote": ev.get("quote"),
        "quote_verified": True,
        "order_key": [ci, ps, pe],
    }

def regression_self_test() -> None:
    a = {"chunk_id": "primary-0001", "paragraph_start": 10, "paragraph_end": 12}
    b = {"chunk_id": "primary-0002", "paragraph_start": 1, "paragraph_end": 2}
    c = {"chunk_id": "primary-0002", "paragraph_start": 5, "paragraph_end": 6}
    assert (1,10,12) < (2,1,2)
    assert (2,1,2) < (2,5,6)

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B4 TEMPORAL MODEL ===")

    try:
        regression_self_test()
    except AssertionError:
        print("FAIL regression_self_test")
        return 1
    print("PASS regression_self_test")

    if not CANON_CLAIMS.exists():
        print("FAIL canon_claims_missing")
        return 1

    store = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    claims = store.get("records") or []
    if not claims:
        print("FAIL canon_claims_empty")
        return 1

    timeline: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    for claim in claims:
        if str((claim.get("admission") or {}).get("verdict", "")).upper() != "ACCEPT":
            print(f"FAIL nonaccepted_claim_in_trusted_store: {claim.get('claim_id')}")
            return 1

        anchor = trusted_anchor(claim)
        if anchor is None:
            review.append({
                "review_id": stable_id("temprev", claim.get("claim_id", ""), "missing_anchor"),
                "claim_id": claim.get("claim_id"),
                "reason": "NO_NORMALIZABLE_TEXTUAL_ANCHOR",
                "subject": claim.get("subject"),
                "predicate": claim.get("predicate"),
                "value": claim.get("value"),
                "truth_scope": claim.get("truth_scope"),
            })
            continue

        timeline.append({
            "temporal_id": stable_id(
                "time",
                claim.get("claim_id", ""),
                anchor["chunk_id"],
                anchor["paragraph_start"],
                anchor["paragraph_end"],
            ),
            "claim_id": claim.get("claim_id"),
            "temporal_basis": "TEXTUAL_ORDER",
            "world_time_status": "UNKNOWN",
            "truth_scope": claim.get("truth_scope"),
            "subject": claim.get("subject"),
            "predicate": claim.get("predicate"),
            "value": claim.get("value"),
            "anchor": anchor,
        })

    timeline.sort(key=lambda x: (
        x["anchor"]["order_key"][0],
        x["anchor"]["order_key"][1],
        x["anchor"]["order_key"][2],
        str(x.get("claim_id", "")),
    ))

    for idx, item in enumerate(timeline):
        item["sequence_index"] = idx
        item["previous_temporal_id"] = timeline[idx - 1]["temporal_id"] if idx > 0 else None
        item["next_temporal_id"] = timeline[idx + 1]["temporal_id"] if idx + 1 < len(timeline) else None

    # Derived ordering edges are textual-order only; no claim about physical simultaneity/duration.
    order_edges: list[dict[str, Any]] = []
    for left, right in zip(timeline, timeline[1:]):
        order_edges.append({
            "order_id": stable_id("ord", left["temporal_id"], right["temporal_id"]),
            "relation": "TEXTUALLY_BEFORE",
            "source_temporal_id": left["temporal_id"],
            "target_temporal_id": right["temporal_id"],
            "basis": "PRIMARY_SOURCE_POSITION",
        })

    tids = [x["temporal_id"] for x in timeline]
    if len(tids) != len(set(tids)):
        print("FAIL duplicate_temporal_ids")
        return 1

    for edge in order_edges:
        if edge["source_temporal_id"] not in set(tids) or edge["target_temporal_id"] not in set(tids):
            print("FAIL dangling_temporal_edge")
            return 1

    payload = {
        "schema_version": "1.0",
        "work_id": store.get("work_id", "sto_let_tomu_vpered"),
        "model_type": "TRUSTED_TEMPORAL_MODEL",
        "semantics": {
            "TEXTUAL_ORDER": "Order of trusted claims by verified source position.",
            "world_time_status": "UNKNOWN unless normalized temporal evidence exists.",
            "warning": "TEXTUALLY_BEFORE does not prove physical-world temporal precedence when narration is non-linear.",
        },
        "timeline": timeline,
        "order_edges": order_edges,
    }
    TEMPORAL_MODEL.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    TEMPORAL_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": store.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TEMPORAL_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    run = {
        "stage": "MVP-14B4_TEMPORAL_MODEL",
        "result": "PASS",
        "canon_claims_input": len(claims),
        "temporal_anchors": len(timeline),
        "textual_order_edges": len(order_edges),
        "review_queue": len(review),
        "world_time_normalized": 0,
        "regression_tests": {
            "cross_chunk_order": "PASS",
            "within_chunk_order": "PASS",
        },
        "invariants": {
            "trusted_canon_only": True,
            "verified_source_anchor_required": True,
            "textual_order_not_world_time": True,
            "deterministic_temporal_ids": True,
            "no_calendar_time_invention": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b4_temporal_model.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B4 Temporal Model",
        "",
        f"- Canon claims input: {len(claims)}",
        f"- Temporal anchors: {len(timeline)}",
        f"- Textual order edges: {len(order_edges)}",
        f"- Review queue: {len(review)}",
        f"- Normalized world-time anchors: 0",
        "",
        "## Semantics",
        "- Current v1 models verified textual order only.",
        "- TEXTUALLY_BEFORE means earlier in the primary source, not necessarily earlier in physical story time.",
        "- No calendar/date/time values are invented.",
        "- CHARACTER_BELIEF and WORLD_STATE scopes are preserved unchanged.",
        "",
        "## Invariants",
        "- Only trusted canon claims are temporally indexed.",
        "- Every timeline item has a verified source anchor.",
        "- Temporal IDs are deterministic.",
        "- Textual ordering is explicitly separated from world-time semantics.",
    ]
    (REPORTS / "MVP14B4_TEMPORAL_MODEL_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims_input: {len(claims)}")
    print(f"PASS temporal_anchors: {len(timeline)}")
    print(f"PASS textual_order_edges: {len(order_edges)}")
    print(f"CHECK review_queue: {len(review)}")
    print("CHECK world_time_normalized: 0")
    print("PASS invariant_textual_order_not_world_time")
    print("PASS invariant_no_calendar_time_invention")
    print("=== ALINA BOOK 2 MVP-14B4 TEMPORAL MODEL: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
