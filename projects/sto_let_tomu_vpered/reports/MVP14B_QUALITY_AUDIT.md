# MVP-14B Quality Audit — Sto let tomu vpered

## Verdict

Execution status: PASS.
Semantic quality status: CONDITIONAL / REQUIRES ALGORITHM PATCH.

The raw extraction is useful, but it is not safe for canon acceptance.

## Major findings

### 1. Work / structure boundary failure

The detected chapter list contains 39 items. Chapter 39, "24. Прощай, супергерла!", spans paragraphs 3884..5062 — 1179 paragraphs. Most prior chapters are roughly 40–190 paragraphs.

This is a structural anomaly and strongly indicates that the current chapter detector swallowed additional tail material into the last chapter.

Observed downstream symptom: late chunk evidence contains characters and concepts unrelated to the primary "Сто лет тому вперёд" plot, including Посейдон, профессор Комуру and ашиклеки.

Required patch:
- add structural anomaly detection;
- flag oversized chapters;
- add WORK/PART/BOOK boundary detection before semantic extraction;
- never merge semantic state across unresolved work boundaries.

### 2. Entity collision by surface name

Current `merge_by_name()` merges records by case-folded display name.

This is unsafe.

The source itself contains the chapter title "У нас в классе три Коли", proving that "Коля" is not a unique entity key.

Observed downstream symptom: one merged "Коля" accumulates mutually incompatible age, origin, profession, biography and knowledge facts.

Required patch:
- never use display name as entity identity;
- create provisional mention IDs per chunk/scene;
- resolve identity using context, aliases, relations, chronology and explicit full-name evidence;
- allow same surface name to map to multiple entity IDs.

### 3. Alias/translation duplication

Examples:
- Djavat / Джавад;
- Pavel / Павел / Старик Павел;
- Alice / Alica / Алиса;
- Nikolai Nikolaevich / Николай Николаевич.

Required patch:
- canonical language for source entities: source language (Russian here);
- transliteration/translation variants become aliases, not separate entities;
- normalize Unicode and common model misspellings before candidate matching.

### 4. Evidence is not claim-level

Current schema stores a list of facts and a separate list of evidence.

This allows unsupported mapping.

Examples found:
- world rule about the number of mielophones is paired with an unrelated quote about a sick animal;
- location/object facts are sometimes paired with generic scene text;
- some English paraphrases are placed in evidence instead of source snippets.

Required patch:
Every claim must be represented as:

```json
{
  "claim": "...",
  "provenance": "SOURCE_CANON|DERIVED|HYPOTHESIS",
  "confidence": "CONFIRMED|PROBABLE|POSSIBLE",
  "evidence": [
    {"chunk_id":"...", "quote":"...", "paragraph_start":0, "paragraph_end":0}
  ]
}
```

A SOURCE_CANON claim without source evidence must be rejected.

### 5. Observation vs inference leakage

Examples:
- "In the Soviet era, people could keep secrets and have private spaces." is not a world rule established by the text;
- traits such as "Healthy", "Curious", "Presumptuous" may be inferred without explicit support;
- some causal links are invented from temporal adjacency.

Required patch:
- SOURCE_FACT: explicit;
- DERIVED: justified inference;
- HYPOTHESIS: uncertain interpretation;
- no inferred world rule may enter SOURCE_CANON.

### 6. Knowledge-state contamination

Current extraction aggregates character knowledge across chunks without time/state boundaries.

This loses the distinction:
```text
WHAT IS TRUE
≠ WHAT CHARACTER KNOWS NOW
≠ WHAT CHARACTER LEARNS LATER
```

Required patch:
Store knowledge events with:
- entity_id;
- proposition;
- learned_at_event;
- valid_from;
- evidence;
- confidence.

### 7. Language instability

Raw records mix Russian, English, transliteration and malformed mixed-script tokens (e.g. mieloфон, Aлиса/Alica).

Required patch:
- source-language normalization layer;
- preserve original quote;
- normalized canonical value in Russian;
- aliases retain transliterations only for matching.

## Positive findings

The pipeline already demonstrates:
- complete 79-chunk execution;
- resumability/reuse;
- per-chunk evidence files;
- thermal control;
- useful extraction of recurring objects/events/locations;
- enough raw material to build a robust reconciliation layer.

Therefore the correct response is not to discard MVP-14B, but to introduce a stricter semantic contract before final canonization.

## Required algorithm sequence

```text
SOURCE
→ STRUCTURE AUDIT
→ WORK/PART BOUNDARY DETECTION
→ SCENE/CHUNK MENTIONS
→ CLAIM-LEVEL EVIDENCE
→ PROVISIONAL ENTITY IDs
→ ENTITY RESOLUTION
→ ALIAS NORMALIZATION
→ EVENT/TIMELINE
→ KNOWLEDGE STATE
→ GLOSSARY
→ CULTURAL EMBODIMENTS
→ CONTRADICTION CHECK
→ CANON ACCEPTANCE
```

## Acceptance decision

MVP-14B execution: PASS.
MVP-14B semantic quality: CONDITIONAL.
Final canon acceptance: BLOCKED until MVP-14C resolves the findings above.
