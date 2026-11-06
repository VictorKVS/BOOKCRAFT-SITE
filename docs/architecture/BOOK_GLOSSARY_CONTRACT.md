# ALINA BOOK 2 — Book Glossary & Concept Dictionary

## Purpose

The glossary is a stable semantic layer shared by Analyst, Writer, Comic Producer and Visual Prompt Builder.

It prevents terminology drift across a long book, series or generated continuation.

## Entry schema

```json
{
  "term_id": "miellophone",
  "term": "миелофон",
  "aliases": [],
  "category": "DEVICE",
  "source_definition": "",
  "agent_definition": "",
  "facts": [],
  "evidence": [],
  "relations": [],
  "confidence": "CONFIRMED",
  "provenance": "SOURCE_CANON",
  "ambiguities": []
}
```

## Definition rule

`source_definition` answers: what does this book establish?

`agent_definition` is a compact normalized definition used by agents.

External encyclopedia/web knowledge, if later added, must live in a separate field and never overwrite source definition.

## Extraction sources

Terms are collected from:
- named technologies/devices;
- organizations/institutions;
- locations;
- professions;
- scientific concepts;
- species/creatures;
- transport;
- time-travel concepts;
- recurring social/world concepts;
- explicit world rules.

## Uses

The glossary is consumed by:
- character/world analysis;
- Writer prompts;
- semantic guard;
- contradiction checker;
- comic captions/dialogue;
- image prompt builder;
- educational/reference UI.
