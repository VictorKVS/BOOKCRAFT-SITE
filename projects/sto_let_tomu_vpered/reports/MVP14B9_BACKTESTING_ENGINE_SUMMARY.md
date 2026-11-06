# MVP-14B9 Backtesting Engine

- Predictions input: 0
- Future trusted claims available: 0
- Predictions evaluated: 0
- Confirmed: 0
- Refuted: 0
- Mixed: 0
- Pending: 0
- Status: NO_FUTURE_EVIDENCE_YET

## Leakage policy
- Claims at or before the prediction cutoff are excluded from evaluation.
- Only trusted canon claims after cutoff may confirm/refute a frozen prediction.
- Absence of future evidence never counts as refutation.
- Unfrozen predictions are not evaluated.

## Regression tests
- Cutoff leakage guard: PASS
- Confirmation detection: PASS
- Explicit refutation detection: PASS
- No-evidence pending guard: PASS