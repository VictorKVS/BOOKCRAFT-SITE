# MVP-14A.1 — Structural Boundary Detection

The original ingest detected numbered chapters but lost DOCX paragraph style metadata.

That allowed a long tail of additional material to be absorbed into the final detected chapter.

The patched ingest now preserves paragraph styles and writes:

- `structure/chapters.json`
- `structure/structure_candidates.json`
- `structure/chunk_index.json`

Structure candidates are short paragraphs that look like headings because of:
- DOCX heading/title style;
- PART / BOOK / STORY patterns;
- uppercase title-like text.

This stage does not automatically cut the source. It produces evidence for a later WORK/PART boundary resolver.

Acceptance rule:
an oversized chapter or unresolved work boundary blocks final canon reconciliation.
