# MVP-14B3 Contradiction Engine

- Canon claims input: 3
- Contradictions found: 0
- Review queue: 0

## Regression tests
- Explicit predicate opposition: PASS
- Single-valued property conflict: PASS
- Truth-scope separation: PASS
- Multi-valued false-positive guard: PASS

## Current v1 policy
- Only trusted canon claims are compared.
- CHARACTER_BELIEF and WORLD_STATE are never treated as the same truth scope.
- Explicit opposite predicates may conflict for the same subject/value.
- Different values conflict only for predicates declared single-valued.
- Temporal contradictions are intentionally deferred until normalized time is available.