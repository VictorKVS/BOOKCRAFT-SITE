# ALINA KNOWLEDGE WORKSPACE

After analysis, ALINA must not return only a completion message. The project opens a working knowledge-base workspace.

## 1. Run report

Show what ALINA actually did:
- accepted sources
- identified works
- chapter/segment split
- evidence extraction
- entity extraction
- event extraction
- timeline build
- relationship graph
- technology/world extraction
- contradiction scan
- review queue

Every stage has:
status, item_count, errors, warnings, parser/model version, start/end timestamps.

## 2. Project KPIs

- sources
- works
- chapters
- evidence claims
- characters
- events
- locations
- technologies
- relations
- contradictions
- unresolved/review items

No invented numbers. UI receives them from the run manifest.

## 3. Working tabs

Overview
Works
Characters
Events
Timeline
World
Technology
Relations
Contradictions
Evidence
Review Queue

## 4. Every KB object is inspectable

Minimum object contract:
- object_id
- object_type
- canonical_name
- aliases
- description
- confidence
- status
- provenance[]
- relations[]
- conflicts[]
- first_seen
- last_seen
- revision_history[]

## 5. Provenance

User must be able to move:
KB OBJECT -> CLAIM -> SOURCE WORK -> CHAPTER/SEGMENT -> SOURCE FRAGMENT

No trusted object without provenance.

## 6. Human actions

User may:
- CONFIRM
- EDIT
- MARK DISPUTED
- MERGE DUPLICATES
- SPLIT ENTITY
- REJECT
- LOCK AS CANON
- ADD NOTE

Every action creates revision history. Never rewrite source evidence.

## 7. Search/filter

Search all KB objects.
Filters:
- object type
- work
- status
- confidence
- conflict presence
- review required
- first/last appearance

## 8. Private mode

All project KB data stays local by default.
Repository contains application code and generic schemas only.
