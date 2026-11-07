# MVP-15 ALINA Evaluation & Prediction Benchmark

## Baseline conclusion

- Production pipeline integration: PASS
- Historical cutoff leakage audit: PASS
- Fact/world-model layers: evaluable
- Reasoning layer: not yet forecast-ready
- Forecasting quality: NOT SCORABLE
- Reason: no real predictions were frozen at historical cutoffs.

## Evaluation windows

| Known | Hidden future | Known claims | Future claims | Known events | Future events | Frozen predictions | Leakage |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1-10 | 11-20 | 12 | 16 | 2 | 4 | 0 | PASS |
| 1-20 | 21-30 | 28 | 15 | 6 | 3 | 0 | PASS |
| 1-30 | 31-40 | 43 | 17 | 9 | 4 | 0 | PASS |
| 1-40 | 41-50 | 60 | 15 | 13 | 4 | 0 | PASS |
| 1-50 | 51-61 | 75 | 20 | 17 | 2 | 0 | PASS |

## Interpretation

This is a baseline evaluation, not a success claim.
The current system has demonstrated trusted extraction and world-model construction.
It has NOT yet demonstrated real forecasting because the current hypothesis engine produced no promoted analyst hypotheses and therefore no historical frozen predictions.

The next engineering target is to improve hypothesis generation without weakening canon safety, then freeze predictions at each cutoff and rerun this benchmark.