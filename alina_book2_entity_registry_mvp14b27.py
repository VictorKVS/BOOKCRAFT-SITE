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
EVIDENCE = PROJECT / "evidence" / "chunk_claims_v2"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

CANON_CLAIMS = CANON / "canon_claims.json"
ENTITY_REGISTRY = CANON / "entity_registry.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_entity_id(entity_type: str, canonical_name: str) -> str:
    raw = f"{entity_type}:{norm(canonical_name)}".encode("utf-8")
    return "ent-" + hashlib.sha256(raw).hexdigest()[:16]

def load_known_mentions() -> dict[str, dict[str, Any]]:
    known: dict[str, dict[str, Any]] = {}
    for path in sorted(EVIDENCE.glob("primary-*.json")):
        package = json.loads(path.read_text(encoding="utf-8"))
        validated = package.get("validated") or {}
        for mention in validated.get("mentions", []):
            surface = str(mention.get("surface", "")).strip()
            if not surface:
                continue
            key = norm(surface)
            item = known.setdefault(key, {
                "canonical_name": surface,
                "entity_type": mention.get("entity_type") or "UNKNOWN",
                "aliases": set(),
                "source_mentions": set(),
            })
            for alias in mention.get("aliases") or []:
                if str(alias).strip():
                    item["aliases"].add(str(alias).strip())
            if mention.get("mention_id"):
                item["source_mentions"].add(str(mention["mention_id"]))
    return known

def text_contains_name(text: str, name: str) -> bool:
    return norm(name) in norm(text)

def add_entity(
    registry: dict[str, dict[str, Any]],
    *,
    canonical_name: str,
    entity_type: str,
    aliases: list[str] | None,
    claim_id: str,
    source_mentions: list[str] | None = None,
    role: str,
) -> None:
    key = f"{entity_type}:{norm(canonical_name)}"
    if key not in registry:
        registry[key] = {
            "entity_id": stable_entity_id(entity_type, canonical_name),
            "canonical_name": canonical_name,
            "entity_type": entity_type,
            "aliases": set(),
            "source_claims": set(),
            "source_mentions": set(),
            "roles_in_claims": {},
        }
    item = registry[key]
    for alias in aliases or []:
        if alias and norm(alias) != norm(canonical_name):
            item["aliases"].add(alias)
    if claim_id:
        item["source_claims"].add(claim_id)
        item["roles_in_claims"].setdefault(claim_id, set()).add(role)
    for mid in source_mentions or []:
        item["source_mentions"].add(mid)

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.7 ENTITY REGISTRY ===")

    if not CANON_CLAIMS.exists():
        print(f"FAIL canon_claims_missing: {CANON_CLAIMS}")
        return 1

    store = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    records = store.get("records") or []
    if not records:
        print("FAIL canon_store_empty")
        return 1

    known = load_known_mentions()
    registry: dict[str, dict[str, Any]] = {}

    for rec in records:
        claim_id = str(rec.get("claim_id", ""))
        subject = str(rec.get("subject", "")).strip()
        predicate = str(rec.get("predicate", ""))
        value = str(rec.get("value", ""))
        evidence_text = " ".join(str(e.get("quote", "")) for e in rec.get("evidence") or [])
        searchable = " ".join([subject, predicate, value, evidence_text])

        # 1) Subject entity: only promote when the subject is a known mention.
        subject_key = norm(subject)
        if subject_key in known:
            km = known[subject_key]
            add_entity(
                registry,
                canonical_name=km["canonical_name"],
                entity_type=str(km["entity_type"]),
                aliases=sorted(km["aliases"]),
                claim_id=claim_id,
                source_mentions=sorted(km["source_mentions"]),
                role="SUBJECT",
            )

        # 2) Referenced named entities: only names already known from source mention extraction,
        # and only when they occur literally in the accepted claim/evidence.
        for key, km in known.items():
            name = str(km["canonical_name"])
            if subject_key == key:
                continue
            if text_contains_name(searchable, name):
                add_entity(
                    registry,
                    canonical_name=name,
                    entity_type=str(km["entity_type"]),
                    aliases=sorted(km["aliases"]),
                    claim_id=claim_id,
                    source_mentions=sorted(km["source_mentions"]),
                    role="REFERENCED",
                )

    if not registry:
        print("FAIL no_entities_resolved")
        return 1

    records_out: list[dict[str, Any]] = []
    for item in registry.values():
        records_out.append({
            "entity_id": item["entity_id"],
            "canonical_name": item["canonical_name"],
            "entity_type": item["entity_type"],
            "aliases": sorted(item["aliases"]),
            "source_claims": sorted(item["source_claims"]),
            "source_mentions": sorted(item["source_mentions"]),
            "roles_in_claims": {
                cid: sorted(roles)
                for cid, roles in sorted(item["roles_in_claims"].items())
            },
        })
    records_out.sort(key=lambda x: (x["entity_type"], norm(x["canonical_name"]), x["entity_id"]))

    ids = [x["entity_id"] for x in records_out]
    if len(ids) != len(set(ids)):
        print("FAIL duplicate_entity_ids")
        return 1

    canon_claim_ids = {str(r.get("claim_id", "")) for r in records}
    referenced_claim_ids = {
        cid
        for ent in records_out
        for cid in ent.get("source_claims", [])
    }
    if not referenced_claim_ids.issubset(canon_claim_ids):
        print("FAIL entity_references_noncanon_claim")
        return 1

    payload = {
        "schema_version": "1.0",
        "work_id": store.get("work_id", "sto_let_tomu_vpered"),
        "registry_type": "TRUSTED_ENTITY_REGISTRY",
        "records": records_out,
    }
    ENTITY_REGISTRY.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    type_counts: dict[str, int] = {}
    for ent in records_out:
        et = str(ent.get("entity_type", "UNKNOWN"))
        type_counts[et] = type_counts.get(et, 0) + 1

    run = {
        "stage": "MVP-14B2_7_ENTITY_REGISTRY",
        "result": "PASS",
        "canon_claims_input": len(records),
        "entities_registered": len(records_out),
        "entity_type_counts": type_counts,
        "invariants": {
            "stable_entity_ids": True,
            "entity_ids_unique": True,
            "entities_derived_from_trusted_canon_only": True,
            "referenced_names_must_exist_in_source_mentions": True,
            "no_freeform_entity_invention": True,
        },
    }
    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b2_7_entity_registry.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.7 Entity Registry",
        "",
        f"- Canon claims input: {len(records)}",
        f"- Entities registered: {len(records_out)}",
        "",
        "## Entity types",
    ]
    for key, value in sorted(type_counts.items()):
        lines.append(f"- {key}: {value}")
    lines += [
        "",
        "## Invariants",
        "- Entity IDs are deterministic and unique.",
        "- Entities are linked only to trusted canon claims.",
        "- Referenced names must already exist in source mention extraction.",
        "- The registry does not invent free-form entities from arbitrary text.",
    ]
    (REPORTS / "MVP14B2_7_ENTITY_REGISTRY_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims_input: {len(records)}")
    print(f"PASS entities_registered: {len(records_out)}")
    for key, value in sorted(type_counts.items()):
        print(f"CHECK entity_type_{key}: {value}")
    print("PASS invariant_stable_entity_ids")
    print("PASS invariant_entity_ids_unique")
    print("PASS invariant_entities_from_trusted_canon_only")
    print("PASS invariant_no_freeform_entity_invention")
    print("=== ALINA BOOK 2 MVP-14B2.7 ENTITY REGISTRY: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
