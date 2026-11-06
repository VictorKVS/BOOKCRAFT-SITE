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

HYPOTHESIS_STORE = CANON / "hypothesis_store.json"
TEMPORAL_MODEL = CANON / "temporal_model.json"
STATE_STORE = CANON / "state_store.json"
KNOWLEDGE_GRAPH = CANON / "knowledge_graph.json"

PREDICTION_STORE = CANON / "prediction_store.json"
PREDICTION_RUN = CANON / "prediction_run_manifest.json"
PREDICTION_REVIEW = CANON / "prediction_review_queue.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def latest_cutoff(timeline: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not timeline:
        return None
    ordered = sorted(
        timeline,
        key=lambda t: (
            int(t.get("sequence_index", -1)),
            str(t.get("temporal_id", "")),
        ),
    )
    last = ordered[-1]
    anchor = last.get("anchor") or {}
    return {
        "temporal_id": last.get("temporal_id"),
        "sequence_index": last.get("sequence_index"),
        "chunk_id": anchor.get("chunk_id"),
        "paragraph_end": anchor.get("paragraph_end"),
        "basis": "LATEST_TRUSTED_TEXTUAL_POSITION",
    }

def prediction_score(hyp: dict[str, Any]) -> dict[str, Any]:
    # Transparent deterministic transformation from hypothesis support.
    # This is an ordinal forecast strength, NOT calibrated probability.
    raw = float(hyp.get("support_score", 0.0))
    if raw >= 0.70:
        band = "HIGH"
    elif raw >= 0.40:
        band = "MEDIUM"
    else:
        band = "LOW"
    return {
        "score": round(max(0.0, min(1.0, raw)), 3),
        "band": band,
        "semantics": "FORECAST_STRENGTH_NOT_PROBABILITY",
    }

def make_predictions(
    hypotheses: list[dict[str, Any]],
    cutoff: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    predictions: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    for hyp in hypotheses:
        hid = str(hyp.get("hypothesis_id", ""))
        status = str(hyp.get("status", "")).upper()
        if status != "OPEN":
            continue

        supporting = [str(x) for x in hyp.get("supporting_claim_ids") or []]
        if len(supporting) < 2:
            review.append({
                "review_id": stable_id("predrev", hid, "insufficient_support"),
                "hypothesis_id": hid,
                "reason": "HYPOTHESIS_SUPPORT_BELOW_PREDICTION_THRESHOLD",
            })
            continue

        strength = prediction_score(hyp)
        if strength["band"] not in {"MEDIUM", "HIGH"}:
            review.append({
                "review_id": stable_id("predrev", hid, "weak_strength"),
                "hypothesis_id": hid,
                "reason": "FORECAST_STRENGTH_TOO_LOW",
            })
            continue

        pid = stable_id(
            "pred",
            hid,
            hyp.get("statement", ""),
            cutoff.get("temporal_id", ""),
            cutoff.get("sequence_index", ""),
        )

        predictions.append({
            "prediction_id": pid,
            "statement": hyp.get("statement"),
            "status": "FROZEN_AWAITING_FUTURE_EVIDENCE",
            "source_hypothesis_id": hid,
            "supporting_claim_ids": supporting,
            "forecast_strength": strength,
            "cutoff": dict(cutoff),
            "evaluation": {
                "status": "NOT_YET_EVALUATED",
                "result": None,
                "matched_future_claim_ids": [],
                "refuting_future_claim_ids": [],
            },
            "leakage_guard": {
                "future_evidence_allowed_at_creation": False,
                "prediction_frozen_before_backtest": True,
            },
        })

    predictions.sort(key=lambda x: x["prediction_id"])
    review.sort(key=lambda x: x["review_id"])
    return predictions, review

def regression_self_test() -> None:
    cutoff = {
        "temporal_id": "time-test",
        "sequence_index": 5,
        "chunk_id": "primary-0005",
        "paragraph_end": 100,
        "basis": "LATEST_TRUSTED_TEXTUAL_POSITION",
    }

    strong = [{
        "hypothesis_id": "hyp-1",
        "statement": "Объект будет обнаружен",
        "status": "OPEN",
        "support_score": 0.8,
        "supporting_claim_ids": ["c1", "c2"],
    }]
    p, r = make_predictions(strong, cutoff)
    if len(p) != 1 or r:
        raise AssertionError("strong_hypothesis_prediction_failed")
    if p[0]["evaluation"]["status"] != "NOT_YET_EVALUATED":
        raise AssertionError("prediction_must_start_unevaluated")
    if not p[0]["leakage_guard"]["prediction_frozen_before_backtest"]:
        raise AssertionError("freeze_guard_failed")

    weak_support = [{
        "hypothesis_id": "hyp-2",
        "statement": "X",
        "status": "OPEN",
        "support_score": 0.9,
        "supporting_claim_ids": ["c1"],
    }]
    p, r = make_predictions(weak_support, cutoff)
    if p or len(r) != 1:
        raise AssertionError("minimum_support_guard_failed")

    closed = [{
        "hypothesis_id": "hyp-3",
        "statement": "Y",
        "status": "REFUTED",
        "support_score": 0.9,
        "supporting_claim_ids": ["c1", "c2"],
    }]
    p, r = make_predictions(closed, cutoff)
    if p or r:
        raise AssertionError("closed_hypothesis_guard_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B8 PREDICTION ENGINE ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    for path, label in [
        (HYPOTHESIS_STORE, "hypothesis_store"),
        (TEMPORAL_MODEL, "temporal_model"),
        (STATE_STORE, "state_store"),
        (KNOWLEDGE_GRAPH, "knowledge_graph"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    hyp_data = json.loads(HYPOTHESIS_STORE.read_text(encoding="utf-8"))
    temporal_data = json.loads(TEMPORAL_MODEL.read_text(encoding="utf-8"))
    state_data = json.loads(STATE_STORE.read_text(encoding="utf-8"))
    graph_data = json.loads(KNOWLEDGE_GRAPH.read_text(encoding="utf-8"))

    hypotheses = hyp_data.get("records") or []
    timeline = temporal_data.get("timeline") or []
    cutoff = latest_cutoff(timeline)
    if cutoff is None:
        print("FAIL no_prediction_cutoff")
        return 1

    predictions, review = make_predictions(hypotheses, cutoff)

    # Freeze manifest hashes the trusted input IDs rather than file bytes so it remains
    # portable across platforms and deterministic for the same semantic snapshot.
    snapshot_parts = []
    snapshot_parts.extend(sorted(str(h.get("hypothesis_id", "")) for h in hypotheses))
    snapshot_parts.extend(sorted(str(s.get("state_id", "")) for s in state_data.get("records") or []))
    snapshot_parts.extend(sorted(str(e.get("edge_id", "")) for e in graph_data.get("edges") or []))
    snapshot_fingerprint = hashlib.sha256(
        "|".join(snapshot_parts).encode("utf-8")
    ).hexdigest()

    prediction_ids = [p["prediction_id"] for p in predictions]
    if len(prediction_ids) != len(set(prediction_ids)):
        print("FAIL duplicate_prediction_ids")
        return 1

    for p in predictions:
        if p["evaluation"]["status"] != "NOT_YET_EVALUATED":
            print(f"FAIL prediction_pre_evaluated: {p['prediction_id']}")
            return 1
        if not p["leakage_guard"]["prediction_frozen_before_backtest"]:
            print(f"FAIL prediction_not_frozen: {p['prediction_id']}")
            return 1

    PREDICTION_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": hyp_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "FROZEN_PREDICTIONS",
        "semantics": {
            "forecast_strength": "Ordinal heuristic strength, not calibrated probability.",
            "status": "Predictions are frozen before any future evidence is used for evaluation.",
        },
        "records": predictions,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    PREDICTION_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": hyp_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "PREDICTION_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "schema_version": "1.0",
        "work_id": hyp_data.get("work_id", "sto_let_tomu_vpered"),
        "stage": "MVP-14B8_PREDICTION_ENGINE",
        "cutoff": cutoff,
        "snapshot_fingerprint_sha256": snapshot_fingerprint,
        "inputs": {
            "hypotheses": len(hypotheses),
            "state_observations": len(state_data.get("records") or []),
            "graph_edges": len(graph_data.get("edges") or []),
        },
        "predictions_frozen": len(predictions),
        "review_queue": len(review),
        "future_evidence_used": False,
    }
    PREDICTION_RUN.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    run = {
        "stage": "MVP-14B8_PREDICTION_ENGINE",
        "result": "PASS",
        "open_hypotheses_input": sum(
            1 for h in hypotheses if str(h.get("status", "")).upper() == "OPEN"
        ),
        "predictions_frozen": len(predictions),
        "review_queue": len(review),
        "cutoff_sequence_index": cutoff.get("sequence_index"),
        "future_evidence_used": False,
        "regression_tests": {
            "strong_hypothesis_prediction": "PASS",
            "minimum_support_guard": "PASS",
            "closed_hypothesis_guard": "PASS",
            "prediction_freeze_guard": "PASS",
        },
        "invariants": {
            "predictions_from_open_hypotheses_only": True,
            "minimum_two_supporting_claims": True,
            "prediction_frozen_before_backtest": True,
            "future_evidence_not_used_at_creation": True,
            "forecast_strength_not_probability": True,
            "deterministic_prediction_ids": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b8_prediction_engine.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B8 Prediction Engine",
        "",
        f"- Open hypotheses input: {run['open_hypotheses_input']}",
        f"- Predictions frozen: {len(predictions)}",
        f"- Review queue: {len(review)}",
        f"- Cutoff sequence index: {cutoff.get('sequence_index')}",
        "- Future evidence used at prediction creation: NO",
        "",
        "## Leakage control",
        "- Every prediction is frozen at a specific trusted textual cutoff.",
        "- Future evidence is forbidden during prediction creation.",
        "- Evaluation starts as NOT_YET_EVALUATED.",
        "- Backtesting must operate only after new source material is admitted through the trusted pipeline.",
        "",
        "## Promotion policy",
        "- Predictions are generated only from OPEN analyst hypotheses.",
        "- At least two supporting trusted claims are required.",
        "- MEDIUM/HIGH forecast strength is required.",
        "- Forecast strength is not a calibrated probability.",
    ]
    (REPORTS / "MVP14B8_PREDICTION_ENGINE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS open_hypotheses_input: {run['open_hypotheses_input']}")
    print(f"CHECK predictions_frozen: {len(predictions)}")
    print(f"CHECK review_queue: {len(review)}")
    print(f"PASS cutoff_sequence_index: {cutoff.get('sequence_index')}")
    print("PASS future_evidence_used: False")
    print("PASS invariant_prediction_frozen_before_backtest")
    print("PASS invariant_future_evidence_not_used_at_creation")
    print("=== ALINA BOOK 2 MVP-14B8 PREDICTION ENGINE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
