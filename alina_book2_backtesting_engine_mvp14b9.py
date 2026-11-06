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

PREDICTION_STORE = CANON / "prediction_store.json"
PREDICTION_MANIFEST = CANON / "prediction_run_manifest.json"
CANON_CLAIMS = CANON / "canon_claims.json"
TEMPORAL_MODEL = CANON / "temporal_model.json"

BACKTEST_RESULTS = CANON / "backtest_results.json"
BACKTEST_MANIFEST = CANON / "backtest_manifest.json"
BACKTEST_REVIEW = CANON / "backtest_review_queue.json"

OPPOSITE_PREDICATES = {
    ("имеет", "не имеет"),
    ("является", "не является"),
    ("находится", "не находится"),
    ("существует", "не существует"),
    ("жив", "мертв"),
}
OPPOSITE_PREDICATES |= {(b, a) for a, b in list(OPPOSITE_PREDICATES)}

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9\s-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def claim_text(claim: dict[str, Any]) -> str:
    return norm(" ".join([
        str(claim.get("subject", "")),
        str(claim.get("predicate", "")),
        str(claim.get("value", "")),
    ]))

def future_claims_after_cutoff(
    claims: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
    cutoff_sequence_index: int,
) -> list[dict[str, Any]]:
    temporal_by_claim = {
        str(t.get("claim_id", "")): t
        for t in timeline
    }
    out = []
    for claim in claims:
        cid = str(claim.get("claim_id", ""))
        t = temporal_by_claim.get(cid)
        if t is None:
            continue
        seq = t.get("sequence_index")
        if seq is None or int(seq) <= int(cutoff_sequence_index):
            continue
        row = dict(claim)
        row["_sequence_index"] = int(seq)
        row["_temporal_id"] = t.get("temporal_id")
        out.append(row)
    return sorted(out, key=lambda c: (c["_sequence_index"], str(c.get("claim_id", ""))))

def evaluate_prediction(
    prediction: dict[str, Any],
    future_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    statement = norm(str(prediction.get("statement", "")))
    if not statement:
        return {
            "status": "REVIEW",
            "result": "UNSCORABLE",
            "reason": "EMPTY_PREDICTION_STATEMENT",
            "matched_future_claim_ids": [],
            "refuting_future_claim_ids": [],
        }

    matched: list[str] = []
    refuting: list[str] = []

    for claim in future_claims:
        cid = str(claim.get("claim_id", ""))
        ctext = claim_text(claim)
        value = norm(str(claim.get("value", "")))
        predicate = norm(str(claim.get("predicate", "")))

        # Conservative confirmation:
        # exact normalized value match, exact full claim text match, or prediction contained
        # as a sufficiently informative phrase in the structured claim text.
        if statement == value or statement == ctext or (
            len(statement.split()) >= 3 and statement in ctext
        ):
            matched.append(cid)
            continue

        # Conservative refutation:
        # prediction represented as "subject predicate value" and future claim has
        # the same normalized subject/value but an explicitly opposite predicate.
        parts = statement.split()
        if len(parts) >= 3:
            subject = norm(str(claim.get("subject", "")))
            cvalue = norm(str(claim.get("value", "")))
            # We cannot safely parse arbitrary prediction grammar; only explicit metadata
            # may activate structured refutation.
            meta = prediction.get("structured_target") or {}
            p_subject = norm(str(meta.get("subject", "")))
            p_predicate = norm(str(meta.get("predicate", "")))
            p_value = norm(str(meta.get("value", "")))
            if p_subject and p_predicate and p_value:
                if subject == p_subject and cvalue == p_value and (p_predicate, predicate) in OPPOSITE_PREDICATES:
                    refuting.append(cid)

    if matched and refuting:
        return {
            "status": "EVALUATED",
            "result": "MIXED",
            "reason": "FUTURE_EVIDENCE_BOTH_SUPPORTS_AND_REFUTES",
            "matched_future_claim_ids": sorted(set(matched)),
            "refuting_future_claim_ids": sorted(set(refuting)),
        }
    if matched:
        return {
            "status": "EVALUATED",
            "result": "CONFIRMED",
            "reason": "FUTURE_TRUSTED_CLAIM_MATCH",
            "matched_future_claim_ids": sorted(set(matched)),
            "refuting_future_claim_ids": [],
        }
    if refuting:
        return {
            "status": "EVALUATED",
            "result": "REFUTED",
            "reason": "FUTURE_TRUSTED_CLAIM_EXPLICITLY_OPPOSES_PREDICTION",
            "matched_future_claim_ids": [],
            "refuting_future_claim_ids": sorted(set(refuting)),
        }
    return {
        "status": "NOT_YET_EVALUATED",
        "result": None,
        "reason": "NO_MATCHING_FUTURE_EVIDENCE",
        "matched_future_claim_ids": [],
        "refuting_future_claim_ids": [],
    }

def regression_self_test() -> None:
    timeline = [
        {"claim_id": "old", "sequence_index": 1, "temporal_id": "t1"},
        {"claim_id": "new", "sequence_index": 3, "temporal_id": "t3"},
        {"claim_id": "opp", "sequence_index": 4, "temporal_id": "t4"},
    ]
    claims = [
        {"claim_id": "old", "subject": "Объект", "predicate": "имеет", "value": "ключ"},
        {"claim_id": "new", "subject": "Объект", "predicate": "имеет", "value": "секретный ключ"},
        {"claim_id": "opp", "subject": "Объект", "predicate": "не имеет", "value": "ключ"},
    ]
    future = future_claims_after_cutoff(claims, timeline, 2)
    if [c["claim_id"] for c in future] != ["new", "opp"]:
        raise AssertionError("cutoff_leakage_guard_failed")

    p1 = {"prediction_id": "p1", "statement": "секретный ключ"}
    r1 = evaluate_prediction(p1, future)
    if r1["result"] != "CONFIRMED":
        raise AssertionError("confirmation_failed")

    p2 = {
        "prediction_id": "p2",
        "statement": "Объект имеет ключ",
        "structured_target": {"subject": "Объект", "predicate": "имеет", "value": "ключ"},
    }
    r2 = evaluate_prediction(p2, future)
    if r2["result"] != "REFUTED":
        raise AssertionError("refutation_failed")

    p3 = {"prediction_id": "p3", "statement": "то, чего в будущем нет"}
    r3 = evaluate_prediction(p3, future)
    if r3["status"] != "NOT_YET_EVALUATED":
        raise AssertionError("no_evidence_guard_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B9 BACKTESTING ENGINE ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    for path, label in [
        (PREDICTION_STORE, "prediction_store"),
        (PREDICTION_MANIFEST, "prediction_run_manifest"),
        (CANON_CLAIMS, "canon_claims"),
        (TEMPORAL_MODEL, "temporal_model"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    prediction_data = json.loads(PREDICTION_STORE.read_text(encoding="utf-8"))
    pred_manifest = json.loads(PREDICTION_MANIFEST.read_text(encoding="utf-8"))
    canon = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    temporal = json.loads(TEMPORAL_MODEL.read_text(encoding="utf-8"))

    predictions = prediction_data.get("records") or []
    claims = canon.get("records") or []
    timeline = temporal.get("timeline") or []

    cutoff = pred_manifest.get("cutoff") or {}
    cutoff_seq = cutoff.get("sequence_index")
    if cutoff_seq is None:
        print("FAIL prediction_cutoff_missing")
        return 1

    if pred_manifest.get("future_evidence_used") is not False:
        print("FAIL prediction_snapshot_already_used_future_evidence")
        return 1

    future = future_claims_after_cutoff(claims, timeline, int(cutoff_seq))

    results: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    for pred in predictions:
        if str(pred.get("status", "")) != "FROZEN_AWAITING_FUTURE_EVIDENCE":
            review.append({
                "review_id": stable_id("backrev", pred.get("prediction_id", ""), "not_frozen"),
                "prediction_id": pred.get("prediction_id"),
                "reason": "PREDICTION_NOT_FROZEN",
            })
            continue

        result = evaluate_prediction(pred, future)
        results.append({
            "backtest_id": stable_id("backtest", pred.get("prediction_id", ""), cutoff_seq),
            "prediction_id": pred.get("prediction_id"),
            "prediction_statement": pred.get("statement"),
            "prediction_cutoff": pred.get("cutoff"),
            "future_claims_considered": [str(c.get("claim_id", "")) for c in future],
            "evaluation": result,
        })

    confirmed = sum(1 for r in results if r["evaluation"]["result"] == "CONFIRMED")
    refuted = sum(1 for r in results if r["evaluation"]["result"] == "REFUTED")
    mixed = sum(1 for r in results if r["evaluation"]["result"] == "MIXED")
    pending = sum(1 for r in results if r["evaluation"]["status"] == "NOT_YET_EVALUATED")

    BACKTEST_RESULTS.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": prediction_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "BACKTEST_RESULTS",
        "records": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    BACKTEST_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": prediction_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "BACKTEST_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    latest_seq = max([int(t.get("sequence_index", -1)) for t in timeline], default=-1)
    manifest = {
        "schema_version": "1.0",
        "work_id": prediction_data.get("work_id", "sto_let_tomu_vpered"),
        "stage": "MVP-14B9_BACKTESTING_ENGINE",
        "prediction_cutoff_sequence_index": int(cutoff_seq),
        "latest_available_sequence_index": latest_seq,
        "future_claims_available": len(future),
        "predictions_input": len(predictions),
        "predictions_evaluated": len(results),
        "confirmed": confirmed,
        "refuted": refuted,
        "mixed": mixed,
        "pending": pending,
        "review_queue": len(review),
        "leakage_guard": {
            "pre_cutoff_claims_excluded": True,
            "only_post_cutoff_trusted_claims_considered": True,
        },
    }
    BACKTEST_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    run = {
        "stage": "MVP-14B9_BACKTESTING_ENGINE",
        "result": "PASS",
        **manifest,
        "regression_tests": {
            "cutoff_leakage_guard": "PASS",
            "confirmation_detection": "PASS",
            "explicit_refutation_detection": "PASS",
            "no_evidence_pending_guard": "PASS",
        },
        "invariants": {
            "only_frozen_predictions_evaluated": True,
            "pre_cutoff_evidence_excluded": True,
            "only_trusted_future_claims_used": True,
            "absence_of_evidence_not_treated_as_refutation": True,
            "deterministic_backtest_ids": True,
        },
    }
    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b9_backtesting_engine.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    status = "NO_FUTURE_EVIDENCE_YET" if len(future) == 0 else "FUTURE_EVIDENCE_AVAILABLE"
    lines = [
        "# MVP-14B9 Backtesting Engine",
        "",
        f"- Predictions input: {len(predictions)}",
        f"- Future trusted claims available: {len(future)}",
        f"- Predictions evaluated: {len(results)}",
        f"- Confirmed: {confirmed}",
        f"- Refuted: {refuted}",
        f"- Mixed: {mixed}",
        f"- Pending: {pending}",
        f"- Status: {status}",
        "",
        "## Leakage policy",
        "- Claims at or before the prediction cutoff are excluded from evaluation.",
        "- Only trusted canon claims after cutoff may confirm/refute a frozen prediction.",
        "- Absence of future evidence never counts as refutation.",
        "- Unfrozen predictions are not evaluated.",
        "",
        "## Regression tests",
        "- Cutoff leakage guard: PASS",
        "- Confirmation detection: PASS",
        "- Explicit refutation detection: PASS",
        "- No-evidence pending guard: PASS",
    ]
    (REPORTS / "MVP14B9_BACKTESTING_ENGINE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS predictions_input: {len(predictions)}")
    print(f"CHECK future_claims_available: {len(future)}")
    print(f"CHECK predictions_evaluated: {len(results)}")
    print(f"CHECK confirmed: {confirmed}")
    print(f"CHECK refuted: {refuted}")
    print(f"CHECK pending: {pending}")
    print(f"CHECK status: {status}")
    print("PASS invariant_pre_cutoff_evidence_excluded")
    print("PASS invariant_absence_of_evidence_not_refutation")
    print("=== ALINA BOOK 2 MVP-14B9 BACKTESTING ENGINE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
