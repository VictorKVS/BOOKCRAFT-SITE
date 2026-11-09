# ALINA CYCLE CONTINUITY ENGINE v1

## Purpose

The Continuity Engine operates only on work-level research programs that passed R30.

It does not overwrite source facts.
It compares trusted outputs across works and builds a cross-work continuity model.

## Core principle

AUTHOR TEXT != PERFECT CANON DATABASE

ALINA must preserve:
1. SOURCE FACT
2. WORK CANON
3. CROSS-WORK CANON
4. CONFLICT / VARIANT / RETCON
5. ALINA BEST-FIT RECONSTRUCTION

## Input gate

A work may enter the cycle engine only when:

- research_program.status = RESEARCH_READY
- R30.status = PASS
- source_fingerprint is known
- evidence coverage is above the configured minimum
- unresolved blocking source-boundary problems = 0

## Cross-work tasks

C01 — Work admission
Validate that each work is ready for cycle-level comparison.

C02 — Entity merge
Resolve identities and aliases across works.

C03 — Character biography continuity
Compare age, profession, family, abilities, known history.

C04 — Character knowledge continuity
Track what each character knows and when they learned it.

C05 — Character state continuity
Compare physical/social/emotional/informational state across works.

C06 — Relationship continuity
Compare family, friendship, conflict, authority and cooperation links.

C07 — Global event merge
Build a cross-work event registry.

C08 — Chronology reconstruction
Compare publication order, explicit dates, relative anchors and inferred order.

C09 — Age consistency
Check ages against chronology and biography.

C10 — Location continuity
Compare locations, addresses, spatial relations and existence constraints.

C11 — Travel continuity
Compare routes, durations and movement feasibility.

C12 — Technology continuity
Compare appearance, capability, limitation and availability of technologies.

C13 — Object continuity
Track important objects, ownership, destruction, transfer and reappearance.

C14 — Organization continuity
Compare institutions, roles, structures and authority.

C15 — World-rule continuity
Compare physical/social/world rules across works.

C16 — Terminology continuity
Track renamed concepts, aliases and source variants.

C17 — Internal contradiction aggregation
Lift work-level contradictions into cycle-level context.

C18 — Cross-work contradiction detection
Detect incompatible trusted facts between different works.

C19 — Retcon candidate detection
Identify later claims that may intentionally supersede earlier canon.

C20 — Author memory drift candidate detection
Identify likely continuity drift without claiming author intent.

C21 — Source edition variant detection
Separate textual/edition differences from story-world contradictions.

C22 — Contradiction classification
Classify each case:
- CONTRADICTION
- CONTINUITY_ERROR
- RETCON_CANDIDATE
- SOURCE_VARIANT
- TEMPORAL_AMBIGUITY
- ENTITY_AMBIGUITY
- POSSIBLE_EXPLANATION
- UNRESOLVED

C23 — Explanation generation
Generate bounded explanations without silently choosing one.

C24 — Evidence comparison matrix
Store all competing evidence side by side.

C25 — Canon stability scoring
Score stable facts by independent support across works.

C26 — Best-fit chronology
Build ALINA reconstructed chronology with uncertainty.

C27 — Best-fit world model
Build a non-destructive analytical world reconstruction.

C28 — Continuity impact analysis
Show which conflicts affect downstream creative products and forecasts.

C29 — Human review queue
Escalate unresolved high-impact contradictions.

C30 — Cycle continuity quality gate
Decide whether the cycle is ready for forecast/creative use.

## Conflict record

{
  "conflict_id": "CC-0001",
  "type": "AGE_CONFLICT",
  "classification": "UNRESOLVED",
  "entities": ["CHAR-ALICE"],
  "claims": [
    {
      "work_id": "ALICE-001",
      "claim_id": "...",
      "value": "10",
      "evidence_ref": "..."
    },
    {
      "work_id": "ALICE-014",
      "claim_id": "...",
      "value": "12",
      "evidence_ref": "..."
    }
  ],
  "possible_explanations": [
    "TIME_GAP",
    "SOURCE_VARIANT",
    "RETCON_CANDIDATE",
    "AUTHOR_MEMORY_DRIFT_CANDIDATE"
  ],
  "selected_resolution": null,
  "resolution_mode": "NONE",
  "impact": {
    "chronology": "HIGH",
    "creative": "MEDIUM",
    "forecast": "HIGH"
  },
  "status": "REVIEW"
}

## Important language rule

ALINA must never state:
"the author forgot"

unless supported by an external explicit author statement.

Allowed:
"Later text conflicts with an earlier established state. Intentional retcon is not confirmed."

Internal classification may use:
AUTHOR_MEMORY_DRIFT_CANDIDATE

but UI text should say:
POSSIBLE CONTINUITY DRIFT

## Canon modes for downstream products

STRICT_SOURCE
- preserve source-specific inconsistencies

BEST_FIT_CANON
- use ALINA reconstructed continuity model

LATE_SOURCE_PRIORITY
- later source wins when explicitly configured

CUSTOM_CANON
- human selects conflict resolutions

## Output files

cycle_research/
  continuity_program.json
  entity_merge.json
  biography_continuity.json
  knowledge_continuity.json
  relationship_continuity.json
  event_registry.json
  chronology_candidates.json
  reconstructed_chronology.json
  technology_continuity.json
  world_rule_continuity.json
  conflicts.json
  retcon_candidates.json
  continuity_drift_candidates.json
  evidence_matrix.json
  canon_stability.json
  best_fit_world.json
  review_queue.json
  continuity_scorecard.json

## Production rule

No cycle-level result may mutate:
- source files
- work-level evidence
- accepted work canon
- frozen historical runs

Cycle reconstruction is a separate analytical layer.
