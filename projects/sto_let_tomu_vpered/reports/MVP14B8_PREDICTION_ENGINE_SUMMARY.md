# MVP-14B8 Prediction Engine

- Open hypotheses input: 0
- Predictions frozen: 0
- Review queue: 0
- Cutoff sequence index: 94
- Future evidence used at prediction creation: NO

## Leakage control
- Every prediction is frozen at a specific trusted textual cutoff.
- Future evidence is forbidden during prediction creation.
- Evaluation starts as NOT_YET_EVALUATED.
- Backtesting must operate only after new source material is admitted through the trusted pipeline.

## Promotion policy
- Predictions are generated only from OPEN analyst hypotheses.
- At least two supporting trusted claims are required.
- MEDIUM/HIGH forecast strength is required.
- Forecast strength is not a calibrated probability.