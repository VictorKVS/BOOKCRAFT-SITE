# ALINA WRITER — Mode Algorithms

## 1. CONTINUE

Input:
- current narrative state;
- last confirmed scene;
- active plot threads;
- target length;
- optional user direction.

Algorithm:

```text
READ STATE
→ SELECT ACTIVE THREADS
→ DETERMINE NEXT NECESSARY STATE CHANGE
→ PLAN BEAT
→ PLAN SCENE
→ WRITE DRAFT
→ CHECK CHARACTER KNOWLEDGE
→ CHECK CANON
→ CHECK CONTINUITY
→ REPAIR
→ EMIT PROSE + STATE DELTA
```

The agent must not reveal a secret to a character who does not know it.

## 2. ALTER

Input:
- source narrative;
- requested change;
- preservation constraints.

Algorithm:

```text
LOCATE CHANGE POINT
→ COMPUTE DEPENDENCIES
→ IDENTIFY AFFECTED FUTURE EVENTS
→ CREATE BRANCH
→ REPLAN DOWNSTREAM EVENTS
→ GENERATE REVISED SCENES
→ CHECK NEW BRANCH CONSISTENCY
```

Two submodes:

- **PATCH** — local rewrite with minimal downstream impact.
- **BRANCH** — alternate timeline with explicit divergence point.

## 3. SERIES

Input:
- story/world/canon;
- desired number of books/episodes;
- genre and escalation target.

Algorithm:

```text
EXTRACT SERIES CORE
→ DEFINE IMMUTABLE CANON
→ DEFINE LONG ARC
→ DEFINE CHARACTER ARC MATRIX
→ DISTRIBUTE REVEALS / CONFLICTS
→ DEFINE BOOK OBJECTIVES
→ DEFINE BOOK END STATES
→ GENERATE BOOK OUTLINES
→ GENERATE SCENES
→ GLOBAL CONTINUITY CHECK
```

### Escalation rule

Each installment must change the world or characters. Repetition without state progression is rejected.

## Scene contract

Before prose, generate an internal scene plan:

```yaml
scene_id:
location:
time:
pov:
participants:
entry_state:
objective:
conflict:
reveal:
emotional_turn:
required_events:
forbidden_events:
exit_state:
```

## Character voice contract

Each major character may have:

```text
lexicon
sentence rhythm
social register
typical evasions
humor
taboo subjects
emotional leakage
knowledge limits
```

## Critic priority

If critics disagree:

```text
CANON / CONTINUITY
    >
USER CONSTRAINTS
    >
SCENE OBJECTIVE
    >
STYLE PREFERENCE
```

A style critic cannot override established facts.
