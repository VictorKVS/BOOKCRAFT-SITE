# ALINA BOOK 2 — Analysis Projects Architecture

## Purpose

ALINA BOOK 2 is expected to process many independent books, series and research corpora.

A **project** is the isolation boundary for one analysis target.

Examples:
- one novel;
- one multi-volume novel;
- one book series;
- one author's universe;
- one comparison study across several works.

## Project hierarchy

```text
projects/
└── <project_id>/
    ├── project.json
    ├── sources/
    ├── structure/
    ├── state/
    ├── graph/
    ├── evidence/
    ├── reports/
    ├── branches/
    └── runs/
```

## Core project files

### project.json
Identity, type, source inventory, status, language, model profile and processing settings.

### sources/
Original source files or source manifests.

### structure/
Detected volumes, parts, chapters and scenes.

### state/
Current and historical Narrative State snapshots.

### graph/
Character, event, relation, knowledge, object, location and plot-thread graph exports.

### evidence/
Source-grounding and acceptance evidence.

### reports/
Human-readable analysis outputs.

### branches/
Alternative canon / continuation branches.

### runs/
Machine execution history.

## Project types

```text
SINGLE_BOOK
MULTI_VOLUME_BOOK
BOOK_SERIES
UNIVERSE
COMPARATIVE_STUDY
```

## Project lifecycle

```text
CREATED
→ SOURCES_ADDED
→ STRUCTURE_DETECTED
→ INGESTING
→ MERGING
→ VALIDATING
→ READY
→ EXTENDING
→ ARCHIVED
```

## Isolation principle

No project may silently read or write another project's state.

Cross-project comparison is allowed only through an explicit comparative project.
