# MVP-14B2 — Claim-Level Canon Analyzer

MVP-14B2 replaces the unsafe MVP-14B aggregation contract.

## Input

Only the primary work:
- paragraphs 0..3976;
- 61 chunks from `primary_work_chunk_index.json`.

## Core changes

- no `merge_by_name()`;
- every character/object/location occurrence is a local mention;
- source facts are claim records;
- every SOURCE_CANON claim must include a verbatim quote;
- code verifies that the quote actually exists in the chunk;
- verified quotes receive absolute paragraph ranges;
- unsupported SOURCE_CANON claims are marked `UNSUPPORTED`;
- DERIVED and HYPOTHESIS remain explicitly separate;
- terminology is extracted in the same pass for the project glossary.

## Output

- `evidence/chunk_claims_v2/*.json`
- `state/literary_claims_raw_v2.json`
- `runs/mvp14b2_claim_level_canon.json`
- `reports/MVP14B2_CLAIM_LEVEL_SUMMARY.md`

MVP-14B2 still does NOT create final global entities. That is the responsibility of MVP-14C.
