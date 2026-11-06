from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
EVIDENCE = PROJECT / "evidence" / "chunk_claims_v2"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

ACCEPTED = "CANON_ACCEPTED"
REVIEW = "CANON_REVIEW"

def iter_claims(validated: dict[str, Any]):
    for mention in validated.get("mentions", []):
        for claim in mention.get("claims", []):
            yield "mention", mention.get("surface", ""), claim
    for event in validated.get("events", []):
        for claim in event.get("claims", []):
            yield "event", event.get("event", ""), claim
    for term in validated.get("terms", []):
        claim = term.get("definition_claim")
        if isinstance(claim, dict):
            yield "term", term.get("term", ""), claim

def stable_record_id(work_id: str, claim_id: str) -> str:
    raw = f"{work_id}:{claim_id}".encode("utf-8")
    return "canon-" + hashlib.sha256(raw).hexdigest()[:16]

def source_record(path: Path, scope: str, subject: str, claim: dict[str, Any]) -> dict[str, Any]:
    admission = claim.get("canon_admission") or {}
    evidence = []
    for ev in claim.get("evidence") or []:
        evidence.append({
            "chunk_id": ev.get("chunk_id"),
            "paragraph_start": ev.get("paragraph_start"),
            "paragraph_end": ev.get("paragraph_end"),
            "quote": ev.get("quote"),
            "quote_verified": ev.get("quote_verified") is True,
        })

    return {
        "record_id": stable_record_id("sto_let_tomu_vpered", str(claim.get("claim_id", ""))),
        "work_id": "sto_let_tomu_vpered",
        "claim_id": claim.get("claim_id"),
        "scope": scope,
        "subject": subject,
        "predicate": claim.get("predicate"),
        "value": claim.get("value"),
        "truth_scope": admission.get("truth_scope", "UNKNOWN"),
        "provenance": claim.get("provenance"),
        "confidence": claim.get("confidence"),
        "admission": {
            "stage": admission.get("stage"),
            "verdict": admission.get("verdict"),
            "reason": admission.get("reason"),
            "checks": admission.get("checks") or [],
        },
        "evidence": evidence,
        "source_artifact": str(path.relative_to(ROOT)).replace("\\", "/"),
    }

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.6 CANON STORE ===")

    files = sorted(EVIDENCE.glob("primary-*.json"))
    if not files:
        print("FAIL no_claim_files")
        return 1

    accepted_records: list[dict[str, Any]] = []
    review_records: list[dict[str, Any]] = []

    for path in files:
        package = json.loads(path.read_text(encoding="utf-8"))
        validated = package["validated"]
        for scope, subject, claim in iter_claims(validated):
            status = claim.get("acceptance")
            if status == ACCEPTED:
                accepted_records.append(source_record(path, scope, subject, claim))
            elif status == REVIEW:
                review_records.append(source_record(path, scope, subject, claim))

    # Deterministic ordering is important for diffs, audit and reproducibility.
    accepted_records.sort(key=lambda x: (str(x.get("claim_id")), str(x.get("record_id"))))
    review_records.sort(key=lambda x: (str(x.get("claim_id")), str(x.get("record_id"))))

    accepted_ids = [x["claim_id"] for x in accepted_records]
    review_ids = [x["claim_id"] for x in review_records]

    if len(accepted_ids) != len(set(accepted_ids)):
        print("FAIL duplicate_accepted_claim_ids")
        return 1
    if len(review_ids) != len(set(review_ids)):
        print("FAIL duplicate_review_claim_ids")
        return 1
    if set(accepted_ids) & set(review_ids):
        print("FAIL claim_in_both_canon_and_review")
        return 1

    for rec in accepted_records:
        if rec["admission"]["verdict"] != "ACCEPT":
            print(f"FAIL accepted_without_admission_accept: {rec['claim_id']}")
            return 1
        if not rec["evidence"] or not all(e.get("quote_verified") for e in rec["evidence"]):
            print(f"FAIL accepted_without_verified_evidence: {rec['claim_id']}")
            return 1

    CANON.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    canon_claims = {
        "schema_version": "1.0",
        "work_id": "sto_let_tomu_vpered",
        "store_type": "TRUSTED_CANON_CLAIMS",
        "records": accepted_records,
    }
    review_queue = {
        "schema_version": "1.0",
        "work_id": "sto_let_tomu_vpered",
        "store_type": "CANON_REVIEW_QUEUE",
        "records": review_records,
    }

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "schema_version": "1.0",
        "work_id": "sto_let_tomu_vpered",
        "stage": "MVP-14B2.6_CANON_STORE",
        "generated_at_utc": generated_at,
        "canon_claims_file": "canon_claims.json",
        "review_queue_file": "canon_review_queue.json",
        "canon_claims": len(accepted_records),
        "review_queue": len(review_records),
        "truth_scope_counts": {},
        "invariants": {
            "canon_contains_only_admission_accept": True,
            "review_is_physically_separated": True,
            "verified_evidence_required": True,
            "claim_ids_unique": True,
            "canon_review_disjoint": True,
        },
    }
    for rec in accepted_records:
        ts = str(rec.get("truth_scope", "UNKNOWN"))
        manifest["truth_scope_counts"][ts] = manifest["truth_scope_counts"].get(ts, 0) + 1

    (CANON / "canon_claims.json").write_text(
        json.dumps(canon_claims, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CANON / "canon_review_queue.json").write_text(
        json.dumps(review_queue, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CANON / "canon_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    run = {
        "stage": "MVP-14B2_6_CANON_STORE",
        "result": "PASS",
        "canon_claims": len(accepted_records),
        "review_queue": len(review_records),
        "accepted_claim_ids": accepted_ids,
        "review_claim_ids": review_ids,
        "truth_scope_counts": manifest["truth_scope_counts"],
        "invariants": manifest["invariants"],
    }
    (RUNS / "mvp14b2_6_canon_store.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.6 Canon Store",
        "",
        f"- CANON records: {len(accepted_records)}",
        f"- REVIEW records: {len(review_records)}",
        "",
        "## Truth scopes",
    ]
    for key, value in sorted(manifest["truth_scope_counts"].items()):
        lines.append(f"- {key}: {value}")
    lines += [
        "",
        "## Invariants",
        "- Canon contains only records admitted with verdict ACCEPT.",
        "- Review queue is physically separated from trusted canon.",
        "- Every canon record contains verified source evidence.",
        "- Claim IDs are unique.",
        "- Canon and review sets are disjoint.",
    ]
    (REPORTS / "MVP14B2_6_CANON_STORE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims: {len(accepted_records)}")
    print(f"PASS review_queue: {len(review_records)}")
    print("PASS invariant_canon_contains_only_admission_accept")
    print("PASS invariant_review_physically_separated")
    print("PASS invariant_verified_evidence_required")
    print("PASS invariant_claim_ids_unique")
    print("PASS invariant_canon_review_disjoint")
    print("=== ALINA BOOK 2 MVP-14B2.6 CANON STORE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
