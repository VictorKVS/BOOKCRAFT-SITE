# ALINA TEXT ANALYSIS FACTORY v1

## Role
The Text Analysis Factory is the mandatory production engine between Verified Corpus and the Research Complex.

It reads one verified/scoped work at a time and produces a versioned TEXT_ANALYSIS_PACKAGE.

Research tasks R05-R30 consume this package and its evidence-backed derivatives. They do not independently re-read or reinterpret the raw source unless their contract explicitly requires it.

## Pipeline

VERIFIED CORPUS
-> WORK SCOPE
-> CHUNKS
-> SEMANTIC EXTRACTION
-> EVIDENCE VERIFICATION
-> TRUSTED REGISTRIES
-> WEIGHTED GRAPH
-> TEXT_ANALYSIS_PACKAGE
-> RESEARCH COMPLEX
-> CONTINUITY

## Factory stages

TA01 SCOPE
- work/source identity
- exact work boundary
- source fingerprint

TA02 CHUNK
- deterministic chunking
- chunk hashes
- resumable checkpoint

TA03 EXTRACT
- claims
- characters
- events
- relations
- locations
- technologies
- organizations
- time anchors
- open threads

TA04 EVIDENCE
- exact/near/rejected evidence verification
- evidence coverage

TA05 REGISTRIES
- evidence-gated character/entity/event/location/technology/organization stores

TA06 GRAPH
- evidence-weighted nodes and edges

TA07 PACKAGE
- immutable/versioned summary for downstream consumers

## Output

research/<work_id>/text_analysis/text_analysis_package.json

Required fields:
- schema_version
- factory_id
- work_id
- source_fingerprint
- analysis_fingerprint
- status
- stage_statuses
- boundary
- model
- metrics
- artifacts
- quality
- blockers
- created_at
- updated_at

## Status
NOT_STARTED
RUNNING
EXTRACTED
EVIDENCE_REVIEW
TRUSTED
FAILED

## Quality rule
TEXT_ANALYSIS_PACKAGE is TRUSTED only if evidence verification and required registries meet their quality gates.

R03 PASS means semantic extraction finished. It does NOT mean the text analysis factory is TRUSTED.

## Research mapping
R01/R02 prepare the work scope.
R03 executes TA03.
R04 executes TA04.
R07/R14/R17/R20/R22 populate TA05.
The factory package is refreshed after each of these tasks.

R05-R30 may consume the package according to their dependencies.

## Product rule
The Dashboard must expose Text Analysis Factory as its own pipeline stage.
