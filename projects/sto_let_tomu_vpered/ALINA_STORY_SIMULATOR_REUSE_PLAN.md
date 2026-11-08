# ALINA STORY SIMULATOR REUSE PLAN

## Decision

Use the already parsed ALINA / "Сто лет тому вперёд" corpus as the first integration bed for the new Story Project / Legacy Continuation architecture.

Do not rebuild ingest, evidence, canon, entities, events, state, transitions, graph or benchmark layers from scratch.

## Existing foundation to reuse

- source/work chunks
- evidence / claim extraction
- canon admission / canon store
- entity registry
- relation / event store
- knowledge graph
- contradiction engine
- temporal model
- state engine
- transitions / causal layer
- hypothesis / prediction layers
- historical forecast benchmark / backtesting
- evaluation scorecard

## New layers to add

1. WORLD MODEL
2. FACTION / POWER MODEL
3. OPEN THREAD GRAPH
4. INNOVATION & DIFFUSION MODEL
5. CHARACTER COGNITIVE PROFILE
6. RELATIONSHIP / INTIMACY STATE
7. AUTHOR INTENT
8. STORY COMPOSITION ENGINE
9. BRANCH SIMULATOR
10. STYLE / LEXICON PASS
11. GAME NARRATIVE EXPORT (later)

## Integration order

### Phase A — World reconstruction
Existing canon + state + graph
-> world objects
-> rules
-> resources
-> locations
-> institutions
-> technologies
-> social constraints

### Phase B — Open threads
Detect unresolved:
- promises
- conflicts
- goals
- missing outcomes
- latent threats
- unused assets
- pending relationships
- unfinished technical ideas

### Phase C — Character cognition
For each major character:
- demonstrated knowledge
- decision patterns
- motives
- constraints
- blind spots
- learning over time

### Phase D — Story simulation
CURRENT STATE
+ CHARACTER MODELS
+ OPEN THREADS
+ WORLD RULES
+ AUTHOR INTENT
-> candidate branches

### Phase E — Backtest
Hide known future chapters/segments.
Freeze branch predictions.
Reveal future.
Score:
- event
- character action
- motive
- relationship
- world consequence
- open thread continuation
- surprise miss
- canon violation
- leakage

## Acceptance

Only after ALINA demonstrates that the new layers work on the already parsed corpus do we instantiate the same contracts for SOTNIK LAB.

## Migration principle

ALINA = reference implementation.
SOTNIK = second benchmark / complex historical-world benchmark.

No project-specific logic may be hard-coded into the shared engines.
