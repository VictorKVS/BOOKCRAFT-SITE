# MVP-14B7 Hypothesis Engine

- Trusted claims input: 3
- Graph propositions input: 2
- Hypothesis candidates: 2
- Analyst hypotheses promoted: 0
- Review queue: 2

## Promotion policy
- Character belief alone is never promoted to an analyst hypothesis.
- At least two independent trusted claims are required.
- Promotion requires MEDIUM/HIGH heuristic support score.
- Contradicted candidates are not promoted.
- Support score is explicitly NOT a probability.

## Separation
- Canon remains immutable trusted evidence.
- Hypotheses live in a separate store and remain unproven until confirmed or refuted.