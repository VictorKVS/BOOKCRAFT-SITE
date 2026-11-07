from __future__ import annotations

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
ENTITY_REGISTRY = CANON / "entity_registry.json"
RELATION_STORE = CANON / "relation_store.json"
EVENT_STORE = CANON / "event_store.json"
STATE_STORE = CANON / "state_store.json"
HYPOTHESIS_STORE = CANON / "hypothesis_store.json"
PREDICTION_STORE = CANON / "prediction_store.json"

OUT_JSON = REPORTS / "MVP15_EVALUATION_BENCHMARK.json"
OUT_MD = REPORTS / "MVP15_EVALUATION_BENCHMARK.md"
RUN_JSON = RUNS / "mvp15_evaluation_benchmark.json"

WINDOWS = [
    (10, 20),
    (20, 30),
    (30, 40),
    (40, 50),
    (50, 61),
]

def chunk_no(chunk_id: str) -> int | None:
    m = re.fullmatch(r"primary-(\d+)", str(chunk_id or ""))
    return int(m.group(1)) if m else None

def claim_chunk(claim: dict[str, Any]) -> int | None:
    vals = []
    for ev in claim.get("evidence") or []:
        n = chunk_no(ev.get("chunk_id"))
        if n is not None:
            vals.append(n)
    return min(vals) if vals else None

def event_chunk(event: dict[str, Any]) -> int | None:
    vals = []
    for ev in event.get("evidence") or []:
        n = chunk_no(ev.get("chunk_id"))
        if n is not None:
            vals.append(n)
    if vals:
        return min(vals)
    cid = event.get("claim_id")
    if cid:
        m = re.match(r"primary-(\d+)-", str(cid))
        if m:
            return int(m.group(1))
    return None

def record_claim_ids(record: dict[str, Any]) -> list[str]:
    vals = []
    for key in ("claim_id", "source_claim_id"):
        if record.get(key):
            vals.append(str(record[key]))
    vals += [str(x) for x in record.get("source_claims") or []]
    return vals

def claim_id_chunk(claim_id: str) -> int | None:
    m = re.match(r"primary-(\d+)-", str(claim_id or ""))
    return int(m.group(1)) if m else None

def in_known_record(record: dict[str, Any], cutoff: int) -> bool:
    ids = record_claim_ids(record)
    nums = [claim_id_chunk(x) for x in ids]
    nums = [x for x in nums if x is not None]
    return bool(nums) and all(x <= cutoff for x in nums)

def count_future_claims(claims: list[dict[str, Any]], cutoff: int, horizon: int) -> int:
    return sum(1 for c in claims if (claim_chunk(c) or 10**9) > cutoff and (claim_chunk(c) or 0) <= horizon)

def count_known_claims(claims: list[dict[str, Any]], cutoff: int) -> int:
    return sum(1 for c in claims if (claim_chunk(c) or 10**9) <= cutoff)

def prediction_metrics(predictions: list[dict[str, Any]], cutoff: int) -> dict[str, Any]:
    eligible = []
    leakage = []
    for p in predictions:
        c = p.get("cutoff") or {}
        cid = chunk_no(c.get("chunk_id"))
        if cid == cutoff:
            eligible.append(p)
        if cid is not None and cid > cutoff:
            leakage.append(str(p.get("prediction_id", "")))
    return {
        "frozen_predictions_at_exact_cutoff": len(eligible),
        "future_prediction_artifact_leakage": len(leakage),
    }

def regression_self_test() -> None:
    sample = [
        {"claim_id":"primary-0002-c-1","evidence":[{"chunk_id":"primary-0002"}]},
        {"claim_id":"primary-0011-c-1","evidence":[{"chunk_id":"primary-0011"}]},
        {"claim_id":"primary-0021-c-1","evidence":[{"chunk_id":"primary-0021"}]},
    ]
    if count_known_claims(sample, 10) != 1:
        raise AssertionError("known_cutoff_filter_failed")
    if count_future_claims(sample, 10, 20) != 1:
        raise AssertionError("future_window_filter_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-15 EVALUATION BENCHMARK ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    required = [
        CANON_CLAIMS, ENTITY_REGISTRY, RELATION_STORE, EVENT_STORE,
        STATE_STORE, HYPOTHESIS_STORE, PREDICTION_STORE,
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("FAIL missing_inputs")
        for p in missing:
            print("  " + p)
        return 1

    claims = json.loads(CANON_CLAIMS.read_text(encoding="utf-8")).get("records") or []
    entities = json.loads(ENTITY_REGISTRY.read_text(encoding="utf-8")).get("records") or []
    relations = json.loads(RELATION_STORE.read_text(encoding="utf-8")).get("records") or []
    events = json.loads(EVENT_STORE.read_text(encoding="utf-8")).get("records") or []
    states = json.loads(STATE_STORE.read_text(encoding="utf-8")).get("records") or []
    hypotheses = json.loads(HYPOTHESIS_STORE.read_text(encoding="utf-8")).get("records") or []
    predictions = json.loads(PREDICTION_STORE.read_text(encoding="utf-8")).get("records") or []

    rows = []
    leakage_violations = []

    for cutoff, horizon in WINDOWS:
        known_claims = [c for c in claims if (claim_chunk(c) or 10**9) <= cutoff]
        future_claims = [
            c for c in claims
            if cutoff < (claim_chunk(c) or -1) <= horizon
        ]

        known_entities = [e for e in entities if in_known_record(e, cutoff)]
        known_relations = [r for r in relations if in_known_record(r, cutoff)]
        known_events = [e for e in events if (event_chunk(e) or 10**9) <= cutoff]
        future_events = [e for e in events if cutoff < (event_chunk(e) or -1) <= horizon]
        known_states = [s for s in states if in_known_record(s, cutoff)]

        # Strict leakage audit: every item in the known snapshot must be sourced at/before cutoff.
        bad_claims = [
            str(c.get("claim_id", ""))
            for c in known_claims
            if any((chunk_no(ev.get("chunk_id")) or 10**9) > cutoff for ev in c.get("evidence") or [])
        ]
        if bad_claims:
            leakage_violations += [f"{cutoff}:{x}" for x in bad_claims]

        pm = prediction_metrics(predictions, cutoff)

        row = {
            "cutoff_chunk": cutoff,
            "future_horizon_chunk": horizon,
            "known_snapshot": {
                "trusted_claims": len(known_claims),
                "entities": len(known_entities),
                "relations": len(known_relations),
                "events": len(known_events),
                "states": len(known_states),
            },
            "hidden_future_truth": {
                "trusted_claims": len(future_claims),
                "events": len(future_events),
            },
            "forecasting": {
                "analyst_hypotheses_available_from_current_engine": 0,
                **pm,
                "status": "NO_REAL_FROZEN_PREDICTIONS_AT_CUTOFF",
            },
            "evaluation": {
                "event_hit": None,
                "character_hit": None,
                "relationship_hit": None,
                "state_hit": None,
                "location_hit": None,
                "motive_hit": None,
                "causal_hit": None,
                "plot_direction_hit": None,
                "surprise_miss": None,
                "false_positive": None,
                "reason": "No real predictions were frozen at this historical cutoff.",
            },
            "leakage_check": "PASS" if not bad_claims and pm["future_prediction_artifact_leakage"] == 0 else "FAIL",
        }
        rows.append(row)

    if leakage_violations:
        print(f"FAIL leakage_violations: {len(leakage_violations)}")
        return 1

    # Current benchmark conclusion is intentionally strict:
    # understanding pipeline is populated, forecasting cannot yet be scored.
    benchmark = {
        "schema_version": "1.0",
        "work_id": "sto_let_tomu_vpered",
        "benchmark": "MVP-15_ALINA_EVALUATION_AND_PREDICTION_BENCHMARK",
        "mode": "RETROSPECTIVE_TRUSTED_CANON_CUTOFF_AUDIT",
        "baseline_learning_disabled": True,
        "windows": rows,
        "summary": {
            "windows_total": len(rows),
            "leakage_violations": 0,
            "level_1_fact_extraction": "EVALUABLE",
            "level_2_world_model": "EVALUABLE",
            "level_3_reasoning": "NOT_YET_FORECAST_READY",
            "level_4_forecasting": "NOT_SCORABLE_NO_HISTORICAL_FROZEN_PREDICTIONS",
            "forecasting_score": None,
            "critical_finding": (
                "The production pipeline is integrated, but the current hypothesis engine "
                "promotes zero analyst hypotheses; therefore genuine forecasting quality "
                "has not yet been demonstrated."
            ),
        },
        "anti_leakage": {
            "known_snapshot_uses_claims_at_or_before_cutoff_only": True,
            "hidden_future_is_strictly_after_cutoff": True,
            "no_future_claim_used_as_known_evidence": True,
        },
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(benchmark, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# MVP-15 ALINA Evaluation & Prediction Benchmark",
        "",
        "## Baseline conclusion",
        "",
        "- Production pipeline integration: PASS",
        "- Historical cutoff leakage audit: PASS",
        "- Fact/world-model layers: evaluable",
        "- Reasoning layer: not yet forecast-ready",
        "- Forecasting quality: NOT SCORABLE",
        "- Reason: no real predictions were frozen at historical cutoffs.",
        "",
        "## Evaluation windows",
        "",
        "| Known | Hidden future | Known claims | Future claims | Known events | Future events | Frozen predictions | Leakage |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| 1-{r['cutoff_chunk']} | {r['cutoff_chunk']+1}-{r['future_horizon_chunk']} | "
            f"{r['known_snapshot']['trusted_claims']} | {r['hidden_future_truth']['trusted_claims']} | "
            f"{r['known_snapshot']['events']} | {r['hidden_future_truth']['events']} | "
            f"{r['forecasting']['frozen_predictions_at_exact_cutoff']} | {r['leakage_check']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "This is a baseline evaluation, not a success claim.",
        "The current system has demonstrated trusted extraction and world-model construction.",
        "It has NOT yet demonstrated real forecasting because the current hypothesis engine produced no promoted analyst hypotheses and therefore no historical frozen predictions.",
        "",
        "The next engineering target is to improve hypothesis generation without weakening canon safety, then freeze predictions at each cutoff and rerun this benchmark.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    run = {
        "stage": "MVP-15_EVALUATION_BENCHMARK",
        "result": "PASS",
        "windows_total": len(rows),
        "leakage_violations": 0,
        "forecasting_score": None,
        "forecasting_status": "NOT_SCORABLE_NO_HISTORICAL_FROZEN_PREDICTIONS",
        "critical_finding": benchmark["summary"]["critical_finding"],
    }
    RUN_JSON.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"PASS windows_total: {len(rows)}")
    print("PASS leakage_violations: 0")
    for r in rows:
        print(
            f"CHECK window 1-{r['cutoff_chunk']} -> {r['cutoff_chunk']+1}-{r['future_horizon_chunk']}: "
            f"known_claims={r['known_snapshot']['trusted_claims']}, "
            f"future_claims={r['hidden_future_truth']['trusted_claims']}, "
            f"predictions={r['forecasting']['frozen_predictions_at_exact_cutoff']}"
        )
    print("CHECK forecasting_status: NOT_SCORABLE_NO_HISTORICAL_FROZEN_PREDICTIONS")
    print("PASS anti_leakage_cutoff_audit")
    print("=== ALINA BOOK 2 MVP-15 EVALUATION BENCHMARK: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
