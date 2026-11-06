# Timeline & Event Graph Contract

## Goal

Preserve chronological and causal consistency.

## Timeline dimensions

ALINA must distinguish:

- story time;
- narration order;
- flashback time;
- remembered time;
- predicted time;
- dream/hallucination time;
- alternate branch time.

## Event graph

```text
EVENT
├── BEFORE / AFTER
├── CAUSES
├── ENABLES
├── PREVENTS
├── REVEALS
├── CHANGES_STATE
└── OPENS / CLOSES THREAD
```

## Temporal certainty

```text
EXACT
BOUNDED
RELATIVE
APPROXIMATE
UNKNOWN
CONFLICTED
```

## Continuity checks

- character cannot be in two incompatible places;
- dead/absent character cannot act unless explicitly justified;
- object possession must propagate;
- injuries and recovery must propagate;
- knowledge cannot appear before acquisition;
- secrets cannot be used by unaware characters;
- causal dependencies must exist before effects;
- branch events must not contaminate mainline canon.
