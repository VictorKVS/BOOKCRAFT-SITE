# MVP-14B5 State Engine

- Canon claims input: 95
- State observations: 61
- World-state observations: 57
- Epistemic observations: 4
- Entities with states: 28
- Review queue: 34

## Semantics
- State Engine v1 stores observations, not inferred continuous states.
- WORLD_STATE and CHARACTER_BELIEF remain separate.
- No state persistence is inferred between textual positions.
- valid_until remains UNKNOWN unless future evidence establishes a transition.

## Invariants
- Every state originates from trusted canon.
- Every state references a known entity and trusted temporal anchor.
- Verified source evidence is mandatory.
- State IDs are deterministic.