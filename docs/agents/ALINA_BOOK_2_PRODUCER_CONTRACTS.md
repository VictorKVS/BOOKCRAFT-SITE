# ALINA BOOK 2 — Producer Contracts

## Input contract

Producer accepts:

```yaml
mode:
source_story:
user_brief:
target_format:
target_length:
genre:
audience:
must_keep:
must_change:
must_avoid:
canon_lock:
creative_freedom:
```

## Producer → Analyst

Request:
- source decomposition;
- canon extraction;
- timeline;
- unresolved plot threads;
- character states;
- knowledge/belief states;
- contradictions;
- world rules.

Analyst returns structured state and evidence.

## Producer → Writer

Writer receives a scene contract, never only "write the next chapter".

```yaml
scene_id:
objective:
pov:
location:
time:
participants:
entry_state:
conflict:
required_events:
forbidden_events:
reveal_limit:
style:
target_length:
exit_state:
```

## Writer → Producer

```json
{
  "prose": "...",
  "state_delta": {},
  "new_threads": [],
  "resolved_threads": [],
  "canon_change_requests": [],
  "writer_notes": []
}
```

## Critic → Producer

```json
{
  "decision": "PASS | CONDITIONAL | REPAIR | REPLAN | REJECT",
  "failures": [],
  "warnings": [],
  "repair_targets": [],
  "evidence": []
}
```

## Producer state

Producer maintains:

- current project version;
- accepted scene versions;
- rejected drafts;
- open issues;
- arc progress;
- unresolved setups;
- pending payoffs;
- continuity status;
- canon version.

## Release condition

A book/episode may be marked release-ready only if:

- all required scenes are accepted;
- no critical canon conflicts remain;
- required setups/payoffs are closed or intentionally deferred;
- character arc targets are met;
- continuity gate passes;
- user-locked constraints are satisfied.
