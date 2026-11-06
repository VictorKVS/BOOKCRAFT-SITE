# ALINA BOOK 2 — Critic Layer v2

## Mission

Critics are independent evaluators. They do not write the primary draft and do not own canon.

Their job is to detect defects with explicit evidence and return actionable repair instructions.

## Critic set

### Continuity Critic
Checks:
- chronology;
- location;
- object possession;
- injuries/recovery;
- knowledge acquisition;
- branch contamination;
- unresolved continuity flags.

### Canon Critic
Checks:
- locked canon;
- world rules;
- identity;
- established facts;
- forbidden retcons.

### Character Logic Critic
Checks:
- goals;
- motives;
- emotional state;
- prior decisions;
- knowledge limits;
- voice consistency.

### Plot Critic
Checks:
- scene purpose;
- causal progression;
- setup/payoff;
- thread movement;
- stakes;
- reversals;
- redundancy.

### Pacing Critic
Checks:
- scene length;
- information density;
- conflict rhythm;
- repeated beats;
- dead zones;
- escalation.

### Genre Critic
Uses active genre profiles.

Examples:
- detective: clue fairness, suspect logic, reveal timing;
- thriller: pressure and deadline;
- science fiction: rule/technology consistency;
- drama: emotional causality;
- series fiction: local/global arc balance.

### Style Critic
Checks:
- POV;
- tense;
- tone;
- register;
- verbosity;
- repetition;
- forbidden stylistic drift.

Style cannot override canon.

## Unified critic output

```json
{
  "critic_id": "continuity",
  "decision": "PASS | CONDITIONAL | REPAIR | REPLAN | REJECT",
  "severity": "INFO | MINOR | MAJOR | CRITICAL",
  "failures": [
    {
      "code": "KNOWLEDGE_BEFORE_ACQUISITION",
      "location": "scene-014",
      "description": "...",
      "evidence": ["fact-22", "event-91"],
      "repair_instruction": "..."
    }
  ],
  "warnings": [],
  "score": 0.0
}
```

## Decision precedence

```text
CRITICAL CANON / CONTINUITY
    >
USER LOCKS
    >
CHARACTER LOGIC
    >
PLOT / PACING
    >
GENRE
    >
STYLE
```

## Gate aggregation

Final scene decision:

- any CRITICAL failure -> REJECT or REPLAN;
- MAJOR canon/continuity -> REPAIR/REPLAN;
- only MINOR defects -> CONDITIONAL or REPAIR;
- no blocking defects -> PASS.

## Evidence principle

Critics must reference structured state or exact scene fragments where possible.

No critic may return only "I don't like it".
