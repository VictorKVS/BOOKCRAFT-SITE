# Canon Registry Contract

## Purpose

The Canon Registry stores facts that define what is true in the current story branch.

Canon is versioned.

## Canon record

```yaml
canon_id:
statement:
type:
scope:
status:
valid_from:
valid_to:
source:
source_fragment:
confidence:
locked_by_user:
branch:
supersedes:
conflicts_with:
notes:
```

## Rules

1. User-locked canon cannot be silently changed.
2. Writer proposals that conflict with canon become change requests.
3. Producer can approve a retcon only explicitly.
4. Branch timelines keep separate canon namespaces.
5. Deleted or superseded canon remains in history.
6. Canon without evidence is marked provisional unless directly specified by the user.

## Conflict classes

```text
HARD_CONTRADICTION
SOFT_TENSION
TEMPORAL_CONFLICT
IDENTITY_CONFLICT
WORLD_RULE_CONFLICT
KNOWLEDGE_STATE_CONFLICT
STYLE_ONLY
```

Only the first five are canon-level conflicts.
