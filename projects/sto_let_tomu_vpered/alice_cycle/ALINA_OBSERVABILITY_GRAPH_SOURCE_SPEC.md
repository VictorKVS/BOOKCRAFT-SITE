# ALINA OBSERVABILITY, GRAPH LAB & SOURCE CENTER

## 1. Observability / trace

Every project run must emit structured events.

Trace event:
- timestamp
- run_id
- project_id
- stage
- agent/module
- action
- input_ref
- output_ref
- status: QUEUED/RUNNING/PASS/WARN/FAIL/REVIEW
- progress_current
- progress_total
- duration_ms
- error_code
- error_message
- parent_trace_id
- trace_id

UI must expose:
- active module
- queue
- elapsed time
- warnings/errors
- stage progress
- live trace stream
- filter INFO/DEBUG/WARN/ERROR
- links from trace output to produced KB object

No silent work.

## 2. Run manifest

At the end:
- sources processed
- works detected/matched/review
- chapters/segments
- claims
- entities
- events
- relations
- timeline anchors
- contradictions
- review queue
- failed tasks
- versions of parsers/models/rules

## 3. Graph Lab

Nodes:
WORK, CHAPTER, CHARACTER, EVENT, LOCATION, TECHNOLOGY, ORGANIZATION, RELATION, CLAIM, SOURCE, TIME_ANCHOR, HYPOTHESIS.

Every trusted edge must point to provenance.

Capabilities:
- filter node/edge types
- ego graph
- shortest path
- path explanation
- show only conflicts
- show only one work
- compare two works
- chronology overlay
- confidence threshold
- click node -> inspector -> evidence
- click edge -> why this relation exists

## 4. Source Center

Source classes:
- CANON_SOURCE
- PRIMARY_REFERENCE
- SECONDARY_REFERENCE
- WEB_RESEARCH
- FAN_RECONSTRUCTION
- GENERATED_HYPOTHESIS

Important:
WEB_RESEARCH never becomes CANON_SOURCE automatically.

Source record:
- source_id
- title
- author/org
- URL/file ref
- source class
- authority tier
- publication date
- edition/version
- access date
- checksum
- rights/access status
- downloadable
- parser status
- extracted claims
- linked works/entities
- verification status

## 5. Automated research

When EXTERNAL RESEARCH is explicitly enabled:

SEARCH -> OPEN/READ -> EXTRACT -> CROSS-CHECK -> CLASSIFY -> REVIEW -> ADD TO KB

The research agent may:
- search websites
- read accessible pages
- follow relevant links
- collect metadata
- compare sources
- create evidence packages
- monitor source freshness later

It must not:
- silently promote web claims to canon
- bypass paywalls/access controls
- download copyrighted full texts without permission
- expose private project content in search queries unless explicitly allowed

## 6. Download/read policy

Download full source only when:
- user provided it, or
- public domain, or
- source explicitly permits download, or
- user has authorized/legal access through a connected source.

Otherwise:
- save citation/metadata/link
- read allowed excerpts/pages
- store derived evidence within permitted limits.

## 7. Private project boundary

Project content remains local by default.
External research queries should be minimized and sanitized.
GitHub stores platform code/schemas, not private corpus or private KB.
