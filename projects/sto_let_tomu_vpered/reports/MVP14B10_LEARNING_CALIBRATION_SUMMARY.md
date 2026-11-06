# MVP-14B10 Learning / Calibration Layer

- Hypotheses input: 0
- Predictions input: 0
- Backtests input: 0
- Decisive backtests: 0
- Calibration updates applied: 0
- Prediction support weight: 1.0 -> 1.0

## Learning policy
- Confirmed and refuted backtests may influence future weighting.
- Fewer than 3 decisive observations cannot change the weight.
- Pending and mixed results do not change the weight.
- Weight updates are bounded and deterministic.
- Canon, evidence, and past frozen predictions are never rewritten.

## Safety boundary
- Learning changes future decision parameters only.
- Learning never converts a hypothesis into canon.
- Learning never edits source evidence.