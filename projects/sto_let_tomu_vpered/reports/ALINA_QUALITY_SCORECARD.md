# ALINA BOOK 2 — Quality Scorecard

## System status
- Upstream stages passed: 14/14
- Current maturity: TRUSTED_ANALYTICAL_FOUNDATION_READY
- Prediction / learning maturity: NOT_YET_DATA_MATURE

## Pipeline counts
- claims_checked_by_safety: 139
- safe_canon_candidates: 122
- safety_rejected: 17
- canon_accepted: 95
- canon_review: 27
- trusted_entities: 46
- trusted_relations: 61
- trusted_events: 19
- graph_nodes: 119
- graph_edges: 80
- contradictions: 0
- temporal_anchors: 95
- world_time_normalized: 0
- state_observations: 61
- confirmed_transitions: 8
- explicit_causal_links: 1
- hypothesis_candidates: 2
- analyst_hypotheses: 0
- predictions_frozen: 0
- backtests_evaluated: 0
- calibration_updates: 0

## Quality metrics
- safety_pass_rate: 87.8%
- safety_rejection_rate: 12.2%
- canon_admission_rate_of_safe_candidates: 77.9%
- canon_review_rate_of_safe_candidates: 22.1%
- entity_registration_per_canon_claim: 48.4%
- relation_coverage_per_canon_claim: 84.2%
- temporal_anchor_coverage: 100.0%
- state_observation_coverage: 64.2%
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
- transition_causality: READY
- hypothesis_reasoning: WAITING_FOR_INDEPENDENT_SUPPORT
- prediction: WAITING_FOR_HYPOTHESES
- backtesting: WAITING_FOR_FROZEN_PREDICTIONS_AND_FUTURE_EVIDENCE
- calibration: NOT_MATURE

## Blockers to next maturity
- No normalized world-time anchors yet; only textual order is available.
- No analyst hypotheses have enough independent support for promotion.
- No frozen predictions exist yet, so real backtesting cannot start.
- Calibration remains at baseline until at least 3 decisive backtests exist.

## Interpretation
- Zero does not automatically mean failure: a layer may be conservatively waiting for evidence.
- Textual order is currently complete for trusted canon, but world-time normalization is not yet available.
- Real prediction quality cannot be measured until analyst hypotheses are promoted, predictions are frozen, and later trusted evidence arrives.
- Calibration remains at baseline until enough decisive backtests exist.