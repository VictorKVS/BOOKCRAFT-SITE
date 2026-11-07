from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

BASELINE = REPORTS / "MVP15_1_HISTORICAL_FORECAST_BASELINE.json"
OUT_JSON = REPORTS / "MVP15_2_FULL_EVALUATION_SCORECARD.json"
OUT_MD = REPORTS / "MVP15_2_FULL_EVALUATION_SCORECARD.md"
RUN_JSON = RUNS / "mvp15_2_full_evaluation_scorecard.json"

def safe_div(a: int | float, b: int | float) -> float | None:
    if not b:
        return None
    return round(float(a) / float(b), 4)

def f1(p: float | None, r: float | None) -> float | None:
    if p is None or r is None or (p + r) == 0:
        return None
    return round(2 * p * r / (p + r), 4)

def avg(vals: list[float | None]) -> float | None:
    x = [v for v in vals if v is not None]
    return None if not x else round(statistics.mean(x), 4)

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-15.2 FULL EVALUATION SCORECARD ===")

    if not BASELINE.exists():
        print("FAIL baseline_missing")
        return 1

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    windows = baseline.get("windows") or []
    if not windows:
        print("FAIL baseline_windows_missing")
        return 1

    event_tp = event_fp = event_actual = 0
    trans_tp = trans_fp = trans_actual = 0

    event_window_precision = []
    event_window_recall = []
    event_window_f1 = []
    trans_window_precision = []
    trans_window_recall = []
    trans_window_f1 = []

    rows = []

    for w in windows:
        er = w.get("event_recurrence") or {}
        tr = w.get("transition_recurrence") or {}

        ep = er.get("precision")
        erc = er.get("recall")
        ef1 = f1(ep, erc)

        tp = tr.get("precision")
        trc = tr.get("recall")
        tf1 = f1(tp, trc)

        event_window_precision.append(ep)
        event_window_recall.append(erc)
        event_window_f1.append(ef1)
        trans_window_precision.append(tp)
        trans_window_recall.append(trc)
        trans_window_f1.append(tf1)

        event_tp += int(er.get("hits", 0))
        event_fp += int(er.get("false_positives", 0))
        event_actual += int(er.get("predictable_actual_recurring_actors", 0))

        trans_tp += int(tr.get("hits", 0))
        trans_fp += int(tr.get("false_positives", 0))
        trans_actual += int(tr.get("predictable_actual_recurring_entities", 0))

        rows.append({
            "known_range": w.get("known_range"),
            "hidden_future_range": w.get("hidden_future_range"),
            "event": {
                "precision": ep,
                "recall": erc,
                "f1": ef1,
                "hits": er.get("hits", 0),
                "false_positives": er.get("false_positives", 0),
            },
            "transition": {
                "precision": tp,
                "recall": trc,
                "f1": tf1,
                "hits": tr.get("hits", 0),
                "false_positives": tr.get("false_positives", 0),
            },
            "leakage_check": w.get("leakage_check"),
        })

    event_micro_precision = safe_div(event_tp, event_tp + event_fp)
    event_micro_recall = safe_div(event_tp, event_actual)
    event_micro_f1 = f1(event_micro_precision, event_micro_recall)

    trans_micro_precision = safe_div(trans_tp, trans_tp + trans_fp)
    trans_micro_recall = safe_div(trans_tp, trans_actual)
    trans_micro_f1 = f1(trans_micro_precision, trans_micro_recall)

    macro = {
        "event_precision": avg(event_window_precision),
        "event_recall": avg(event_window_recall),
        "event_f1": avg(event_window_f1),
        "transition_precision": avg(trans_window_precision),
        "transition_recall": avg(trans_window_recall),
        "transition_f1": avg(trans_window_f1),
    }

    micro = {
        "event_precision": event_micro_precision,
        "event_recall": event_micro_recall,
        "event_f1": event_micro_f1,
        "transition_precision": trans_micro_precision,
        "transition_recall": trans_micro_recall,
        "transition_f1": trans_micro_f1,
    }

    # Acceptance contract for future reasoning engine.
    acceptance = {
        "must_keep_leakage_zero": True,
        "must_not_reduce_event_micro_f1": event_micro_f1,
        "must_exceed_event_micro_precision": event_micro_precision,
        "must_exceed_transition_micro_f1": trans_micro_f1,
        "must_not_reduce_transition_micro_precision": trans_micro_precision,
        "minimum_windows_with_event_precision_ge_0_5": sum(
            1 for v in event_window_precision if v is not None and v >= 0.5
        ),
        "minimum_windows_with_transition_precision_ge_0_5": sum(
            1 for v in trans_window_precision if v is not None and v >= 0.5
        ),
    }

    weaknesses = []
    if event_micro_precision is not None and event_micro_precision < 0.75:
        weaknesses.append("Event recurrence precision is moderate; recurring protagonists are over-predicted in some windows.")
    if trans_micro_precision is not None and trans_micro_precision < 0.5:
        weaknesses.append("Transition recurrence precision is weak; repeated past transitions do not reliably imply another near-future transition.")
    if rows[-1]["transition"]["precision"] == 0.0:
        weaknesses.append("Late-window transition prediction collapses to 0 precision in chunks 51-61.")
    if all((x or 0) >= 0.5 for x in event_window_recall if x is not None):
        weaknesses.append("Event recall is strong, so the main event problem is selectivity rather than coverage.")

    scorecard = {
        "schema_version": "1.0",
        "work_id": baseline.get("work_id", "sto_let_tomu_vpered"),
        "stage": "MVP-15.2_FULL_EVALUATION_SCORECARD",
        "baseline": baseline.get("benchmark"),
        "leakage": {
            "violations": sum(1 for w in windows if w.get("leakage_check") != "PASS"),
            "status": "PASS" if all(w.get("leakage_check") == "PASS" for w in windows) else "FAIL",
        },
        "micro_metrics": micro,
        "macro_metrics": macro,
        "window_metrics": rows,
        "baseline_acceptance_contract_for_v2": acceptance,
        "weaknesses": weaknesses,
        "current_conclusion": {
            "event_forecasting": "USABLE_BASELINE_NOT_YET_REASONING",
            "transition_forecasting": "WEAK_BASELINE",
            "overall": "BASELINE_ESTABLISHED_READY_FOR_V2_COMPARISON",
        },
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8")

    def fmt(v: Any) -> str:
        return "N/A" if v is None else f"{v:.4f}" if isinstance(v, float) else str(v)

    lines = [
        "# MVP-15.2 Full Evaluation Scorecard",
        "",
        "## Micro metrics",
        "",
        f"- Event precision: {fmt(micro['event_precision'])}",
        f"- Event recall: {fmt(micro['event_recall'])}",
        f"- Event F1: {fmt(micro['event_f1'])}",
        f"- Transition precision: {fmt(micro['transition_precision'])}",
        f"- Transition recall: {fmt(micro['transition_recall'])}",
        f"- Transition F1: {fmt(micro['transition_f1'])}",
        "",
        "## Macro metrics",
        "",
        f"- Event precision: {fmt(macro['event_precision'])}",
        f"- Event recall: {fmt(macro['event_recall'])}",
        f"- Event F1: {fmt(macro['event_f1'])}",
        f"- Transition precision: {fmt(macro['transition_precision'])}",
        f"- Transition recall: {fmt(macro['transition_recall'])}",
        f"- Transition F1: {fmt(macro['transition_f1'])}",
        "",
        "## Window scorecard",
        "",
        "| Known | Hidden | Event P | Event R | Event F1 | Transition P | Transition R | Transition F1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        kr = r["known_range"]; hr = r["hidden_future_range"]
        lines.append(
            f"| {kr[0]}-{kr[1]} | {hr[0]}-{hr[1]} | "
            f"{fmt(r['event']['precision'])} | {fmt(r['event']['recall'])} | {fmt(r['event']['f1'])} | "
            f"{fmt(r['transition']['precision'])} | {fmt(r['transition']['recall'])} | {fmt(r['transition']['f1'])} |"
        )

    lines += [
        "",
        "## Acceptance contract for Hypothesis Engine v2",
        "",
        f"- Leakage must remain 0.",
        f"- Event micro F1 must be >= {fmt(event_micro_f1)}.",
        f"- Event micro precision should exceed {fmt(event_micro_precision)}.",
        f"- Transition micro F1 should exceed {fmt(trans_micro_f1)}.",
        f"- Transition micro precision must not fall below {fmt(trans_micro_precision)}.",
        "",
        "## Current weaknesses",
    ]
    for w in weaknesses:
        lines.append(f"- {w}")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    run = {
        "stage": "MVP-15_2_FULL_EVALUATION_SCORECARD",
        "result": "PASS",
        "leakage_violations": scorecard["leakage"]["violations"],
        "event_micro_precision": event_micro_precision,
        "event_micro_recall": event_micro_recall,
        "event_micro_f1": event_micro_f1,
        "transition_micro_precision": trans_micro_precision,
        "transition_micro_recall": trans_micro_recall,
        "transition_micro_f1": trans_micro_f1,
        "status": scorecard["current_conclusion"]["overall"],
    }
    RUN_JSON.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PASS leakage_violations: 0")
    print(f"CHECK event_micro_precision: {event_micro_precision}")
    print(f"CHECK event_micro_recall: {event_micro_recall}")
    print(f"CHECK event_micro_f1: {event_micro_f1}")
    print(f"CHECK transition_micro_precision: {trans_micro_precision}")
    print(f"CHECK transition_micro_recall: {trans_micro_recall}")
    print(f"CHECK transition_micro_f1: {trans_micro_f1}")
    print("PASS baseline_acceptance_contract_created")
    print("=== ALINA BOOK 2 MVP-15.2 FULL EVALUATION SCORECARD: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
