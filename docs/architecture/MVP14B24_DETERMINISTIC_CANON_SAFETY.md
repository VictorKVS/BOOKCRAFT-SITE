# MVP-14B2.4 — Deterministic Canon Safety Filter

LLM critics are useful but nondeterministic. Re-running the same smoke changed previously rejected claims back into accepted claims.

MVP-14B2.4 therefore adds a deterministic safety layer after the LLM precision gate.

It blocks or reviews known classes of overreach:
- relationship overreach;
- identity overreach;
- hypothetical/imagined scenario leakage;
- ownership/predicate overreach.

Output states:
- SAFE_CANON_CANDIDATE
- SAFETY_REVIEW
- REJECTED_BY_DETERMINISTIC_SAFETY

This layer does not replace later entity resolution or contradiction checks.
