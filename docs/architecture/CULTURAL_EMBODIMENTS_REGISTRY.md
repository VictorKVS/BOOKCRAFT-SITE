# ALINA BOOK 2 — Cultural Embodiments Registry

## Purpose

Store successful screen, illustration and other culturally recognizable embodiments without confusing them with literary source canon.

## Status values

- LOCKED — selected by user as adaptation reference.
- REFERENCE — useful reference, not authoritative.
- REJECTED — explicitly unsuitable.
- UNREVIEWED — collected but not evaluated.

## Record schema

```json
{
  "embodiment_id": "",
  "character_id": "",
  "work": "",
  "medium": "",
  "version": "",
  "visual_traits": [],
  "behavioural_traits": [],
  "recognizability": null,
  "literary_fidelity": null,
  "adaptation_usefulness": null,
  "status": "UNREVIEWED",
  "provenance": "CULTURAL_REFERENCE",
  "notes": []
}
```

## Merge rule

```text
SOURCE CHARACTER BIBLE
  + selected embodiment(s)
  + user visual lock
  → project visual identity
```

A selected embodiment may guide appearance or performance language, but may not silently alter age, biography, relationships, knowledge state, causality or world rules established by the source.
