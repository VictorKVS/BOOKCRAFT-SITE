# MVP-14B2.1 Evidence Critic Audit

## Verdict

The entailment critic is useful, but not sufficient for canon acceptance.

Observed smoke result:
- checked: 26
- supported entailed: 10
- partial: 3
- rejected: 13

## Critical remaining issue: narrative mode

A claim may be correctly entailed by a quote while still NOT being a fact of the story world.

Examples:

### Imagined future treated as fact
Claim:
`Коля пропал двадцать лет назад`

The quote contains this sentence, but it occurs inside Kolya's imagined Rip Van Winkle scenario.

Correct classification:
- CHARACTER_THOUGHT / HYPOTHETICAL_SCENARIO
- not SOURCE_CANON world fact.

### Description overinterpreted as identity
Claim:
`Коля встретил уборщика`

The quote only says he saw a strange creature "то ли рыцарь-лилипут, то ли пылесос на ножках".

The critic accepted the claim even though "уборщик" is not established by the quote.

### Relationship overreach
Claim:
`Коля имеет друга по имени Фима`

The quote establishes that Fima is from Kolya's class and asks to visit; friendship is plausible but not explicit in that evidence.

## Required additional layer

```text
QUOTE EXISTS
→ CLAIM-QUOTE ENTAILMENT
→ NARRATIVE / EPISTEMIC MODE
→ CANON ELIGIBILITY
```

Narrative modes:
- NARRATOR_FACT
- CHARACTER_SPEECH
- CHARACTER_THOUGHT
- CHARACTER_BELIEF
- HYPOTHETICAL_SCENARIO
- DREAM
- ANALOGY
- FICTION_WITHIN_FICTION
- UNKNOWN

Only evidence judged as actual story-world assertion may become canon.

## Decision

Do not run all 61 chunks yet.
Add MVP-14B2.2 Narrative Mode Guard and rerun the same 3-chunk smoke.
