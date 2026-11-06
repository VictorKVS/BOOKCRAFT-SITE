from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

RUN_FILES = {
    "safety": RUNS / "mvp14b2_4_deterministic_canon_safety.json",
    "admission": RUNS / "mvp14b2_5_canon_admission.json",
    "canon": RUNS / "mvp14b2_6_canon_store.json",
    "entities": RUNS / "mvp14b2_7_entity_registry.json",
    "relations": RUNS / "mvp14b2_8_relation_event_store.json",
    "graph": RUNS / "mvp14b2_9_knowledge_graph.json",
    "contradictions": RUNS / "mvp14b3_contradiction_engine.json",
    "temporal": RUNS / "mvp14b4_temporal_model.json",
    "states": RUNS / "mvp14b5_state_engine.json",
    "causal": RUNS / "mvp14b6_state_transition_causal.json",
    "hypotheses": RUNS / "mvp14b7_hypothesis_engine.json",
    "predictions": RUNS / "mvp14b8_prediction_engine.json",
    "backtesting": RUNS / "mvp14b9_backtesting_engine.json",
    "calibration": RUNS / "mvp14b10_learning_calibration.json",
}

SCORECARD_JSON = REPORTS / "ALINA_QUALITY_SCORECARD.json"
SCORECARD_MD = REPORTS / "ALINA_QUALITY_SCORECARD.md"

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def rate(num: int | float, den: int | float) -> float | None:
    if not den:
        return None
    return round(float(num) / float(den), 4)

def pct(v: float | None) -> str:
    return "N/A" if v is None else f"{v * 100:.1f}%"

def all_pass(data: dict[str, Any]) -> bool:
    return str(data.get("result", "")).upper() == "PASS"

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B11 QUALITY SCORECARD ===")

    missing = [name for name, path in RUN_FILES.items() if not path.exists()]
    if missing:
        print("FAIL missing_run_files: " + ", ".join(missing))
        return 1

    d = {name: load(path) for name, path in RUN_FILES.items()}

    failed_stages = [name for name, row in d.items() if not all_pass(row)]
    if failed_stages:
        print("FAIL upstream_stage_not_passed: " + ", ".join(failed_stages))
        return 1

    safety = d["safety"]
    admission = d["admission"]
    canon = d["canon"]
    entities = d["entities"]
    relations = d["relations"]
    graph = d["graph"]
    contradictions = d["contradictions"]
    temporal = d["temporal"]
    states = d["states"]
    causal = d["causal"]
    hypotheses = d["hypotheses"]
    predictions = d["predictions"]
    backtesting = d["backtesting"]
    calibration = d["calibration"]

    metrics = {
        "safety_pass_rate": rate(safety.get("safe_canon_candidates", 0), safety.get("claims_checked", 0)),
        "safety_rejection_rate": rate(safety.get("rejected", 0), safety.get("claims_checked", 0)),
        "canon_admission_rate_of_safe_candidates": rate(
            admission.get("canon_accepted", 0),
            admission.get("safe_canon_inputs", 0),
        ),
        "canon_review_rate_of_safe_candidates": rate(
            admission.get("canon_review", 0),
            admission.get("safe_canon_inputs", 0),
        ),
        "entity_registration_per_canon_claim": rate(
            entities.get("entities_registered", 0),
            entities.get("canon_claims_input", 0),
        ),
        "relation_coverage_per_canon_claim": rate(
            relations.get("relations_written", 0) + relations.get("events_written", 0),
            relations.get("canon_claims_input", 0),
        ),
        "temporal_anchor_coverage": rate(
            temporal.get("temporal_anchors", 0),
            temporal.get("canon_claims_input", 0),
        ),
        "state_observation_coverage": rate(
            states.get("state_observations", 0),
            states.get("canon_claims_input", 0),
        ),
        "world_time_normalization_rate": rate(
            temporal.get("world_time_normalized", 0),
            temporal.get("temporal_anchors", 0),
        ),
        "hypothesis_promotion_rate": rate(
            hypotheses.get("analyst_hypotheses_promoted", 0),
            hypotheses.get("hypothesis_candidates", 0),
        ),
        "prediction_generation_rate": rate(
            predictions.get("predictions_frozen", 0),
            predictions.get("open_hypotheses_input", 0),
        ),
        "backtest_evaluation_rate": rate(
            backtesting.get("predictions_evaluated", 0),
            backtesting.get("predictions_input", 0),
        ),
    }

    pipeline_counts = {
        "claims_checked_by_safety": safety.get("claims_checked", 0),
        "safe_canon_candidates": safety.get("safe_canon_candidates", 0),
        "safety_rejected": safety.get("rejected", 0),
        "canon_accepted": admission.get("canon_accepted", 0),
        "canon_review": admission.get("canon_review", 0),
        "trusted_entities": entities.get("entities_registered", 0),
        "trusted_relations": relations.get("relations_written", 0),
        "trusted_events": relations.get("events_written", 0),
        "graph_nodes": (
            graph.get("entity_nodes", 0)
            + graph.get("proposition_nodes", 0)
            + graph.get("literal_nodes", 0)
            + graph.get("event_nodes", 0)
        ),
        "graph_edges": graph.get("edges", 0),
        "contradictions": contradictions.get("contradictions_found", 0),
        "temporal_anchors": temporal.get("temporal_anchors", 0),
        "world_time_normalized": temporal.get("world_time_normalized", 0),
        "state_observations": states.get("state_observations", 0),
        "confirmed_transitions": causal.get("confirmed_transitions", 0),
        "explicit_causal_links": causal.get("explicit_causal_links", 0),
        "hypothesis_candidates": hypotheses.get("hypothesis_candidates", 0),
        "analyst_hypotheses": hypotheses.get("analyst_hypotheses_promoted", 0),
        "predictions_frozen": predictions.get("predictions_frozen", 0),
        "backtests_evaluated": backtesting.get("predictions_evaluated", 0),
        "calibration_updates": calibration.get("calibration_updates_applied", 0),
    }

    # Readiness is not a single quality percentage: absence of later-stage data can mean
    # "not enough evidence yet", not "bad quality".
    layer_status = {
        "evidence_safety": "READY",
        "canon": "READY" if canon.get("canon_claims", 0) > 0 else "NO_CANON_DATA",
        "entity_graph": "READY" if graph.get("edges", 0) > 0 else "NO_GRAPH_DATA",
        "temporal_textual_order": "READY" if temporal.get("temporal_anchors", 0) > 0 else "NO_TEMPORAL_DATA",
        "world_time": "NOT_MATURE" if temporal.get("world_time_normalized", 0) == 0 else "READY",
        "state_model": "READY" if states.get("state_observations", 0) > 0 else "NO_STATE_DATA",
        "transition_causality": (
            "WAITING_FOR_EVIDENCE"
            if causal.get("confirmed_transitions", 0) == 0 and causal.get("trusted_events_input", 0) == 0
            else "READY"
        ),
        "hypothesis_reasoning": (
            "WAITING_FOR_INDEPENDENT_SUPPORT"
            if hypotheses.get("analyst_hypotheses_promoted", 0) == 0
            else "READY"
        ),
        "prediction": (
            "WAITING_FOR_HYPOTHESES"
            if predictions.get("predictions_frozen", 0) == 0
            else "READY"
        ),
        "backtesting": (
            "WAITING_FOR_FROZEN_PREDICTIONS_AND_FUTURE_EVIDENCE"
            if backtesting.get("predictions_evaluated", 0) == 0
            else "READY"
        ),
        "calibration": (
            "NOT_MATURE"
            if calibration.get("decisive_backtests", 0) < 3
            else "READY"
        ),
    }

    blockers = []
    if temporal.get("world_time_normalized", 0) == 0:
        blockers.append("No normalized world-time anchors yet; only textual order is available.")
    if relations.get("events_written", 0) == 0:
        blockers.append("No trusted events yet; transition/causal layers cannot mature on real data.")
    if hypotheses.get("analyst_hypotheses_promoted", 0) == 0:
        blockers.append("No analyst hypotheses have enough independent support for promotion.")
    if predictions.get("predictions_frozen", 0) == 0:
        blockers.append("No frozen predictions exist yet, so real backtesting cannot start.")
    if calibration.get("decisive_backtests", 0) < 3:
        blockers.append("Calibration remains at baseline until at least 3 decisive backtests exist.")

    scorecard = {
        "schema_version": "1.0",
        "work_id": "sto_let_tomu_vpered",
        "stage": "MVP-14B11_QUALITY_SCORECARD",
        "upstream_stages_passed": len(d),
        "upstream_stages_total": len(d),
        "pipeline_counts": pipeline_counts,
        "quality_metrics": metrics,
        "layer_status": layer_status,
        "current_maturity": "TRUSTED_ANALYTICAL_FOUNDATION_READY",
        "prediction_learning_maturity": "NOT_YET_DATA_MATURE",
        "blockers_to_next_maturity": blockers,
        "interpretation_rules": [
            "A zero count is not automatically a quality failure.",
            "Later analytical layers may be waiting for sufficient trusted evidence.",
            "Rates with a zero denominator are reported as null/N/A, not as zero.",
            "World-time maturity is distinct from textual-order coverage.",
            "Prediction and calibration quality cannot be scored before real frozen predictions and future evidence exist.",
        ],
    }

    SCORECARD_JSON.write_text(
        json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# ALINA BOOK 2 — Quality Scorecard",
        "",
        "## System status",
        f"- Upstream stages passed: {len(d)}/{len(d)}",
        "- Current maturity: TRUSTED_ANALYTICAL_FOUNDATION_READY",
        "- Prediction / learning maturity: NOT_YET_DATA_MATURE",
        "",
        "## Pipeline counts",
    ]
    for key, value in pipeline_counts.items():
        lines.append(f"- {key}: {value}")

    lines += ["", "## Quality metrics"]
    for key, value in metrics.items():
        lines.append(f"- {key}: {pct(value)}")

    lines += ["", "## Layer readiness"]
    for key, value in layer_status.items():
        lines.append(f"- {key}: {value}")

    lines += ["", "## Blockers to next maturity"]
    for item in blockers:
        lines.append(f"- {item}")

    lines += [
        "",
        "## Interpretation",
        "- Zero does not automatically mean failure: a layer may be conservatively waiting for evidence.",
        "- Textual order is currently complete for trusted canon, but world-time normalization is not yet available.",
        "- Real prediction quality cannot be measured until analyst hypotheses are promoted, predictions are frozen, and later trusted evidence arrives.",
        "- Calibration remains at baseline until enough decisive backtests exist.",
    ]

    SCORECARD_MD.write_text("\n".join(lines), encoding="utf-8")

    run = {
        "stage": "MVP-14B11_QUALITY_SCORECARD",
        "result": "PASS",
        "upstream_stages_passed": len(d),
        "upstream_stages_total": len(d),
        "current_maturity": scorecard["current_maturity"],
        "prediction_learning_maturity": scorecard["prediction_learning_maturity"],
        "blockers_count": len(blockers),
        "invariants": {
            "zero_not_automatically_failure": True,
            "zero_denominator_reported_as_na": True,
            "textual_time_separate_from_world_time": True,
            "prediction_quality_not_scored_without_predictions": True,
            "calibration_quality_not_scored_without_decisive_backtests": True,
        },
    }
    (RUNS / "mvp14b11_quality_scorecard.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"PASS upstream_stages: {len(d)}/{len(d)}")
    print(f"PASS canon_accepted: {pipeline_counts['canon_accepted']}")
    print(f"PASS trusted_entities: {pipeline_counts['trusted_entities']}")
    print(f"PASS graph_edges: {pipeline_counts['graph_edges']}")
    print(f"CHECK world_time_normalized: {pipeline_counts['world_time_normalized']}")
    print(f"CHECK analyst_hypotheses: {pipeline_counts['analyst_hypotheses']}")
    print(f"CHECK predictions_frozen: {pipeline_counts['predictions_frozen']}")
    print(f"CHECK decisive_backtests: {calibration.get('decisive_backtests', 0)}")
    print(f"PASS current_maturity: {scorecard['current_maturity']}")
    print(f"CHECK prediction_learning_maturity: {scorecard['prediction_learning_maturity']}")
    print("=== ALINA BOOK 2 MVP-14B11 QUALITY SCORECARD: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
