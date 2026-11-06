# MVP-14C Precheck

This deterministic stage audits raw MVP-14B output before canon reconciliation.

It checks:
- oversized chapter / structural boundary anomalies;
- duplicate surface-name entities;
- transliteration/alias candidates;
- mixed-script contamination;
- evidence entries that look like model paraphrases instead of source quotations;
- obvious contradictions inside merged entities.

A result of CONDITIONAL is expected on the current raw dataset. The goal is to prove that the validator catches the exact algorithmic defects identified during GitHub review.

After the precheck:
1. publish results;
2. review findings;
3. implement entity-resolution and claim-level evidence repair;
4. rerun regression.
