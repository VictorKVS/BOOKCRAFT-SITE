# ALINA AUTO CORPUS INGEST

## Goal

Turn uploaded literary files into a structured, evidence-linked corpus automatically.

The pipeline must reproduce the manual reference workflow already demonstrated on the Alice cycle.

## Pipeline

SOURCE FILE
-> FORMAT DETECTOR
-> STRUCTURE PARSER
-> WORK SPLITTER
-> METADATA EXTRACTOR
-> TITLE / EDITION RESOLVER
-> MANIFEST MATCHER
-> CHAPTER / SEGMENT INDEXER
-> SOURCE HASH / PROVENANCE
-> CORPUS BUILDER
-> REVIEW QUEUE

## Modules

### 1. FORMAT DETECTOR

Input:
- file path / source reference

Output:
- file type
- parser route
- encoding
- parse confidence

Supported first:
- FB2
- PDF
- TXT
- EPUB
- DOCX

### 2. STRUCTURE PARSER

Extract:
- top-level sections
- nested sections
- headings
- chapters
- collection containers
- author/title metadata

Must preserve source hierarchy.

### 3. WORK SPLITTER

Goal:
distinguish true works from:
- collection headings
- cycles
- omnibus containers
- prefaces
- chapter headings
- appendices

Output:
- candidate_work_id
- title
- start/end boundaries
- parent container
- confidence

### 4. TITLE / EDITION RESOLVER

Normalize:
- spelling variants
- ё/е
- punctuation
- alternate titles
- source typos
- edition-specific titles

Never silently overwrite source title.

Store:
- source_title
- normalized_title
- aliases
- conflict_status

### 5. MANIFEST MATCHER

Match candidate work against known catalog.

Signals:
- title similarity
- author
- year
- aliases
- characters
- cycle
- bibliographic metadata

Output:
- matched_work_id
- confidence
- evidence
- unresolved candidates

### 6. CHAPTER / SEGMENT INDEXER

For each matched work:
- chapters
- page/section ranges
- segment IDs
- source anchors

### 7. SOURCE PROVENANCE

Store:
- source filename
- checksum
- edition
- publication data
- user-provided / external source flag
- ingest timestamp
- parser version

### 8. CORPUS BUILDER

Create logical work package:

WORK-ID/
- metadata
- source_index
- chapters
- chunks
- ingest_report

Do not commit copyrighted full text by default.

### 9. REVIEW QUEUE

Anything uncertain goes to review:
- ambiguous title
- conflicting edition
- collection vs work ambiguity
- duplicated work
- missing work
- malformed structure

## Acceptance test: Alice cycle

Manual reference:
- 52-work manifest
- omnibus FB2 matched 51 works
- separate PDF matched ALICE-029
- source metadata conflicts preserved

Automatic run must reproduce:
- total expected works: 52
- detected/matched works
- missing works
- title conflicts
- composite containers
- ALICE-029 resolution

## Output example

{
  "source": "...fb2",
  "cycle": "Алиса Селезнёва",
  "works_detected": 51,
  "works_matched": 49,
  "review_required": 2,
  "missing": 1,
  "conflicts": 2
}

## Gate

AUTO INGEST is not accepted until:
- manual vs auto work count matches
- no collection container is promoted as a work
- source title conflicts are preserved
- provenance exists for every work
- unresolved mappings are not auto-promoted
