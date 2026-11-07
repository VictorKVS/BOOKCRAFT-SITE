# MVP-14B6 State Transition / Causal Layer

- State observations input: 61
- Trusted events input: 19
- Confirmed transitions: 8
- Explicit causal links: 1
- Review queue: 20

## Policy
- Textual succession alone never creates a state transition.
- Temporal adjacency alone never creates a causal link.
- A transition requires explicit transition evidence.
- A causal link requires explicit causal evidence.
- CHARACTER_BELIEF and WORLD_STATE are never merged into one transition.

## Regression tests
- False transition guard: PASS
- Explicit transition detection: PASS
- Explicit causality detection: PASS
- Truth-scope transition guard: PASS