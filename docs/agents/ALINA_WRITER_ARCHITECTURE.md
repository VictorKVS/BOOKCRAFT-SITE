# ALINA WRITER — Creative Story Agent

## Purpose

ALINA WRITER is a dedicated creative agent. It is intentionally separated from ALINA Analyst.

- **ALINA Analyst** understands the source, builds the world model, extracts canon, events, characters, relations, beliefs, motives and evidence.
- **ALINA WRITER** consumes that structured state and creates or transforms fiction.

The writer must not silently rewrite canon unless the selected mode explicitly allows it.

## Core modes

### CONTINUE
Continue the story while preserving:
- canon;
- character state;
- timeline;
- unresolved threads;
- tone/style constraints;
- world rules;
- point of view;
- scene continuity.

### ALTER
Change an existing story under explicit constraints.

Examples:
- change one event;
- change one character decision;
- change genre or tone;
- create an alternate branch;
- rewrite from another point of view;
- repair weak scenes without changing canon.

### SERIES
Transform one story/world into a multi-book or multi-episode series.

Outputs:
- series premise;
- season/book arcs;
- character arcs;
- escalation model;
- recurring conflicts;
- continuity rules;
- future hooks;
- per-book objectives;
- canon registry.

## Architecture

```text
SOURCE STORY
   ↓
ALINA ANALYST
   ↓
NARRATIVE STATE / CANON
   ↓
WRITER MODE ROUTER
   ├── CONTINUE
   ├── ALTER
   └── SERIES
   ↓
STORY PLANNER
   ↓
SCENE PLANNER
   ↓
DRAFT WRITER
   ↓
CONTINUITY CRITIC
   ↓
STYLE CRITIC
   ↓
CANON CHECK
   ↓
REPAIR LOOP
   ↓
FINAL DRAFT
```

## Narrative state consumed by Writer

```text
WORLD
CHARACTERS
CHARACTER_STATES
RELATIONS
EVENTS
TIMELINE
LOCATIONS
OBJECTS
RULES
SECRETS
BELIEFS
KNOWLEDGE_PER_CHARACTER
CONFLICTS
PLOT_THREADS
UNRESOLVED_HOOKS
STYLE_PROFILE
POV
TONE
FORBIDDEN_CHANGES
```

## Writer sub-agents / roles

### 1. Story Planner
Creates macro-structure, beats and target state transitions.

### 2. Scene Planner
Turns beats into scenes:
- participants;
- location;
- objective;
- conflict;
- reveal;
- emotional turn;
- state changes;
- exit condition.

### 3. Draft Writer
Produces prose only after receiving the scene contract.

### 4. Dialogue Specialist
Optional specialist for:
- character voice;
- subtext;
- conflict;
- speech continuity.

### 5. Continuity Critic
Checks:
- chronology;
- injuries;
- possessions;
- location;
- knowledge state;
- promises;
- secrets;
- unresolved threads.

### 6. Canon Critic
Checks whether the draft violates locked world facts.

### 7. Style Critic
Checks style constraints without being authoritative over canon.

### 8. Repair Agent
Receives explicit failures and rewrites only the failing parts where possible.

## Principle: truth and creativity are separated

```text
ALINA ANALYST = truth / state / evidence
ALINA WRITER  = artistic form / invention within allowed space
```

The Writer can invent only where:
- canon is silent;
- the mode permits divergence;
- a new branch is explicitly created.

## Output contract

Every generated scene should return both:

1. prose;
2. state delta.

Example state delta:

```json
{
  "scene_id": "S-014",
  "new_events": ["E-221"],
  "character_state_changes": {
    "anna": {"trust_ivan": -0.2}
  },
  "new_clues": ["C-031"],
  "resolved_threads": [],
  "opened_threads": ["T-019"],
  "canon_changes": []
}
```

This allows the next scene to continue from machine-readable state rather than rereading the entire book.

## Series mode

```text
ORIGINAL STORY / WORLD
   ↓
SERIES BIBLE
   ↓
LONG ARC
   ↓
BOOK / EPISODE ARCS
   ↓
CHARACTER ARC MATRIX
   ↓
THREAD SCHEDULER
   ↓
BOOK N PLANNER
   ↓
SCENE GENERATION
   ↓
CONTINUITY CHECK
```

The series bible should include:
- immutable world rules;
- mutable world state;
- character biographies;
- relationships;
- secrets;
- chronology;
- factions;
- technology/magic rules;
- locations;
- terminology;
- style;
- forbidden contradictions.

## Future model strategy

ALINA WRITER is not tied permanently to one LLM.

Candidate brains are evaluated by role-specific creative benchmarks:
- instruction following;
- continuity;
- character voice;
- scene coherence;
- style;
- long-context consistency;
- repair ability.

The current creative winner may change, while the Writer agent, canon, tests and skill pack remain stable.
