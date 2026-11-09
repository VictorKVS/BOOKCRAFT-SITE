# ALINA RESEARCH COMPLEX — WORK-LEVEL TASK CATALOG v1

## Purpose

For every literary work, ALINA creates a research program before deep semantic processing.

The research program is a controlled set of up to 30 tasks. Each task has:
- stable task_id
- name
- research question
- status
- dependencies
- inputs
- outputs
- evidence requirements
- metrics
- progress
- run history
- blockers
- quality gate

The program is visible in the project dashboard and is not the same thing as an analysis run.

## Work research service file

For each work:

```
projects/<project>/research/<work_id>/research_program.json
```

Required top-level fields:

```json
{
  "schema_version": "1.0",
  "project_id": "A1",
  "work_id": "ALICE-005",
  "work_title": "Сто лет тому вперёд",
  "program_status": "PLANNED",
  "created_at": "",
  "updated_at": "",
  "source_set_version": 1,
  "source_fingerprint": "",
  "research_profile": "LITERARY_FULL_V1",
  "task_limit": 30,
  "summary": {
    "total": 30,
    "planned": 30,
    "running": 0,
    "pass": 0,
    "review": 0,
    "blocked": 0,
    "failed": 0
  },
  "tasks": []
}
```

## Task statuses

```
PLANNED
READY
RUNNING
PASS
REVIEW
BLOCKED
FAILED
REUSED
SKIPPED
```

## First 30 research tasks

### R01 — Source integrity
Confirm exact work boundary, source identity, checksum, title variants and source provenance.

### R02 — Structural map
Chapters, sections, narrative blocks, scene boundaries and text order.

### R03 — Claim extraction
Extract atomic factual claims with evidence references.

### R04 — Evidence verification
Check that each accepted claim is directly supported by source evidence.

### R05 — Narrative-mode classification
Separate narrator fact, character belief, speech, memory, dream, hypothesis and uncertainty.

### R06 — Canon admission
Decide which verified claims enter trusted canon and which remain review/conflict.

### R07 — Entity registry
Identify and resolve characters, organizations, creatures, objects and other named entities.

### R08 — Character identity resolution
Merge aliases and distinguish namesakes/ambiguous references.

### R09 — Character profile
Role, age/state, occupation, abilities, possessions and stable properties supported by evidence.

### R10 — Character goals and motives
Goals, intentions, fears, incentives and explicit/implicit motives with confidence.

### R11 — Character knowledge model
What each character knows, believes, does not know, learns and misinterprets.

### R12 — Character state evolution
Track physical, emotional, social and informational state changes through the work.

### R13 — Relationship graph
Family, friendship, conflict, authority, cooperation, acquaintance and changing relations.

### R14 — Event extraction
Identify meaningful events with actors, objects, location, time anchors and evidence.

### R15 — Event ordering
Establish reliable textual and narrative order of events.

### R16 — Temporal model
Dates, durations, relative anchors, age clues, past/future references and uncertainty.

### R17 — Location registry
Places, environments, travel points and spatial relationships.

### R18 — Movement and travel
Who moves where, by what means, duration, route and continuity constraints.

### R19 — World rules
Physical, social, institutional and fictional rules that govern the world.

### R20 — Technology registry
Devices, transport, medicine, communications, AI/robots and other technologies.

### R21 — Technology capability model
For each technology: capabilities, limits, dependencies, users, evidence and contradictions.

### R22 — Organizations and institutions
Schools, government bodies, police, research organizations, services and social institutions.

### R23 — Objects and artifacts
Important objects, ownership, state, transfers, use and continuity.

### R24 — Causal links
Separate explicit causal statements from mere temporal adjacency.

### R25 — Contradiction analysis
Internal contradictions, inconsistent facts, aliases, chronology conflicts and source anomalies.

### R26 — Open threads and unresolved questions
Mysteries, unfinished arcs, unexplained facts and unresolved character/world questions.

### R27 — Themes and narrative functions
Themes, conflicts, stakes, dramatic functions and recurring motifs; kept separate from canon facts.

### R28 — Sceneability / visual analysis
For each significant scene: participants, poses/actions, interactions, location, props, visual state and continuity.

### R29 — Forecast inputs
Identify only evidence-backed unresolved states suitable for later hypotheses/predictions.

### R30 — Work research quality gate
Aggregate completeness, evidence coverage, conflicts, review queue, blockers and readiness for cross-work cycle analysis.

## Core task record

```json
{
  "task_id": "R14",
  "name": "Event extraction",
  "status": "PLANNED",
  "progress": 0,
  "depends_on": ["R03", "R04", "R07"],
  "goal": "Extract trusted events from the work",
  "inputs": [],
  "outputs": [],
  "evidence_required": true,
  "metrics": {
    "items_found": 0,
    "items_accepted": 0,
    "items_review": 0,
    "evidence_coverage": 0.0
  },
  "last_run_id": null,
  "started_at": null,
  "finished_at": null,
  "duration_ms": null,
  "blockers": [],
  "quality_gate": "NOT_CHECKED"
}
```

## Dashboard

Project -> Work -> Research Program

The dashboard must show:
- overall % completion
- 30 task cards
- current task
- task dependencies
- PASS / REVIEW / BLOCKED / FAILED counts
- evidence coverage
- accepted/rejected object counts
- contradictions
- unresolved items
- last run
- elapsed time
- source and analysis fingerprints
- whether result was REUSED or recomputed

Opening a task must show:
- purpose
- input
- execution history
- trace
- metrics
- output files
- evidence
- review items
- blockers
- quality gate

## Execution rule

ALINA must not mark the work as RESEARCH_READY until R30 passes.

Cross-work cycle analysis may consume only trusted outputs from work-level programs.

Creative Studio may read trusted canon plus explicitly selected analytical/creative layers, but must never mutate canon.
