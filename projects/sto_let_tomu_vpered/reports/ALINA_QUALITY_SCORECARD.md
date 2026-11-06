# ALINA BOOK 2 — Quality Scorecard

## System status
- Upstream stages passed: 14/14
- Current maturity: TRUSTED_ANALYTICAL_FOUNDATION_READY
- Prediction / learning maturity: NOT_YET_DATA_MATURE

## Pipeline counts
- claims_checked_by_safety: 9
- safe_canon_candidates: 4
- safety_rejected: 5
- canon_accepted: 3
- canon_review: 1
- trusted_entities: 3
- trusted_relations: 3
- trusted_events: 0
- graph_nodes: 6
- graph_edges: 3
- contradictions: 0
- temporal_anchors: 3
- world_time_normalized: 0
- state_observations: 3
- confirmed_transitions: 0
- explicit_causal_links: 0
- hypothesis_candidates: 2
- analyst_hypotheses: 0
- predictions_frozen: 0
- backtests_evaluated: 0
- calibration_updates: 0

## Quality metrics
- safety_pass_rate: 44.4%
- safety_rejection_rate: 55.6%
- canon_admission_rate_of_safe_candidates: 75.0%
- canon_review_rate_of_safe_candidates: 25.0%
- entity_registration_per_canon_claim: 100.0%
- relation_coverage_per_canon_claim: 100.0%
- temporal_anchor_coverage: 100.0%
- state_observation_coverage: 100.0%
- world_time_normalization_rate: 0.0%
- hypothesis_promotion_rate: 0.0%
- prediction_generation_rate: N/A
- backtest_evaluation_rate: N/A

## Layer readiness
- evidence_safety: READY
- canon: READY
- entity_graph: READY
- temporal_textual_order: READY
- world_time: NOT_MATURE
- state_model: READY
- transition_causality: WAITING_FOR_EVIDENCE
- hypothesis_reasoning: WAITING_FOR_INDEPENDENT_SUPPORT
- prediction: WAITING_FOR_HYPOTHESES
- backtesting: WAITING_FOR_FROZEN_PREDICTIONS_AND_FUTURE_EVIDENCE
- calibration: NOT_MATURE

## Blockers to next maturity
- No normalized world-time anchors yet; only textual order is available.
- No trusted events yet; transition/causal layers cannot mature on real data.
- No analyst hypotheses have enough independent support for promotion.
- No frozen predictions exist yet, so real backtesting cannot start.
- Calibration remains at baseline until at least 3 decisive backtests exist.

## Interpretation
- Zero does not automatically mean failure: a layer may be conservatively waiting for evidence.
- Textual order is currently complete for trusted canon, but world-time normalization is not yet available.
- Real prediction quality cannot be measured until analyst hypotheses are promoted, predictions are frozen, and later trusted evidence arrives.
- Calibration remains at baseline until enough decisive backtests exist.