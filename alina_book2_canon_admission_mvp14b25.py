from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
EVIDENCE = PROJECT / "evidence" / "chunk_claims_v2"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

SAFE_INPUT = "SAFE_CANON_CANDIDATE"

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

def admission_verdict(scope: str, subject: str, claim: dict[str, Any]) -> tuple[str, str, list[str]]:
    checks: list[str] = []

    evidence = claim.get("evidence") or []
    if not evidence:
        return "REJECT", "NO_EVIDENCE", ["evidence_missing"]

    verified = [e for e in evidence if e.get("quote_verified") is True and str(e.get("quote", "")).strip()]
    if not verified:
        return "REJECT", "UNVERIFIED_EVIDENCE", ["verified_quote_missing"]
    checks.append("evidence_verified")

    safety = claim.get("deterministic_safety") or {}
    if str(safety.get("verdict", "")).upper() != "PASS":
        return "REJECT", "SAFETY_NOT_PASSED", checks + ["deterministic_safety_not_pass"]
    checks.append("deterministic_safety_pass")

    entailment = claim.get("entailment") or {}
    if str(entailment.get("verdict", "")).upper() != "SUPPORTED":
        return "REVIEW", "ENTAILMENT_NOT_STRICTLY_SUPPORTED", checks + ["entailment_not_supported"]
    checks.append("entailment_supported")

    precision = claim.get("precision_gate") or {}
    if str(precision.get("verdict", "")).upper() != "FINAL_CANON_CANDIDATE":
        return "REVIEW", "PRECISION_NOT_FINAL", checks + ["precision_not_final"]
    checks.append("precision_final")

    narrative = claim.get("narrative_mode") or {}
    if narrative and narrative.get("canon_eligible") is not True:
        return "REJECT", "NARRATIVE_NOT_CANON_ELIGIBLE", checks + ["narrative_not_canon_eligible"]
    if narrative:
        checks.append("narrative_canon_eligible")

    mode = str(narrative.get("mode", "")).upper()
    predicate = str(claim.get("predicate", "")).casefold()
    if mode == "CHARACTER_BELIEF":
        # A belief can enter canon only as the fact that the character thinks/assumes/wants/etc.
        # Never promote the proposition inside the belief to objective world-state truth.
        belief_predicates = (
            "предполага", "дума", "счит", "вер", "хоч", "прос", "наде", "бо",
            "реш", "план", "сомнева", "подозрева", "помн", "зна"
        )
        if not any(stem in predicate for stem in belief_predicates):
            return "REVIEW", "BELIEF_SCOPE_AMBIGUOUS", checks + ["belief_scope_requires_review"]
        checks.append("belief_scope_preserved")

    if not str(subject).strip():
        return "REVIEW", "EMPTY_SUBJECT", checks + ["subject_missing"]
    if not str(claim.get("predicate", "")).strip() or not str(claim.get("value", "")).strip():
        return "REVIEW", "INCOMPLETE_CLAIM", checks + ["claim_incomplete"]
    checks.append("claim_complete")

    return "ACCEPT", "ALL_ADMISSION_CHECKS_PASSED", checks

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.5 CANON ADMISSION GATE ===")

    files = sorted(EVIDENCE.glob("primary-*.json"))
    if not files:
        print("FAIL no_claim_files")
        return 1

    safe_inputs = checked = accepted = review = rejected = 0
    reasons: dict[str, int] = {}
    admitted_ids: list[str] = []

    for i, path in enumerate(files, 1):
        package = json.loads(path.read_text(encoding="utf-8"))
        validated = package["validated"]
        chunk_id = validated["chunk_id"]
        touched = 0

        for scope, subject, claim in iter_claims(validated):
            if claim.get("acceptance") != SAFE_INPUT:
                continue

            safe_inputs += 1
            touched += 1
            verdict, reason, checks = admission_verdict(scope, subject, claim)
            checked += 1
            reasons[reason] = reasons.get(reason, 0) + 1

            claim["canon_admission"] = {
                "stage": "MVP-14B2.5",
                "verdict": verdict,
                "reason": reason,
                "checks": checks,
                "scope": scope,
                "subject": subject,
                "truth_scope": (
                    "CHARACTER_BELIEF"
                    if str((claim.get("narrative_mode") or {}).get("mode", "")).upper() == "CHARACTER_BELIEF"
                    else "WORLD_STATE"
                ),
            }

            if verdict == "ACCEPT":
                claim["acceptance"] = "CANON_ACCEPTED"
                accepted += 1
                admitted_ids.append(str(claim.get("claim_id", "")))
            elif verdict == "REVIEW":
                claim["acceptance"] = "CANON_REVIEW"
                review += 1
            else:
                claim["acceptance"] = "CANON_REJECTED"
                rejected += 1

        if touched:
            print(f"[{i}/{len(files)}] ADMISSION {chunk_id}: {touched}")
            path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    if safe_inputs == 0:
        print("FAIL no_safe_canon_candidates")
        return 1
    if checked != safe_inputs:
        print(f"FAIL admission_count_mismatch: safe={safe_inputs} checked={checked}")
        return 1

    # Safety invariant: only SAFE_CANON_CANDIDATE inputs are processed by this stage.
    result = {
        "stage": "MVP-14B2_5_CANON_ADMISSION_GATE",
        "result": "PASS",
        "safe_canon_inputs": safe_inputs,
        "admission_checked": checked,
        "canon_accepted": accepted,
        "canon_review": review,
        "canon_rejected": rejected,
        "admitted_claim_ids": admitted_ids,
        "reason_types": reasons,
        "invariants": {
            "only_safe_candidates_processed": True,
            "character_belief_truth_scope_preserved": True,
            "verified_evidence_required": True,
            "deterministic_safety_pass_required": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    (RUNS / "mvp14b2_5_canon_admission.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.5 Canon Admission Gate",
        "",
        f"- SAFE_CANON_CANDIDATE inputs: {safe_inputs}",
        f"- Admission checked: {checked}",
        f"- CANON_ACCEPTED: {accepted}",
        f"- CANON_REVIEW: {review}",
        f"- CANON_REJECTED: {rejected}",
        "",
        "## Invariants",
        "- Only SAFE_CANON_CANDIDATE inputs are processed.",
        "- Verified source evidence is mandatory.",
        "- Deterministic safety PASS is mandatory.",
        "- Character beliefs stay CHARACTER_BELIEF and are not promoted to objective world-state truth.",
        "",
        "## Reason types",
    ]
    for key, value in sorted(reasons.items()):
        lines.append(f"- {key}: {value}")

    (REPORTS / "MVP14B2_5_CANON_ADMISSION_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS safe_canon_inputs: {safe_inputs}")
    print(f"PASS admission_checked: {checked}")
    print(f"CHECK canon_accepted: {accepted}")
    print(f"CHECK canon_review: {review}")
    print(f"CHECK canon_rejected: {rejected}")
    print("PASS invariant_only_safe_candidates_processed")
    print("PASS invariant_character_belief_truth_scope_preserved")
    print("=== ALINA BOOK 2 MVP-14B2.5 CANON ADMISSION GATE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
