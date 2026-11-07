# SOTNIK BENCHMARK PLAN

Status: DESIGN / NO CLAIM OF SUCCESS YET

## Purpose

Use a long multi-book historical/alternate-history series as a benchmark for the Legacy Continuation Mode.

The benchmark evaluates reconstruction and prediction first. It does not treat fluent continuation text as proof of understanding.

## Required input

The benchmark requires a legally available/user-provided corpus of the books to be analyzed.

No source text -> no corpus-specific conclusions.

## Phase 1 — Corpus ingestion

For each book:

- chapter boundaries
- characters
- places
- factions
- dates / temporal anchors
- events
- relationships
- resources
- technologies
- historical references
- explicit beliefs / plans
- unresolved threads

Every extracted item keeps source provenance.

## Phase 2 — World reconstruction

Build four parallel stores:

1. CANON_WORLD
2. HISTORICAL_REFERENCE
3. AUTHORIAL_DEVIATIONS
4. UNCERTAIN / REVIEW

Goal: distinguish real historical constraints from the fictional world's altered state.

## Phase 3 — Hero cognitive model

Recover demonstrated patterns:

- what the hero knows
- what he does not know
- what experience he reuses
- how he reasons by analogy
- how he organizes people
- how he responds to uncertainty
- recurring mistakes
- changing beliefs

Never infer unlimited expertise.

## Phase 4 — Open-thread graph

Extract:

- promises
- unresolved conflicts
- unfinished reforms
- enemies not neutralized
- alliances under pressure
- unused resources
- relationships with unfinished arcs
- foreshadowed risks
- historical events approaching the current date

Each thread gets evidence, strength, dependencies and likely horizon.

## Phase 5 — Historical pressure engine

For each story date:

- known real events near the horizon
- political changes
- wars / alliances
- trade / economic pressures
- seasonal constraints
- logistical constraints

Historical data must be sourced independently of the fiction corpus.

## Phase 6 — Historical backtesting

Walk-forward evaluation:

BOOK 1 -> predict BOOK 2
BOOK 1-2 -> predict BOOK 3
BOOK 1-3 -> predict BOOK 4
...

Before revealing the next book, freeze:

- expected character actions
- expected world changes
- likely open-thread continuations
- likely faction moves
- likely historical interactions

Then compare with the known next book.

## Metrics

- CHARACTER_ACTION_HIT
- MOTIVE_HIT
- WORLD_CONSEQUENCE_HIT
- RELATIONSHIP_HIT
- FACTION_MOVE_HIT
- OPEN_THREAD_HIT
- HISTORICAL_PRESSURE_HIT
- SURPRISE_MISS
- CANON_VIOLATION
- KNOWLEDGE_LEAKAGE

Separate precision / recall / F1 where applicable.

## Phase 7 — Author-boundary comparison

If the series contains continuation material written by other authors, evaluate it separately from the original-author corpus.

Questions:

- Which character patterns remain stable?
- Which world rules remain stable?
- Which open threads continue?
- Which pacing / composition patterns change?
- Which assumptions are newly introduced?

This is comparison, not a claim to recover the deceased author's private unwritten plan.

## Phase 8 — Future branch simulation

Only after backtesting:

CURRENT_CANON
+ WORLD_STATE
+ HISTORY
+ CHARACTER_MODELS
+ FACTIONS
+ OPEN_THREADS
-> 5-10 candidate future branches

Each branch must show:

- cause
- participants
- prerequisites
- consequences
- affected threads
- 1 / 5 / 10 scene horizon
- confidence
- why it fits / where it is speculative

## Acceptance gates

The system is NOT "continuation-ready" unless:

- leakage = 0
- canon violations below threshold
- character prediction beats naive baseline
- open-thread continuation beats naive baseline
- historical-pressure model is independently sourced
- generated branches remain distinguishable from canon
- style pass does not alter world facts or character intent

## Output surfaces for website

- World Map / History Timeline
- Character Cognitive Profile
- Faction Dashboard
- Open Threads Radar
- Story Branch Graph
- Historical Pressure Timeline
- Canon vs History vs Assumption matrix
- Prediction / Backtest dashboard
- Branch comparison view
