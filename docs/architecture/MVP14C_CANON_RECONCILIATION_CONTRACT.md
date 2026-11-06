# MVP-14C — Canon Reconciliation Contract

## Purpose

Convert noisy per-chunk extraction into an evidence-grounded canon graph.

## Hard rules

1. Surface name is never an entity ID.
2. Two mentions with the same name may represent different characters.
3. Two mentions with different spellings may represent the same character.
4. Every SOURCE_CANON claim must have claim-level source evidence.
5. Inference is labeled DERIVED; uncertainty is labeled HYPOTHESIS.
6. Work boundaries are resolved before cross-chunk merging.
7. Knowledge is time-indexed.
8. Cultural embodiments never overwrite literary facts.

## Core records

### Mention
```json
{
  "mention_id": "m-...",
  "chunk_id": "chunk-...",
  "surface": "Коля",
  "context": "...",
  "candidate_entity_ids": []
}
```

### Entity
```json
{
  "entity_id": "char-...",
  "canonical_name": "",
  "aliases": [],
  "entity_type": "CHARACTER",
  "work_id": "",
  "claims": []
}
```

### Claim
```json
{
  "claim_id": "c-...",
  "subject_id": "",
  "predicate": "",
  "value": "",
  "provenance": "SOURCE_CANON",
  "confidence": "CONFIRMED",
  "evidence": []
}
```

### Evidence
```json
{
  "chunk_id": "",
  "paragraph_start": null,
  "paragraph_end": null,
  "quote": ""
}
```

## Resolution gates

- ENTITY_UNRESOLVED
- ENTITY_RESOLVED
- CLAIM_UNSUPPORTED
- CLAIM_SUPPORTED
- CONTRADICTION_OPEN
- CONTRADICTION_RESOLVED
- CANON_READY

No creative generation may consume records marked unresolved/unsupported unless explicitly allowed as hypothesis.
