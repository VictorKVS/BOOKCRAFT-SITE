# ALINA DOWNSTREAM RESEARCH EXECUTION POLICY v1

## Purpose
Research tasks after Text Analysis Factory must be executable and must never use TASK_EXECUTOR_NOT_CONNECTED as a normal project state.

## Executor classes

### DETERMINISTIC_DERIVATION
Uses only trusted Text Analysis artifacts and deterministic transformations.
Can PASS when its contract is fully satisfied.

### EVIDENCE_REGISTRY
Uses extracted objects plus exact evidence verification.
Can PASS only when configured evidence thresholds are met.

### SEMANTIC_REVIEW
Produces a useful structured candidate output from Text Analysis artifacts, but does not claim trusted canon.
Default status is REVIEW until a dedicated semantic executor or human gate confirms it.

## Task mapping

R05 narrative-mode classification -> SEMANTIC_REVIEW
R06 canon admission -> DETERMINISTIC_DERIVATION over R04 + R05
R08 character identity resolution -> DETERMINISTIC_DERIVATION
R09 character profile -> SEMANTIC_REVIEW
R10 goals and motives -> SEMANTIC_REVIEW
R11 knowledge model -> SEMANTIC_REVIEW
R12 state evolution -> SEMANTIC_REVIEW
R13 relationship graph -> EVIDENCE_REGISTRY
R15 event ordering -> DETERMINISTIC_DERIVATION
R16 temporal model -> EVIDENCE_REGISTRY
R18 movement/travel -> SEMANTIC_REVIEW
R19 world rules -> SEMANTIC_REVIEW
R21 technology capability -> SEMANTIC_REVIEW
R23 objects/artifacts -> SEMANTIC_REVIEW
R24 causal links -> SEMANTIC_REVIEW
R25 contradiction analysis -> DETERMINISTIC_DERIVATION where explicit conflicts exist, otherwise REVIEW
R26 open threads -> EVIDENCE_REGISTRY
R27 themes -> SEMANTIC_REVIEW
R28 sceneability -> DETERMINISTIC_DERIVATION from trusted events/locations/entities
R29 forecast inputs -> DETERMINISTIC_DERIVATION from unresolved threads and trusted states, default REVIEW if state evidence is incomplete

## Rule
A SEMANTIC_REVIEW task is an implemented executor. REVIEW means "candidate analytical output exists but is not yet trusted", not "missing code".
