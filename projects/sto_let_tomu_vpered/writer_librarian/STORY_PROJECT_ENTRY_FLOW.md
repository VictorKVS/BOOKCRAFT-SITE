# STORY PROJECT ENTRY FLOW

## Purpose

The Story / Legacy mode starts with project intent and source acquisition, not with an empty dashboard.

The first user experience must answer:

1. What are we writing?
2. What source material already exists?
3. What external knowledge should be researched?
4. What world/model must be reconstructed?
5. What continuation or new story should be generated?

## Entry Wizard

### STEP 1 — What are we writing?

User selects one:

- CONTINUE_EXISTING_SERIES
- CONTINUE_SINGLE_BOOK
- NEW_STORY_IN_EXISTING_WORLD
- NEW_ORIGINAL_WORLD
- GAME_SCENARIO
- ALTERNATE_HISTORY
- ADAPTATION / REWORK

Required fields:

- project_title
- short_intent
- target_format
- desired_length
- user_constraints
- desired_tone
- must_keep
- must_avoid

### STEP 2 — Source Corpus

User can:

- upload books
- upload series
- upload notes
- upload own drafts
- attach canon documents
- add links/references
- select previously indexed corpus

Each source gets:

- source_id
- title
- author
- source_type
- edition/version
- provenance
- checksum
- copyright/access status
- ingest_status

### STEP 3 — Research Scope

User chooses what ALINA/LIBRARIAN should research.

Examples:

- historical period
- geography
- politics
- military organization
- economy
- agriculture
- technology
- religion
- social structure
- medicine
- professions
- language/register
- folklore
- legal customs
- architecture
- transport
- climate
- real historical figures/events

Output:

RESEARCH_REQUEST
-> LIBRARIAN
-> SOURCE REGISTRY
-> VERIFIED KNOWLEDGE PACKAGE

### STEP 4 — Build the World

Only after corpus + research are available:

CORPUS
+ VERIFIED RESEARCH
-> CANON MODEL
-> HISTORY MODEL
-> AUTHORIAL ASSUMPTIONS
-> WORLD STATE
-> CHARACTERS
-> RELATIONSHIPS
-> FACTIONS
-> INNOVATIONS
-> OPEN THREADS

The UI shows progress and confidence for every layer.

### STEP 5 — World Review

Before continuation starts, user sees:

- World Map
- Timeline
- Character Profiles
- Faction / Power Map
- Open Threads
- Innovation / Technology Map
- Historical Pressure
- Canon vs History vs Assumption
- Uncertain / Review items

User may correct or lock important facts.

### STEP 6 — Continuation Goal

User specifies:

- continue from exact point
- desired number of books/chapters
- mandatory future events
- forbidden events
- characters that must survive/die/change
- themes
- pace
- romance/intimacy level
- historical constraints
- desired degree of divergence from canon/history

This is stored in AUTHOR_INTENT and never silently promoted to source canon.

### STEP 7 — Story Simulation

Engine generates candidate futures:

CURRENT_WORLD
+ CHARACTER_MODELS
+ FACTIONS
+ HISTORY
+ OPEN_THREADS
+ INNOVATIONS
+ AUTHOR_INTENT
-> STORY SIMULATOR

Output:
- 3–10 branches
- causal chain
- risks
- character consistency
- historical plausibility
- affected open threads
- 1 / 5 / 10 scene consequences

### STEP 8 — Author Chooses / Combines

User can:

- select one branch
- combine branches
- reject branches
- ask for darker/lighter/slower/faster options
- preserve specific lines
- lock an outcome

### STEP 9 — Book Plan

Chosen branch becomes:

BOOK ARC
-> ACTS
-> CHAPTERS
-> SCENES
-> DIALOGUE / ACTION
-> STYLE PASS
-> VALIDATION

### STEP 10 — Continuous Update

After each generated/accepted chapter:

- world state updates
- character state updates
- relationships update
- factions update
- open threads update
- innovation effects update
- future branches recalculate

## Home screen concept

[ NEW STORY PROJECT ]

1. What are we writing?
2. Upload / select source corpus
3. Define research scope
4. Build world
5. Review world
6. Define continuation goal
7. Simulate branches
8. Start writing

## Principle

NO WORLD GENERATION BEFORE SOURCE ACQUISITION.
NO CONTINUATION BEFORE WORLD REVIEW.
NO NEW CHAPTER WITHOUT STATE UPDATE.
