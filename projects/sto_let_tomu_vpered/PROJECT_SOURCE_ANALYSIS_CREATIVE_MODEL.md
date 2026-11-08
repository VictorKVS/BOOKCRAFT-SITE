# ALINA PROJECT / SOURCE / ANALYSIS / CREATIVE PRODUCT MODEL

## 1. Core hierarchy

SITE
-> PROJECT REGISTRY
-> PROJECT
   -> SOURCE SET
   -> SOURCE INDEX
   -> KNOWLEDGE BASE
   -> ANALYSIS PROFILES / RUNS
   -> CREATIVE PRODUCTS

A project is long-lived.
An analysis run is NOT a project.
A creative output is NOT a project.

## 2. Project identity

Every project has two names:

- short_code: human-friendly conditional ID, e.g. A1, A2, A56
- title: full title, e.g. "Алиса Селезнёва"

Example:
A1 — Алиса Селезнёва

Project fields:
- project_id: immutable system UUID/PRJ-...
- short_code: A1
- title: Алиса Селезнёва
- status
- privacy
- created_at
- updated_at
- active_source_set_id
- active_kb_version
- active_analysis_profile
- creative_products[]

## 3. Source Set

The project contains a versioned SOURCE SET.

Example A1:
SOURCE SET v1
- Bulychev_Kir_Ves_Kir_Bulychev_v_odnom_tome....fb2
- edition371535.pdf

A source is registered once:
- source_id
- filename
- sha256
- size
- format
- provenance
- copyright/access status
- ingest state

SOURCE SET fingerprint:
hash(sorted(source.sha256))

If fingerprint is unchanged:
- do NOT repeat file ingestion
- do NOT repeat structural parsing
- reuse chunks
- reuse source evidence
- reuse entity candidates
- reuse embeddings where compatible

## 4. Knowledge Base layers

KB is layered and versioned.

KB_SOURCE
- raw source registry
- work boundaries
- chapters/sections
- chunks
- evidence spans

KB_CANON
- works
- characters
- locations
- events
- relations
- technologies
- organizations
- timeline anchors
- world rules

KB_ANALYTICAL
- contradictions
- hypotheses
- causal links
- open threads
- state transitions
- forecasts
- confidence
- review queue

KB_CREATIVE
- author intent
- story branches
- scene plans
- character visual bible
- locations visual bible
- shot plans
- prompt packs

## 5. Reuse / recomputation policy

Two independent fingerprints:

SOURCE_FINGERPRINT = hash(source files)
ANALYSIS_FINGERPRINT = hash(analysis parameters + model + extractor version)

Rules:

A. Sources unchanged + parameters unchanged
-> reuse everything
-> NO analysis run

B. Sources unchanged + new analysis parameters
-> reuse SOURCE/CHUNK/EVIDENCE foundation
-> rerun only dependent analytical stages

C. One new book/source added
-> ingest only new source
-> update entity resolution / timeline / contradictions incrementally
-> do not reread unchanged sources unless dependency requires it

D. Model changed
-> retain source/chunks
-> rerun only model-dependent extraction/evaluation layers

E. Creative parameters changed
-> do not rebuild canonical KB
-> rerun creative pipeline only

## 6. Analysis profiles

Examples:

PROFILE: CANON_FULL
- characters
- events
- relations
- chronology
- locations
- technologies
- world rules
- contradictions
- open threads
- causal links
- forecast

PROFILE: CHARACTER_DEEP
- psychology
- goals
- knowledge
- behavior
- relationships
- evolution

PROFILE: WORLD_TECH
- technology
- economy
- transport
- institutions
- constraints
- continuity

PROFILE: COMIC_PREP
- sceneability
- visual states
- character appearance
- props
- locations
- action beats
- camera opportunities

PROFILE: FILM_PREP
- scene duration
- shot logic
- camera
- blocking
- dialogue
- sound
- VFX
- transitions

## 7. Project Registry UI

PROJECTS

A1 | Алиса Селезнёва
Sources: 2
Works: 52
KB: v4
Analysis: CANON_FULL v3
Products: 3
Status: READY

[Open] [Sources] [KB] [Runs] [Products] [Delete]

A2 | Сотник — альтернативное продолжение
...

## 8. Project workspace tabs

OVERVIEW
SOURCES
WORKS
KNOWLEDGE BASE
GRAPH
TIMELINE
CONTRADICTIONS
ANALYSIS RUNS
FORECAST
CREATIVE STUDIO
EXPORT

## 9. Creative Studio

CREATIVE STUDIO works on top of the verified KB.

Modes:
- BOOK / CONTINUATION
- COMIC
- VISUAL NOVEL
- SHORT VIDEO
- FILM / SERIES
- GAME SCENARIO

## 10. Comic pipeline

CANON KB
+ AUTHOR INTENT
+ STYLE PROFILE
+ VISUAL BIBLE
-> STORY ARC
-> CHAPTER / EPISODE
-> SCENES
-> PANELS
-> SHOT / CAMERA
-> CHARACTER STATE
-> LOCATION STATE
-> DIALOGUE / CAPTION
-> IMAGE PROMPT
-> NEGATIVE PROMPT
-> RAG CONTEXT PACK
-> GENERATION
-> CONTINUITY CHECK
-> PAGE LAYOUT

Each panel stores:
- panel_id
- scene_id
- event_id
- characters
- pose
- gaze
- emotion
- action
- interaction
- costume
- props
- location
- camera
- shot size
- angle
- composition
- lighting
- continuity_before
- continuity_after
- prompt
- negative_prompt
- rag_context_refs
- generated_asset refs

## 11. Short video / film pipeline

CANON KB
-> STORY
-> SCRIPT
-> SCENES
-> SHOT LIST
-> STORYBOARD
-> KEYFRAMES
-> VIDEO PROMPTS
-> VOICE / DIALOGUE
-> MUSIC / SFX
-> VFX
-> EDIT PLAN
-> CONTINUITY QC
-> EXPORT PACKAGE

This allows the same project to generate:
- 30 sec ad
- 1–3 min YouTube short
- 5–15 min short film
- episode
- feature-length script

## 12. RAG for generation

RAG packages are product-specific.

CHARACTER_RAG
- appearance
- clothing
- age/state
- mannerisms
- relations
- prior visual refs

SCENE_RAG
- current world state
- location
- time
- weather/light
- active events
- props
- continuity

CANON_RAG
- source evidence
- verified facts
- contradictions
- forbidden deviations

STYLE_RAG
- selected high-level visual/literary traits
- palette/composition vocabulary
- prohibited direct living-artist imitation rules where applicable

## 13. Prompt compiler

PROMPT = EVENT + CHARACTER_STATE + LOCATION_STATE + CAMERA + STYLE + CONTINUITY + RAG

The prompt compiler does not invent canon.
It converts structured scene state into generation prompts.

## 14. Product versioning

Example:

A1 / Алиса Селезнёва
KB v4

PRODUCT C1 — Comic "Сто лет тому вперёд"
- source KB: v4
- creative profile: COMIC_PREP v2
- storyboard v5
- prompt pack v8
- assets v3

PRODUCT V1 — YouTube short "Москва будущего"
- source KB: v4
- creative profile: FILM_PREP v1
- script v3
- shots v4

A new creative product does not force source re-analysis.

## 15. Core invariants

NO PROJECT -> NO SOURCES
NO SOURCES -> NO KB
UNCHANGED SOURCES -> REUSE SOURCE FOUNDATION
NEW PARAMETERS -> RERUN ONLY DEPENDENT STAGES
CANON KB != CREATIVE KB
CREATIVE OUTPUT NEVER MUTATES CANON
EVERY GENERATED ASSET MUST TRACE BACK TO SCENE + KB + PROMPT + RAG CONTEXT
