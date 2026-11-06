from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

CANON_CLAIMS = CANON / "canon_claims.json"
TEMPORAL_MODEL = CANON / "temporal_model.json"
ENTITY_REGISTRY = CANON / "entity_registry.json"
STATE_STORE = CANON / "state_store.json"
STATE_REVIEW = CANON / "state_review_queue.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def resolve_subject_entity(subject: str, entities: list[dict[str, Any]]) -> dict[str, Any] | None:
    key = norm(subject)
    exact = []
    for ent in entities:
        names = [str(ent.get("canonical_name", ""))] + [str(x) for x in ent.get("aliases") or []]
        if any(norm(name) == key for name in names if str(name).strip()):
            exact.append(ent)
    if len(exact) == 1:
        return exact[0]
    return None

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B5 STATE ENGINE ===")

    for path, label in [
        (CANON_CLAIMS, "canon_claims"),
        (TEMPORAL_MODEL, "temporal_model"),
        (ENTITY_REGISTRY, "entity_registry"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    canon = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    temporal = json.loads(TEMPORAL_MODEL.read_text(encoding="utf-8"))
    entity_data = json.loads(ENTITY_REGISTRY.read_text(encoding="utf-8"))

    claims = canon.get("records") or []
    timeline = temporal.get("timeline") or []
    entities = entity_data.get("records") or []

    if not claims or not timeline or not entities:
        print("FAIL required_store_empty")
        return 1

    claims_by_id = {str(c.get("claim_id", "")): c for c in claims}
    temporal_by_claim = {str(t.get("claim_id", "")): t for t in timeline}
    entity_ids = {str(e.get("entity_id", "")) for e in entities}

    states: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    for claim_id, claim in claims_by_id.items():
        temporal_item = temporal_by_claim.get(claim_id)
        if temporal_item is None:
            review.append({
                "review_id": stable_id("staterev", claim_id, "no_temporal_anchor"),
                "claim_id": claim_id,
                "reason": "NO_TEMPORAL_ANCHOR",
            })
            continue

        subject = str(claim.get("subject", "")).strip()
        ent = resolve_subject_entity(subject, entities)
        if ent is None:
            review.append({
                "review_id": stable_id("staterev", claim_id, "subject_unresolved"),
                "claim_id": claim_id,
                "reason": "SUBJECT_ENTITY_UNRESOLVED",
                "subject": subject,
                "predicate": claim.get("predicate"),
                "value": claim.get("value"),
                "temporal_id": temporal_item.get("temporal_id"),
            })
            continue

        truth_scope = str(claim.get("truth_scope", "UNKNOWN"))
        state_kind = "EPISTEMIC_OBSERVATION" if truth_scope == "CHARACTER_BELIEF" else "WORLD_STATE_OBSERVATION"

        state = {
            "state_id": stable_id(
                "state",
                ent.get("entity_id", ""),
                claim_id,
                temporal_item.get("temporal_id", ""),
                claim.get("predicate", ""),
                claim.get("value", ""),
            ),
            "entity_id": ent.get("entity_id"),
            "entity_name": ent.get("canonical_name"),
            "entity_type": ent.get("entity_type"),
            "claim_id": claim_id,
            "temporal_id": temporal_item.get("temporal_id"),
            "sequence_index": temporal_item.get("sequence_index"),
            "temporal_basis": temporal_item.get("temporal_basis"),
            "world_time_status": temporal_item.get("world_time_status"),
            "state_kind": state_kind,
            "truth_scope": truth_scope,
            "predicate": claim.get("predicate"),
            "value": claim.get("value"),
            "persistence": "NOT_INFERRED",
            "valid_from": "OBSERVATION_ONLY",
            "valid_until": "UNKNOWN",
            "evidence": claim.get("evidence") or [],
        }
        states.append(state)

    states.sort(key=lambda x: (
        int(x.get("sequence_index", 10**9)),
        str(x.get("entity_id", "")),
        str(x.get("state_id", "")),
    ))
    review.sort(key=lambda x: x["review_id"])

    ids = [s["state_id"] for s in states]
    if len(ids) != len(set(ids)):
        print("FAIL duplicate_state_ids")
        return 1

    for s in states:
        if s["entity_id"] not in entity_ids:
            print(f"FAIL unknown_entity_in_state: {s['state_id']}")
            return 1
        if s["claim_id"] not in claims_by_id:
            print(f"FAIL noncanon_claim_in_state: {s['state_id']}")
            return 1
        if s["temporal_id"] not in {str(t.get("temporal_id", "")) for t in timeline}:
            print(f"FAIL unknown_temporal_id_in_state: {s['state_id']}")
            return 1
        ev = s.get("evidence") or []
        if not ev or not all(e.get("quote_verified") is True for e in ev):
            print(f"FAIL unverified_evidence_in_state: {s['state_id']}")
            return 1
        if s["persistence"] != "NOT_INFERRED":
            print(f"FAIL persistence_inferred: {s['state_id']}")
            return 1

    # Entity-centric indexes without inventing persistence.
    entity_states: dict[str, list[str]] = {}
    for s in states:
        entity_states.setdefault(str(s["entity_id"]), []).append(str(s["state_id"]))

    payload = {
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_STATE_OBSERVATIONS",
        "semantics": {
            "WORLD_STATE_OBSERVATION": "A trusted world-state assertion observed at a verified textual position.",
            "EPISTEMIC_OBSERVATION": "A trusted assertion about a character belief/intention/epistemic state.",
            "persistence": "NOT_INFERRED in MVP-14B5. No state is assumed to remain true after its observation point.",
        },
        "records": states,
        "entity_state_index": entity_states,
    }
    STATE_STORE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    STATE_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "STATE_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    world_states = sum(1 for s in states if s["state_kind"] == "WORLD_STATE_OBSERVATION")
    epistemic_states = sum(1 for s in states if s["state_kind"] == "EPISTEMIC_OBSERVATION")

    run = {
        "stage": "MVP-14B5_STATE_ENGINE",
        "result": "PASS",
        "canon_claims_input": len(claims),
        "state_observations": len(states),
        "world_state_observations": world_states,
        "epistemic_observations": epistemic_states,
        "review_queue": len(review),
        "entities_with_states": len(entity_states),
        "invariants": {
            "trusted_canon_only": True,
            "known_entities_only": True,
            "known_temporal_anchors_only": True,
            "verified_evidence_required": True,
            "belief_world_state_separation": True,
            "state_persistence_not_inferred": True,
            "deterministic_state_ids": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b5_state_engine.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B5 State Engine",
        "",
        f"- Canon claims input: {len(claims)}",
        f"- State observations: {len(states)}",
        f"- World-state observations: {world_states}",
        f"- Epistemic observations: {epistemic_states}",
        f"- Entities with states: {len(entity_states)}",
        f"- Review queue: {len(review)}",
        "",
        "## Semantics",
        "- State Engine v1 stores observations, not inferred continuous states.",
        "- WORLD_STATE and CHARACTER_BELIEF remain separate.",
        "- No state persistence is inferred between textual positions.",
        "- valid_until remains UNKNOWN unless future evidence establishes a transition.",
        "",
        "## Invariants",
        "- Every state originates from trusted canon.",
        "- Every state references a known entity and trusted temporal anchor.",
        "- Verified source evidence is mandatory.",
        "- State IDs are deterministic.",
    ]
    (REPORTS / "MVP14B5_STATE_ENGINE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims_input: {len(claims)}")
    print(f"PASS state_observations: {len(states)}")
    print(f"CHECK world_state_observations: {world_states}")
    print(f"CHECK epistemic_observations: {epistemic_states}")
    print(f"CHECK entities_with_states: {len(entity_states)}")
    print(f"CHECK review_queue: {len(review)}")
    print("PASS invariant_belief_world_state_separation")
    print("PASS invariant_state_persistence_not_inferred")
    print("=== ALINA BOOK 2 MVP-14B5 STATE ENGINE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
