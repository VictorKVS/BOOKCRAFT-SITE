# MVP-14B2.5 Canon Admission Gate

- SAFE_CANON_CANDIDATE inputs: 4
- Admission checked: 4
- CANON_ACCEPTED: 3
- CANON_REVIEW: 1
- CANON_REJECTED: 0

## Invariants
- Only SAFE_CANON_CANDIDATE inputs are processed.
- Verified source evidence is mandatory.
- Deterministic safety PASS is mandatory.
- Character beliefs stay CHARACTER_BELIEF and are not promoted to objective world-state truth.

## Reason types
- ALL_ADMISSION_CHECKS_PASSED: 3
- BELIEF_SCOPE_AMBIGUOUS: 1