# Full Trusted Analytical Pipeline

This runner executes the complete ALINA BOOK 2 production line for the selected primary work.

```text
61 PRIMARY WORK CHUNKS
→ MVP-14B2 Claim Extraction
→ MVP-14B2.1 Evidence Entailment Critic
→ MVP-14B2.2 Narrative Mode Guard
→ MVP-14B2.3 Context Precision Gate
→ MVP-14B2.4 Deterministic Canon Safety
→ MVP-14B2.5 Canon Admission
→ MVP-14B2.6 Canon Store
→ MVP-14B2.7 Entity Registry
→ MVP-14B2.8 Relation / Event Store
→ MVP-14B2.9 Knowledge Graph
→ MVP-14B3 Contradiction Engine
→ MVP-14B4 Temporal Model
→ MVP-14B5 State Engine
→ MVP-14B6 State Transition / Causal Layer
→ MVP-14B7 Hypothesis Engine
→ MVP-14B8 Prediction Engine
→ MVP-14B9 Backtesting Engine
→ MVP-14B10 Learning / Calibration
→ MVP-14B11 Quality Scorecard
```

## Production principle

No component is considered complete merely because its isolated smoke test passes.
The full runner is the integration proof that the components operate together as one analytical product.

## Trust boundaries

The line deliberately separates:

- source evidence from model inference;
- trusted canon from review queues;
- world-state from character belief;
- textual order from physical world-time;
- state succession from confirmed transition;
- temporal adjacency from causality;
- hypotheses from canon;
- frozen predictions from future evidence;
- backtesting from prediction creation;
- calibration parameters from immutable source/canon history.

## Final integration checks

The runner requires:

- exactly 61 primary claim files;
- every required stage run artifact through MVP-14B11;
- a readable ALINA quality scorecard;
- all scorecard upstream stages passed;
- maturity state `TRUSTED_ANALYTICAL_FOUNDATION_READY`.

## Thermal policy

The runner retains the proven local thermal policy:

- pause at >= 90 C;
- resume at <= 75 C;
- poll every 10 seconds;
- Ollama timeout 600 seconds;
- retries 3.

## Operational flow

Run:

```powershell
.\RUN_ALINA_BOOK_2_FULL_CANON_PIPELINE.ps1
```

After PASS, publish derived artifacts:

```powershell
.\PUBLISH_ALINA_ANALYSIS_RESULTS.ps1
```

The scorecard may report later analytical layers as waiting for evidence.
That is not an integration failure. For example, zero real predictions or backtests is valid when the trusted evidence is insufficient to promote analyst hypotheses.
