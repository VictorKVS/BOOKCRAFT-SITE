# MVP-14B2.5 Canon Admission Gate

- SAFE_CANON_CANDIDATE inputs: 122
- Admission checked: 122
- CANON_ACCEPTED: 95
- CANON_REVIEW: 27
- CANON_REJECTED: 0

## Invariants
- Only SAFE_CANON_CANDIDATE inputs are processed.
- Verified source evidence is mandatory.
- Deterministic safety PASS is mandatory.
- Character beliefs stay CHARACTER_BELIEF and are not promoted to objective world-state truth.

## Reason types
- ALL_ADMISSION_CHECKS_PASSED: 95
- BELIEF_SCOPE_AMBIGUOUS: 10
- INCOMPLETE_CLAIM: 1
- PRECISION_NOT_FINAL: 16