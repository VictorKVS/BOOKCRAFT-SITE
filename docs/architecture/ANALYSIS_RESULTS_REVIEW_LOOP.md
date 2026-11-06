# ALINA BOOK 2 — Publishing Analysis Results

## Purpose

ALINA analysis is not considered reviewable until its derived artifacts are published to GitHub.

This allows an external reviewer/architect to inspect the actual machine outputs rather than relying only on terminal PASS messages.

## Publishable artifacts

For each project, publish:

- `source_manifest.json`
- `structure/`
- `state/`
- `reports/`
- `runs/`
- `evidence/chunk_analysis/`

## Never publish

- source DOCX/PDF/EPUB files;
- full extracted source text;
- local source chunks containing the complete book;
- model weights;
- secrets.

These remain under `projects/*/sources/` and are ignored by Git.

## Required workflow

```text
RUN ANALYSIS
→ PHYSICAL PASS
→ PUBLISH DERIVED RESULTS
→ GITHUB REVIEW
→ ALGORITHM AUDIT
→ PATCH ALGORITHM
→ REGRESSION RUN
```

A PASS proves execution. GitHub review proves whether the algorithm produced useful, consistent, source-grounded results.

## Review loop

The reviewer should inspect:
- duplicate entities / alias resolution failures;
- hallucinated or unsupported facts;
- weak definitions;
- contradictory world rules;
- event granularity;
- evidence quality;
- terminology drift;
- knowledge-state errors;
- timeline errors;
- missing relations.

Findings must be converted into algorithm changes and regression tests.
