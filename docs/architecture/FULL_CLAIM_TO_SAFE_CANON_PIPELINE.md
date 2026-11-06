# Full Claim-to-Safe-Canon Pipeline

This runner executes the complete claim validation line for the selected primary work:

```text
61 PRIMARY WORK CHUNKS
→ MVP-14B2 Claim Extraction
→ MVP-14B2.1 Evidence Entailment Critic
→ MVP-14B2.2 Narrative Mode Guard
→ MVP-14B2.3 Context Precision Gate
→ MVP-14B2.4 Deterministic Canon Safety
→ SAFE_CANON_CANDIDATE
```

The runner deliberately does **not** declare semantic/final canon acceptance.
After physical execution, derived artifacts must be published and audited.

Thermal policy uses the previously proven values:
- pause at >= 90 C
- resume at <= 75 C

Expected primary-work chunk count: 61.
