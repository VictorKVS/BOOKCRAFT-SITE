# ALINA PROJECT COMMAND CENTER v1

## Product goal
The first screen after opening a project is a decision surface, not a data dump.

Within 5–10 seconds the user must know:
1. What project/corpus is this?
2. Is the corpus trustworthy enough to continue?
3. What is running now?
4. What is blocked/review?
5. What changed since last session?
6. What is the next recommended action?
7. Can I export a report that contains exactly the same state?

## Single source of truth
PROJECT COMMAND CENTER reads only normalized project state and derived dashboard state.

UI cards, alerts and reports must not maintain independent counters.

Source chain:
project files -> project_state.json -> command_center.json -> UI/report

## Dashboard hierarchy

### A. Executive header
- project code/title
- project status
- corpus gate
- research gate
- overall health
- last update
- one primary next action

### B. KPI row
- sources
- corpus objects identified / expected
- corpus verified
- research ready
- research tasks PASS / REVIEW / FAILED
- products

### C. Production pipeline
SOURCE -> CORPUS VERIFY -> TEXT COMPARE -> RESEARCH -> CONTINUITY -> FORECAST -> CREATIVE

Each stage:
- status
- progress
- blocker count
- current object
- click target

### D. Attention queue
Only problems that require action:
- BLOCKED
- REVIEW
- FAILED
- stale source/KB
- unresolved authority/version/completeness
- model/transport failures

Each item:
- severity
- object
- reason
- owner/actor
- recommended action
- drilldown target

### E. Current operation
- active module
- current work/object
- task
- progress
- duration
- checkpoint
- retry/resume state

### F. Trust & evidence
- source authority coverage
- version coverage
- completeness coverage
- evidence coverage
- unresolved count
- benchmark/reference availability

### G. Recent activity
- last project events
- last runs
- last errors
- last verified changes

## Health model
GREEN READY
YELLOW REVIEW
RED BLOCKED/FAILED
BLUE RUNNING
GRAY NOT_STARTED

Health is derived, never manually set.

## Next-action engine
Priority:
1. fatal/blocking incident
2. recoverable failed active run
3. corpus verification blocker
4. human review blocker
5. runnable automated research
6. continuity
7. forecast/creative

The dashboard should expose one primary action and optional secondary actions.

## Report contract
Report is generated from the same command_center snapshot.

Sections:
1. Executive summary
2. Project identity
3. Source set
4. Corpus verification
5. Research progress
6. Current blockers/review
7. Model/runtime state
8. Evidence and trust
9. Chronology/version discrepancies
10. Recent activity
11. Recommended next actions
12. Technical appendix

Formats:
- JSON machine report
- HTML human report
- later: PDF

## UX rule
Every red/yellow metric must be clickable and explain:
- why
- affected object
- evidence
- recommended action

No unexplained status words.
