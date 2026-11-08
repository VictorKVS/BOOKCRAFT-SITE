# ALINA DEEP ANALYSIS ENGINE

## Purpose

The foundation ingest is NOT semantic analysis.

Foundation:
- files
- sections/headings
- catalog matching
- structural claims
- structural objects

Deep analysis:
FULL TEXT -> CHUNKS -> LLM EXTRACTION -> EVIDENCE -> ENTITY RESOLUTION -> EVENTS -> RELATIONS -> TIMELINE -> TECHNOLOGY/WORLD -> CONTRADICTIONS -> GRAPH -> FORECAST INPUT

## Provider policy

Default provider is LOCAL.
No book text is sent to GitHub.

Supported first:
1. Ollama local API: http://127.0.0.1:11434
2. OpenAI-compatible local endpoint configured by environment variables.

If no local model is available, Deep Run must stop with NEEDS_MODEL, not silently fake results.

## Chunk contract

Every chunk:
- chunk_id
- source_id
- work_id if known
- section/chapter
- ordinal
- char_start/char_end
- text_sha256
- local text file reference

Extracted objects always carry:
- chunk_id
- evidence quote/span offsets
- confidence
- extractor/model version

## Per-chunk extraction schema

characters[]
- name
- aliases
- roles
- observed_traits
- knowledge
- goals
- emotions
- actions
- evidence

events[]
- event
- participants
- location
- time_expression
- causes
- consequences
- evidence

relations[]
- source
- target
- relation_type
- state/change
- evidence

locations[]
technologies[]
organizations[]
time_anchors[]
claims[]
open_threads[]

## Progress

Live status must expose:
- file N/M
- work N/M
- chunk N/TOTAL
- current chapter/section
- current chars
- model/provider
- tokens/chars processed
- entities/events found
- warnings/errors
- ETA only if measured from actual throughput, otherwise omit

## Quality gates

NO MODEL -> NO DEEP ANALYSIS
NO EVIDENCE -> NO TRUSTED OBJECT
NO CHUNK TRACE -> NO PASS
NO ENTITY RESOLUTION -> NO FINAL CHARACTER COUNT
NO TEMPORAL/CANON PASS -> NO FORECAST
