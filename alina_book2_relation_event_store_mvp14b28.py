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
ENTITY_REGISTRY = CANON / "entity_registry.json"
RELATION_STORE = CANON / "relation_store.json"
EVENT_STORE = CANON / "event_store.json"
RELATION_REVIEW = CANON / "relation_review_queue.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(p) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def find_entity_by_name(entities: list[dict[str, Any]], text: str) -> dict[str, Any] | None:
    t = norm(text)
    exact = []
    contained = []
    for ent in entities:
        names = [str(ent.get("canonical_name", ""))] + [str(x) for x in ent.get("aliases") or []]
        for name in names:
            n = norm(name)
            if not n:
                continue
            if t == n:
                exact.append(ent)
            elif n in t:
                contained.append(ent)
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None
    # Prefer the longest unique contained name to reduce accidental partial matches.
    if contained:
        contained = sorted(contained, key=lambda e: len(norm(str(e.get("canonical_name", "")))), reverse=True)
        best_len = len(norm(str(contained[0].get("canonical_name", ""))))
        best = [e for e in contained if len(norm(str(e.get("canonical_name", "")))) == best_len]
        if len({e.get("entity_id") for e in best}) == 1:
            return best[0]
    return None

def verified_evidence(rec: dict[str, Any]) -> bool:
    evidence = rec.get("evidence") or []
    return bool(evidence) and all(e.get("quote_verified") is True for e in evidence)

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.8 RELATION & EVENT STORE ===")

    if not CANON_CLAIMS.exists():
        print("FAIL canon_claims_missing")
        return 1
    if not ENTITY_REGISTRY.exists():
        print("FAIL entity_registry_missing")
        return 1

    canon = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    entity_data = json.loads(ENTITY_REGISTRY.read_text(encoding="utf-8"))
    claims = canon.get("records") or []
    entities = entity_data.get("records") or []

    if not claims:
        print("FAIL canon_claims_empty")
        return 1
    if not entities:
        print("FAIL entity_registry_empty")
        return 1

    canon_ids = {str(c.get("claim_id", "")) for c in claims}
    entity_ids = {str(e.get("entity_id", "")) for e in entities}

    relations: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    for rec in claims:
        claim_id = str(rec.get("claim_id", ""))
        subject = str(rec.get("subject", "")).strip()
        predicate = str(rec.get("predicate", "")).strip()
        value = str(rec.get("value", "")).strip()
        scope = str(rec.get("scope", "")).strip()
        truth_scope = str(rec.get("truth_scope", "UNKNOWN"))

        if not verified_evidence(rec):
            print(f"FAIL trusted_claim_without_verified_evidence: {claim_id}")
            return 1

        source_entity = find_entity_by_name(entities, subject)

        # Trusted event claims are stored as events, but only when the event subject itself
        # is backed by at least one entity. Event text remains separate from relations.
        if scope == "event":
            if source_entity is None:
                review.append({
                    "review_id": stable_id("relrev", claim_id, "event_subject_unresolved"),
                    "claim_id": claim_id,
                    "reason": "EVENT_SUBJECT_ENTITY_UNRESOLVED",
                    "subject": subject,
                    "predicate": predicate,
                    "value": value,
                    "truth_scope": truth_scope,
                    "evidence": rec.get("evidence") or [],
                })
                continue
            events.append({
                "event_id": stable_id("evt", claim_id, subject, predicate, value),
                "claim_id": claim_id,
                "event_type": predicate,
                "actor_entity_id": source_entity["entity_id"],
                "actor_name": source_entity["canonical_name"],
                "description": subject,
                "value": value,
                "truth_scope": truth_scope,
                "evidence": rec.get("evidence") or [],
            })
            continue

        if source_entity is None:
            review.append({
                "review_id": stable_id("relrev", claim_id, "source_unresolved"),
                "claim_id": claim_id,
                "reason": "SOURCE_ENTITY_UNRESOLVED",
                "subject": subject,
                "predicate": predicate,
                "value": value,
                "truth_scope": truth_scope,
                "evidence": rec.get("evidence") or [],
            })
            continue

        # Try to resolve an object entity from the claim value first.
        target_entity = find_entity_by_name(entities, value)

        if target_entity is not None and target_entity["entity_id"] != source_entity["entity_id"]:
            relations.append({
                "relation_id": stable_id(
                    "rel", claim_id, source_entity["entity_id"], predicate, target_entity["entity_id"]
                ),
                "claim_id": claim_id,
                "source_entity_id": source_entity["entity_id"],
                "source_name": source_entity["canonical_name"],
                "predicate": predicate,
                "target_kind": "ENTITY",
                "target_entity_id": target_entity["entity_id"],
                "target_name": target_entity["canonical_name"],
                "truth_scope": truth_scope,
                "evidence": rec.get("evidence") or [],
            })
        else:
            # Do not invent an entity for arbitrary value text. Preserve it as a proposition/literal.
            relations.append({
                "relation_id": stable_id("rel", claim_id, source_entity["entity_id"], predicate, value),
                "claim_id": claim_id,
                "source_entity_id": source_entity["entity_id"],
                "source_name": source_entity["canonical_name"],
                "predicate": predicate,
                "target_kind": "PROPOSITION" if truth_scope == "CHARACTER_BELIEF" else "LITERAL",
                "target_value": value,
                "truth_scope": truth_scope,
                "evidence": rec.get("evidence") or [],
            })

    # Invariants.
    relation_ids = [r["relation_id"] for r in relations]
    event_ids = [e["event_id"] for e in events]
    if len(relation_ids) != len(set(relation_ids)):
        print("FAIL duplicate_relation_ids")
        return 1
    if len(event_ids) != len(set(event_ids)):
        print("FAIL duplicate_event_ids")
        return 1

    for r in relations:
        if r["claim_id"] not in canon_ids:
            print(f"FAIL relation_noncanon_claim: {r['relation_id']}")
            return 1
        if r["source_entity_id"] not in entity_ids:
            print(f"FAIL relation_unknown_source_entity: {r['relation_id']}")
            return 1
        if r.get("target_kind") == "ENTITY" and r.get("target_entity_id") not in entity_ids:
            print(f"FAIL relation_unknown_target_entity: {r['relation_id']}")
            return 1
        if not r.get("evidence") or not all(e.get("quote_verified") is True for e in r["evidence"]):
            print(f"FAIL relation_unverified_evidence: {r['relation_id']}")
            return 1

    for e in events:
        if e["claim_id"] not in canon_ids:
            print(f"FAIL event_noncanon_claim: {e['event_id']}")
            return 1
        if e["actor_entity_id"] not in entity_ids:
            print(f"FAIL event_unknown_actor: {e['event_id']}")
            return 1

    relations.sort(key=lambda x: x["relation_id"])
    events.sort(key=lambda x: x["event_id"])
    review.sort(key=lambda x: x["review_id"])

    RELATION_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_RELATIONS",
        "records": relations,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    EVENT_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_EVENTS",
        "records": events,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    RELATION_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "RELATION_EVENT_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    run = {
        "stage": "MVP-14B2_8_RELATION_EVENT_STORE",
        "result": "PASS",
        "canon_claims_input": len(claims),
        "relations_written": len(relations),
        "events_written": len(events),
        "review_queue": len(review),
        "entity_targets": sum(1 for r in relations if r.get("target_kind") == "ENTITY"),
        "proposition_targets": sum(1 for r in relations if r.get("target_kind") == "PROPOSITION"),
        "literal_targets": sum(1 for r in relations if r.get("target_kind") == "LITERAL"),
        "invariants": {
            "relations_from_trusted_canon_only": True,
            "events_from_trusted_canon_only": True,
            "known_entity_ids_only": True,
            "verified_evidence_required": True,
            "no_freeform_entity_invention": True,
            "beliefs_preserved_as_propositions": True,
            "stable_relation_event_ids": True,
        },
    }
    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b2_8_relation_event_store.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.8 Relation / Event Store",
        "",
        f"- Canon claims input: {len(claims)}",
        f"- Relations written: {len(relations)}",
        f"- Events written: {len(events)}",
        f"- Review queue: {len(review)}",
        f"- Entity targets: {run['entity_targets']}",
        f"- Proposition targets: {run['proposition_targets']}",
        f"- Literal targets: {run['literal_targets']}",
        "",
        "## Invariants",
        "- Relations and events originate only from trusted canon claims.",
        "- Entity endpoints must exist in the trusted Entity Registry.",
        "- Verified evidence is mandatory.",
        "- Arbitrary text is never promoted to a new entity.",
        "- Character beliefs remain propositions rather than objective world-state facts.",
        "- Relation and event IDs are deterministic.",
    ]
    (REPORTS / "MVP14B2_8_RELATION_EVENT_STORE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims_input: {len(claims)}")
    print(f"PASS relations_written: {len(relations)}")
    print(f"PASS events_written: {len(events)}")
    print(f"CHECK review_queue: {len(review)}")
    print(f"CHECK entity_targets: {run['entity_targets']}")
    print(f"CHECK proposition_targets: {run['proposition_targets']}")
    print(f"CHECK literal_targets: {run['literal_targets']}")
    print("PASS invariant_relations_from_trusted_canon_only")
    print("PASS invariant_known_entity_ids_only")
    print("PASS invariant_no_freeform_entity_invention")
    print("PASS invariant_beliefs_preserved_as_propositions")
    print("=== ALINA BOOK 2 MVP-14B2.8 RELATION & EVENT STORE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
