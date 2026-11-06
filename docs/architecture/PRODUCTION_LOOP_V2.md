# ALINA BOOK 2 — Production Loop v2

## End-to-end cycle

```text
USER / PROJECT BRIEF
        ↓
PRODUCER
        ↓
ANALYST STATE
        ↓
SCENE CONTRACT
        ↓
WRITER
        ↓
DRAFT + STATE DELTA
        ↓
CRITIC LAYER
        ↓
┌───────────────┬───────────────┬───────────────┐
│ PASS          │ REPAIR        │ REPLAN        │
↓               ↓               ↓
ACCEPT      REPAIR AGENT      PRODUCER
│               │               │
└───────→ RE-CHECK ←────────────┘
        ↓
ANALYST VALIDATES DELTA
        ↓
NARRATIVE STATE vN+1
        ↓
PRODUCER ADVANCES PROJECT
        ↓
NEXT SCENE / CHAPTER
```

## Stage contracts

### Stage 1 — Producer
Creates:
- scene objective;
- constraints;
- required events;
- forbidden events;
- expected exit state.

### Stage 2 — Analyst
Provides:
- current canon;
- relevant character states;
- active threads;
- knowledge/belief state;
- continuity constraints.

### Stage 3 — Writer
Returns:
- prose;
- state delta;
- notes;
- canon change requests.

### Stage 4 — Critics
Return independent defect reports.

### Stage 5 — Repair/Replan
Repair local defects or replan structural failures.

### Stage 6 — Analyst validation
Checks proposed state delta.

### Stage 7 — Commit state
If valid:
- scene becomes accepted;
- Narrative State increments;
- Producer moves to next unit.

## Versioning

Every production artifact must be versioned:

```text
project
scene plan
draft
critic report
repair
accepted scene
state delta
narrative state
```

Rejected artifacts remain in evidence history.

## Acceptance rule

A scene is not complete because prose was generated.

A scene is complete only after:

```text
WRITER OUTPUT
+ CRITIC PASS
+ ANALYST STATE VALIDATION
+ PRODUCER ACCEPTANCE
```

## Failure states

```text
WRITER_FAILED
CRITIC_BLOCKED
REPAIR_EXHAUSTED
REPLAN_REQUIRED
STATE_DELTA_INVALID
CANON_CONFLICT
USER_DECISION_REQUIRED
```

Each failure must preserve reason and evidence.

## First MVP target

For MVP, support one scene cycle:

```text
Narrative State
→ Scene Contract
→ Draft
→ Critics
→ Repair
→ State Validation
→ Accepted Scene
```

Only after this works reliably should the system scale to complete chapters and books.
