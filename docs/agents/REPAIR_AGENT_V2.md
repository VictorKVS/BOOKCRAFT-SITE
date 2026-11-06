# ALINA BOOK 2 — Repair Agent v2

## Mission

Repair Agent fixes explicit defects without unnecessarily rewriting correct content.

```text
DRAFT
+ CRITIC FAILURES
+ CANON
+ SCENE CONTRACT
    ↓
REPAIR AGENT
    ↓
PATCHED DRAFT
+ REPAIR REPORT
```

## Repair strategy

1. classify each defect;
2. identify minimum affected span;
3. preserve accepted material;
4. repair blocking defects first;
5. rerun relevant critics;
6. stop when gates pass or repair budget is exhausted.

## Repair scopes

```text
LINE
PARAGRAPH
DIALOGUE TURN
SCENE BEAT
FULL SCENE
CHAPTER PLAN
ARC PLAN
```

Use the smallest safe scope.

## Non-goals

Repair Agent must not:
- create hidden canon changes;
- change project direction;
- remove a user-locked requirement;
- rewrite entire chapters for a minor style issue.

## Repair report

```json
{
  "repair_id": "R-0014",
  "source_version": "scene-014-v2",
  "target_version": "scene-014-v3",
  "fixed": ["C-01", "C-03"],
  "remaining": [],
  "state_delta_changed": true,
  "canon_change_requests": []
}
```

## Repair budget

Producer controls:
- max repair iterations;
- max rewrite scope;
- when to escalate from REPAIR to REPLAN.
