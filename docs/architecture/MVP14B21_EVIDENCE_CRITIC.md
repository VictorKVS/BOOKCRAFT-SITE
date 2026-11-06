# MVP-14B2.1 — Evidence Entailment Critic

The first MVP-14B2 smoke proved that literal quote existence is necessary but insufficient.

A quote may exist in the chunk while failing to prove the associated claim.

This stage evaluates each already quote-verified SOURCE_CANON claim with a dedicated critic:

```text
CLAIM
+ VERIFIED SOURCE QUOTE
→ EVIDENCE CRITIC
→ SUPPORTED_ENTAILED
  | PARTIAL_REVIEW
  | REJECTED_BY_EVIDENCE_CRITIC
```

Only `SUPPORTED_ENTAILED` claims are eligible for later canon acceptance.

The stage also normalizes:
- event participant objects into plain local surfaces;
- invalid glossary categories into OTHER with an explicit validation marker.
