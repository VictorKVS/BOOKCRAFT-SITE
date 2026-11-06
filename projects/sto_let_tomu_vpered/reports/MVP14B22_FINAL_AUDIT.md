# MVP-14B2.2 Smoke Final Audit

## Verdict

Execution: PASS.
Precision: NOT READY FOR FULL RUN.

False positives remain among CANON_ELIGIBLE claims.

## Confirmed false positives

1. `Коля пропал двадцать лет назад`
   - incorrectly CANON_ELIGIBLE;
   - this is part of Kolya's imagined Rip Van Winkle scenario, not story-world fact.

2. `Коля встретил уборщика`
   - incorrectly CANON_ELIGIBLE;
   - source quote only says he saw a strange creature "то ли рыцарь-лилипут, то ли пылесос на ножках";
   - "уборщик" is not established by the evidence.

3. `Коля имеет друга по имени Фима`
   - still over-interpreted from classmate/visit context;
   - relationship should not be promoted without explicit support.

## Root cause

The narrative guard receives only the claim and the short evidence quote.
It does not receive surrounding source context.

Therefore it cannot reliably distinguish:
- narrator fact;
- imagined scenario;
- quoted/embedded fiction;
- character inference;
- narrator description;
- model-added identity labels.

## Required fix

Add a final Canon Precision Gate using:
- claim;
- exact evidence quote;
- surrounding source paragraphs;
- entailment result;
- narrative-mode result.

Only explicit, context-valid claims become FINAL_CANON_CANDIDATE.
