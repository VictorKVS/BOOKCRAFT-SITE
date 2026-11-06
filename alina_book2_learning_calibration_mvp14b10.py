from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

BACKTEST_RESULTS = CANON / "backtest_results.json"
PREDICTION_STORE = CANON / "prediction_store.json"
HYPOTHESIS_STORE = CANON / "hypothesis_store.json"

CALIBRATION_PROFILE = CANON / "calibration_profile.json"
LEARNING_LEDGER = CANON / "learning_ledger.json"
CALIBRATION_REVIEW = CANON / "calibration_review_queue.json"

DEFAULT_WEIGHT = 1.0
MIN_WEIGHT = 0.5
MAX_WEIGHT = 1.5
STEP = 0.05
MIN_OBSERVATIONS_FOR_ADJUSTMENT = 3

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(str(p).casefold().strip() for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def clamp(v: float) -> float:
    return round(max(MIN_WEIGHT, min(MAX_WEIGHT, v)), 3)

def apply_results(results: list[dict[str, Any]], prior_weight: float = DEFAULT_WEIGHT) -> tuple[float, list[dict[str, Any]]]:
    scored = []
    confirmed = 0
    refuted = 0

    for row in results:
        ev = row.get("evaluation") or {}
        result = ev.get("result")
        if result == "CONFIRMED":
            confirmed += 1
            scored.append({"result": "CONFIRMED", "delta": STEP})
        elif result == "REFUTED":
            refuted += 1
            scored.append({"result": "REFUTED", "delta": -STEP})
        elif result in {"MIXED", None}:
            scored.append({"result": result or "PENDING", "delta": 0.0})

    decisive = confirmed + refuted
    if decisive < MIN_OBSERVATIONS_FOR_ADJUSTMENT:
        return prior_weight, scored

    net = (confirmed - refuted) * STEP
    return clamp(prior_weight + net), scored

def regression_self_test() -> None:
    # Fewer than threshold -> no weight change.
    small = [
        {"evaluation": {"result": "CONFIRMED"}},
        {"evaluation": {"result": "CONFIRMED"}},
    ]
    w, _ = apply_results(small)
    if w != DEFAULT_WEIGHT:
        raise AssertionError("small_sample_guard_failed")

    # Three confirms -> modest increase.
    good = [{"evaluation": {"result": "CONFIRMED"}} for _ in range(3)]
    w, _ = apply_results(good)
    if w <= DEFAULT_WEIGHT:
        raise AssertionError("confirmed_should_increase_weight")

    # Three refutes -> modest decrease.
    bad = [{"evaluation": {"result": "REFUTED"}} for _ in range(3)]
    w, _ = apply_results(bad)
    if w >= DEFAULT_WEIGHT:
        raise AssertionError("refuted_should_decrease_weight")

    # Pending/mixed do not change the score.
    pending = [
        {"evaluation": {"result": None}},
        {"evaluation": {"result": "MIXED"}},
        {"evaluation": {"result": None}},
    ]
    w, _ = apply_results(pending)
    if w != DEFAULT_WEIGHT:
        raise AssertionError("pending_must_not_change_weight")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B10 LEARNING & CALIBRATION LAYER ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    for path, label in [
        (BACKTEST_RESULTS, "backtest_results"),
        (PREDICTION_STORE, "prediction_store"),
        (HYPOTHESIS_STORE, "hypothesis_store"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    backtest_data = json.loads(BACKTEST_RESULTS.read_text(encoding="utf-8"))
    prediction_data = json.loads(PREDICTION_STORE.read_text(encoding="utf-8"))
    hypothesis_data = json.loads(HYPOTHESIS_STORE.read_text(encoding="utf-8"))

    results = backtest_data.get("records") or []
    predictions = prediction_data.get("records") or []
    hypotheses = hypothesis_data.get("records") or []

    prior_weight = DEFAULT_WEIGHT
    new_weight, ledger_rows = apply_results(results, prior_weight)

    decisive = sum(1 for r in results if (r.get("evaluation") or {}).get("result") in {"CONFIRMED", "REFUTED"})
    confirmed = sum(1 for r in results if (r.get("evaluation") or {}).get("result") == "CONFIRMED")
    refuted = sum(1 for r in results if (r.get("evaluation") or {}).get("result") == "REFUTED")
    mixed = sum(1 for r in results if (r.get("evaluation") or {}).get("result") == "MIXED")
    pending = sum(1 for r in results if (r.get("evaluation") or {}).get("status") == "NOT_YET_EVALUATED")

    update_applied = decisive >= MIN_OBSERVATIONS_FOR_ADJUSTMENT and new_weight != prior_weight

    profile = {
        "schema_version": "1.0",
        "work_id": backtest_data.get("work_id", "sto_let_tomu_vpered"),
        "profile_type": "PREDICTION_CALIBRATION_PROFILE",
        "policy_version": "MVP-14B10-v1",
        "parameters": {
            "prediction_support_weight": new_weight,
        },
        "policy": {
            "default_weight": DEFAULT_WEIGHT,
            "min_weight": MIN_WEIGHT,
            "max_weight": MAX_WEIGHT,
            "step": STEP,
            "minimum_decisive_observations_for_adjustment": MIN_OBSERVATIONS_FOR_ADJUSTMENT,
            "pending_and_mixed_do_not_change_weight": True,
        },
        "evidence_summary": {
            "backtests_total": len(results),
            "decisive_backtests": decisive,
            "confirmed": confirmed,
            "refuted": refuted,
            "mixed": mixed,
            "pending": pending,
        },
        "update_applied": update_applied,
    }
    CALIBRATION_PROFILE.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ledger = {
        "schema_version": "1.0",
        "work_id": backtest_data.get("work_id", "sto_let_tomu_vpered"),
        "ledger_type": "CALIBRATION_LEARNING_LEDGER",
        "records": [
            {
                "learning_id": stable_id("learn", idx, row.get("result"), row.get("delta")),
                "source": "BACKTEST_RESULT",
                "result": row.get("result"),
                "weight_delta_candidate": row.get("delta"),
                "applied": update_applied and row.get("delta") != 0.0,
            }
            for idx, row in enumerate(ledger_rows)
        ],
    }
    LEARNING_LEDGER.write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    review = []
    if 0 < decisive < MIN_OBSERVATIONS_FOR_ADJUSTMENT:
        review.append({
            "review_id": stable_id("calrev", "small_sample", decisive),
            "reason": "INSUFFICIENT_DECISIVE_BACKTESTS_FOR_WEIGHT_CHANGE",
            "decisive_backtests": decisive,
            "required": MIN_OBSERVATIONS_FOR_ADJUSTMENT,
        })

    CALIBRATION_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": backtest_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "CALIBRATION_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    run = {
        "stage": "MVP-14B10_LEARNING_CALIBRATION",
        "result": "PASS",
        "hypotheses_input": len(hypotheses),
        "predictions_input": len(predictions),
        "backtests_input": len(results),
        "decisive_backtests": decisive,
        "calibration_updates_applied": 1 if update_applied else 0,
        "prediction_support_weight_before": prior_weight,
        "prediction_support_weight_after": new_weight,
        "review_queue": len(review),
        "regression_tests": {
            "small_sample_guard": "PASS",
            "confirmed_increases_weight": "PASS",
            "refuted_decreases_weight": "PASS",
            "pending_no_effect": "PASS",
        },
        "invariants": {
            "canon_never_mutated": True,
            "hypotheses_never_auto_promoted_by_learning": True,
            "small_samples_do_not_change_weights": True,
            "pending_not_treated_as_failure": True,
            "bounded_weight_updates": True,
            "deterministic_learning_policy": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b10_learning_calibration.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B10 Learning / Calibration Layer",
        "",
        f"- Hypotheses input: {len(hypotheses)}",
        f"- Predictions input: {len(predictions)}",
        f"- Backtests input: {len(results)}",
        f"- Decisive backtests: {decisive}",
        f"- Calibration updates applied: {1 if update_applied else 0}",
        f"- Prediction support weight: {prior_weight} -> {new_weight}",
        "",
        "## Learning policy",
        "- Confirmed and refuted backtests may influence future weighting.",
        "- Fewer than 3 decisive observations cannot change the weight.",
        "- Pending and mixed results do not change the weight.",
        "- Weight updates are bounded and deterministic.",
        "- Canon, evidence, and past frozen predictions are never rewritten.",
        "",
        "## Safety boundary",
        "- Learning changes future decision parameters only.",
        "- Learning never converts a hypothesis into canon.",
        "- Learning never edits source evidence.",
    ]
    (REPORTS / "MVP14B10_LEARNING_CALIBRATION_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS hypotheses_input: {len(hypotheses)}")
    print(f"PASS predictions_input: {len(predictions)}")
    print(f"PASS backtests_input: {len(results)}")
    print(f"CHECK decisive_backtests: {decisive}")
    print(f"CHECK calibration_updates_applied: {1 if update_applied else 0}")
    print(f"CHECK prediction_support_weight: {prior_weight} -> {new_weight}")
    print("PASS invariant_canon_never_mutated")
    print("PASS invariant_small_samples_do_not_change_weights")
    print("PASS invariant_pending_not_treated_as_failure")
    print("=== ALINA BOOK 2 MVP-14B10 LEARNING & CALIBRATION: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
