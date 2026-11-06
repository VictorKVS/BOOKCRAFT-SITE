# Narrative State Schema v2

## Purpose

Narrative State is the machine-readable shared memory of ALINA BOOK 2.

It is the contract between Analyst, Producer, Writer and Critics.

## Top-level model

```yaml
project_id:
canon_version:
source_version:
world:
characters:
relations:
events:
timeline:
locations:
objects:
rules:
knowledge_states:
belief_states:
secrets:
conflicts:
plot_threads:
setups:
payoffs:
unresolved_questions:
style_profile:
continuity_flags:
evidence:
```

## Character

```yaml
character_id:
names:
aliases:
status:
traits:
goals:
fears:
values:
skills:
resources:
relationships:
current_location:
physical_state:
emotional_state:
knowledge:
beliefs:
suspicions:
secrets_known:
secrets_hidden:
open_promises:
arc_state:
last_confirmed_event:
evidence:
```

## Event

```yaml
event_id:
type:
time:
location:
participants:
preconditions:
action:
outcome:
causes:
consequences:
state_changes:
knowledge_changes:
thread_changes:
certainty:
canon_status:
evidence:
```

## Relation

```yaml
relation_id:
source_entity:
target_entity:
relation_type:
direction:
strength:
state:
valid_from:
valid_to:
certainty:
evidence:
```

## Plot thread

```yaml
thread_id:
title:
type:
opened_at:
participants:
question:
stakes:
setups:
developments:
payoff_target:
status:
priority:
evidence:
```

## Knowledge state

For each relevant fact:

```yaml
fact_id:
ground_truth_status:
reader_status:
characters:
  character_id:
    status: knows | believes | suspects | denies | unknown | lies_about
    confidence:
    learned_at:
    evidence:
```

## Canon status

```text
LOCKED
CONFIRMED
PROVISIONAL
BRANCH_ONLY
RETCON_PENDING
REJECTED
```

## State delta

Every accepted Writer output must generate a delta rather than replacing the whole state.

```json
{
  "new_events": [],
  "character_changes": {},
  "relation_changes": [],
  "knowledge_changes": [],
  "thread_changes": [],
  "canon_change_requests": [],
  "continuity_flags": []
}
```

The Analyst applies the delta, validates it, then emits the next canonical state version.
