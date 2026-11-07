# MVP-15.1 Historical Forecast Baseline

This benchmark creates real frozen-at-cutoff deterministic predictions and evaluates them against hidden future trusted data.

## Overall
- Event recurrence predictions: 9
- Event recurrence hits: 6
- Event recurrence precision: 0.6667
- Transition recurrence predictions: 7
- Transition recurrence hits: 3
- Transition recurrence precision: 0.4286

## Windows

| Known | Hidden | Event preds | Event hits | Event precision | Transition preds | Transition hits | Transition precision |
|---|---|---:|---:|---:|---:|---:|---:|
| 1-10 | 11-20 | 1 | 1 | 1.0 | 0 | 0 | None |
| 1-20 | 21-30 | 2 | 1 | 0.5 | 1 | 1 | 1.0 |
| 1-30 | 31-40 | 2 | 1 | 0.5 | 2 | 1 | 0.5 |
| 1-40 | 41-50 | 2 | 2 | 1.0 | 2 | 1 | 0.5 |
| 1-50 | 51-61 | 2 | 1 | 0.5 | 2 | 0 | 0.0 |

## Interpretation
- This is the first scoreable no-leakage forecasting baseline.
- A HIT means the predicted actor/entity really reappeared in the hidden future window.
- A FALSE_POSITIVE means the recurrence was predicted but did not occur in that hidden window.
- These numbers are a baseline for later Hypothesis Engine improvements; they are not evidence that narrative understanding is solved.