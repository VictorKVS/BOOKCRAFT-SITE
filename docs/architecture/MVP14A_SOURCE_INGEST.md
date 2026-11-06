# MVP-14A — Controlled Source Ingest

Purpose: convert a local DOCX source into deterministic, evidence-bearing analysis inputs before any LLM canon analysis starts.

Pipeline:

```text
LOCAL DOCX
→ SHA256
→ DOCX TEXT EXTRACTION
→ PARAGRAPHS
→ CHAPTER DETECTION
→ ANALYSIS CHUNKS
→ SOURCE MANIFEST
→ STRUCTURE INDEX
→ MVP-14B SEMANTIC CANON ANALYSIS
```

The source binary, extracted full text and chunk text stay local under `projects/*/sources/` and are ignored by Git.

Git-safe artifacts:
- `source_manifest.json`
- `structure/chapters.json`
- `structure/chunk_index.json`
- run/evidence metadata

This stage does not invent canon. It only proves what source was ingested and how it was segmented.
