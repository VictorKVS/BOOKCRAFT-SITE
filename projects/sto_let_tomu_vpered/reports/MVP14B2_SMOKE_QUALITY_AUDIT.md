# MVP-14B2 Smoke Quality Audit

## Verdict

Execution: PASS.
Claim-level architecture: major improvement.
Semantic acceptance: CONDITIONAL.

Do NOT run the full 61-chunk pass yet.

## Improvements confirmed

- analysis is restricted to the primary work;
- local mentions are preserved instead of global merge-by-name;
- SOURCE_CANON / DERIVED / HYPOTHESIS are separated;
- literal quote existence is checked;
- absolute paragraph ranges are attached;
- unsupported quotes are blocked;
- terms are extracted in the same pass.

## Remaining defects

### 1. Quote existence is not claim entailment

Current validator proves only that the quote occurs in the chunk.

It does not prove that the quote supports the claim.

Examples from primary-0001:
- claim: "Коля имеет модель фрегата"; quote only says Fima learned about the frigate.
- claim: "Коля имеет старинный кремнёвый пистолет"; quote says Kolya took a pistol from the wall, not that he owns it.
- claim: "Николай Николаевич болеет сердечным приступом"; attached quote is about Kolya waking up and a note for kefir.

Required patch:
add a semantic Evidence Critic that evaluates CLAIM + QUOTE and returns SUPPORTED / PARTIAL / NOT_SUPPORTED.

### 2. Subject/object role errors

The extractor confuses possession, access, observation and action.

Example:
- taking an object from a wall != owning it.

Required patch:
prefer predicates such as:
- observes
- uses
- takes
- knows_about
- located_at
- owns
only when explicitly supported.

### 3. Event participants schema drift

Some participants are serialized as strings like:
`"{'name': 'Коля'}"`

Required patch:
normalize participant objects and strings to canonical local mention surfaces.

### 4. Term category violations

Examples:
- "фрегат" classified as SPECIES;
- "Рип Ван Винкль" classified as CHARACTER even though CHARACTER is not a glossary category in the current contract.

Required patch:
validate term categories against the allowed enum; invalid categories become OTHER and receive a validation finding.

### 5. Quote matching is too brittle

Several plausible source quotes were marked UNSUPPORTED because punctuation/spacing or exact wording differed.

Required patch:
retain exact-match as hard proof, but add normalized/fuzzy candidate detection for REVIEW only. Never auto-promote fuzzy evidence to SOURCE_CANON.

## Next gate

Before the full 61-chunk run:
1. add evidence entailment critic;
2. add schema normalization;
3. rerun 3-chunk smoke;
4. compare support precision;
5. only then launch full analysis.
