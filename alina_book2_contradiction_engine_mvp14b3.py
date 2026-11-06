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
CONTRADICTIONS = CANON / "contradiction_store.json"
CONTRADICTION_REVIEW = CANON / "contradiction_review_queue.json"

# Conservative v1 ontology. Only predicates explicitly declared single-valued
# may conflict merely because their values differ.
SINGLE_VALUED_PREDICATES = {
    "является",
    "находится",
    "имеет статус",
    "представляет собой",
}

# Explicit semantic opposites. We do NOT infer negation from arbitrary wording.
OPPOSITE_PREDICATES = {
    ("имеет", "не имеет"),
    ("является", "не является"),
    ("находится", "не находится"),
    ("существует", "не существует"),
    ("жив", "мертв"),
}
OPPOSITE_PREDICATES |= {(b, a) for a, b in list(OPPOSITE_PREDICATES)}

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9\s-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def evidence_verified(claim: dict[str, Any]) -> bool:
    ev = claim.get("evidence") or []
    return bool(ev) and all(e.get("quote_verified") is True for e in ev)

def same_subject(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return norm(str(a.get("subject", ""))) == norm(str(b.get("subject", "")))

def same_truth_scope(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return str(a.get("truth_scope", "")).upper() == str(b.get("truth_scope", "")).upper()

def pair_key(a: dict[str, Any], b: dict[str, Any]) -> tuple[str, str]:
    return tuple(sorted([str(a.get("claim_id", "")), str(b.get("claim_id", ""))]))

def classify_pair(a: dict[str, Any], b: dict[str, Any]) -> tuple[str, str, str] | None:
    # Beliefs and objective world-state are different epistemic scopes.
    # Never report them as direct contradictions in v1.
    if not same_truth_scope(a, b):
        return None

    if not same_subject(a, b):
        return None

    pa, pb = norm(str(a.get("predicate", ""))), norm(str(b.get("predicate", "")))
    va, vb = norm(str(a.get("value", ""))), norm(str(b.get("value", "")))

    if not pa or not pb or not va or not vb:
        return None

    # 1. Explicit predicate opposition with the same object/value.
    if (pa, pb) in OPPOSITE_PREDICATES and va == vb:
        return (
            "CONTRADICTION",
            "EXPLICIT_PREDICATE_OPPOSITION",
            "Один субъект имеет взаимоисключающие предикаты для одного и того же значения."
        )

    # 2. Single-valued predicate assigned two different values.
    if pa == pb and pa in SINGLE_VALUED_PREDICATES and va != vb:
        return (
            "CONTRADICTION",
            "SINGLE_VALUED_PROPERTY_CONFLICT",
            "Одному субъекту присвоены разные значения свойства, объявленного single-valued."
        )

    # 3. Same subject/predicate/value is not a contradiction; it is corroboration/duplication.
    return None

def detect(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            a, b = claims[i], claims[j]
            key = pair_key(a, b)
            if key in seen:
                continue
            seen.add(key)

            result = classify_pair(a, b)
            if not result:
                continue

            verdict, conflict_type, reason = result
            cid = stable_id(
                "conflict",
                key[0], key[1], conflict_type,
                a.get("truth_scope", "")
            )
            out.append({
                "contradiction_id": cid,
                "verdict": verdict,
                "conflict_type": conflict_type,
                "reason": reason,
                "truth_scope": a.get("truth_scope"),
                "subject": a.get("subject"),
                "claim_a": {
                    "claim_id": a.get("claim_id"),
                    "predicate": a.get("predicate"),
                    "value": a.get("value"),
                    "evidence": a.get("evidence") or [],
                },
                "claim_b": {
                    "claim_id": b.get("claim_id"),
                    "predicate": b.get("predicate"),
                    "value": b.get("value"),
                    "evidence": b.get("evidence") or [],
                },
            })
    return sorted(out, key=lambda x: x["contradiction_id"])

def regression_self_test() -> None:
    def c(cid: str, subject: str, predicate: str, value: str, scope: str = "WORLD_STATE"):
        return {
            "claim_id": cid,
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "truth_scope": scope,
            "evidence": [{"quote": "synthetic", "quote_verified": True}],
        }

    # Must detect explicit opposition.
    t1 = detect([
        c("t1-a", "Объект", "имеет", "ключ"),
        c("t1-b", "Объект", "не имеет", "ключ"),
    ])
    if len(t1) != 1 or t1[0]["conflict_type"] != "EXPLICIT_PREDICATE_OPPOSITION":
        raise AssertionError("selftest_explicit_opposition_failed")

    # Must detect conflicting single-valued property.
    t2 = detect([
        c("t2-a", "Объект", "находится", "Москва"),
        c("t2-b", "Объект", "находится", "Петербург"),
    ])
    if len(t2) != 1 or t2[0]["conflict_type"] != "SINGLE_VALUED_PROPERTY_CONFLICT":
        raise AssertionError("selftest_single_value_failed")

    # Must NOT mix character belief and objective world-state.
    t3 = detect([
        c("t3-a", "Коля", "является", "врачом", "CHARACTER_BELIEF"),
        c("t3-b", "Коля", "является", "учителем", "WORLD_STATE"),
    ])
    if t3:
        raise AssertionError("selftest_scope_separation_failed")

    # Multi-valued predicates with different values are not automatically contradictions.
    t4 = detect([
        c("t4-a", "Коля", "видит", "дом"),
        c("t4-b", "Коля", "видит", "дерево"),
    ])
    if t4:
        raise AssertionError("selftest_multivalue_false_positive_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B3 CONTRADICTION ENGINE ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    if not CANON_CLAIMS.exists():
        print("FAIL canon_claims_missing")
        return 1

    store = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    claims = store.get("records") or []
    if not claims:
        print("FAIL canon_claims_empty")
        return 1

    for claim in claims:
        if str((claim.get("admission") or {}).get("verdict", "")).upper() != "ACCEPT":
            print(f"FAIL nonaccepted_claim_in_trusted_store: {claim.get('claim_id')}")
            return 1
        if not evidence_verified(claim):
            print(f"FAIL unverified_evidence_in_trusted_store: {claim.get('claim_id')}")
            return 1

    conflicts = detect(claims)

    # v1 review queue is reserved for future temporal/ontology ambiguity checks.
    review: list[dict[str, Any]] = []

    CONTRADICTIONS.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": store.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_CONTRADICTIONS",
        "engine_version": "MVP-14B3-v1",
        "records": conflicts,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    CONTRADICTION_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": store.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "CONTRADICTION_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    type_counts: dict[str, int] = {}
    for item in conflicts:
        t = str(item.get("conflict_type", "UNKNOWN"))
        type_counts[t] = type_counts.get(t, 0) + 1

    run = {
        "stage": "MVP-14B3_CONTRADICTION_ENGINE",
        "result": "PASS",
        "canon_claims_input": len(claims),
        "contradictions_found": len(conflicts),
        "review_queue": len(review),
        "conflict_type_counts": type_counts,
        "regression_tests": {
            "explicit_predicate_opposition": "PASS",
            "single_valued_property_conflict": "PASS",
            "truth_scope_separation": "PASS",
            "multivalue_false_positive_guard": "PASS",
        },
        "invariants": {
            "trusted_canon_only": True,
            "verified_evidence_required": True,
            "truth_scopes_not_mixed": True,
            "conservative_rules_only": True,
            "deterministic_conflict_ids": True,
        },
        "limitations": [
            "Temporal contradictions are not evaluated in v1 because trusted claims do not yet carry normalized time intervals.",
            "Coreference/morphological entity resolution is not inferred by this stage.",
            "Only explicit predicate opposites and declared single-valued predicates are treated as contradictions.",
        ],
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b3_contradiction_engine.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B3 Contradiction Engine",
        "",
        f"- Canon claims input: {len(claims)}",
        f"- Contradictions found: {len(conflicts)}",
        f"- Review queue: {len(review)}",
        "",
        "## Regression tests",
        "- Explicit predicate opposition: PASS",
        "- Single-valued property conflict: PASS",
        "- Truth-scope separation: PASS",
        "- Multi-valued false-positive guard: PASS",
        "",
        "## Current v1 policy",
        "- Only trusted canon claims are compared.",
        "- CHARACTER_BELIEF and WORLD_STATE are never treated as the same truth scope.",
        "- Explicit opposite predicates may conflict for the same subject/value.",
        "- Different values conflict only for predicates declared single-valued.",
        "- Temporal contradictions are intentionally deferred until normalized time is available.",
    ]
    (REPORTS / "MVP14B3_CONTRADICTION_ENGINE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS canon_claims_input: {len(claims)}")
    print(f"CHECK contradictions_found: {len(conflicts)}")
    print(f"CHECK review_queue: {len(review)}")
    print("PASS invariant_trusted_canon_only")
    print("PASS invariant_truth_scopes_not_mixed")
    print("PASS invariant_conservative_rules_only")
    print("=== ALINA BOOK 2 MVP-14B3 CONTRADICTION ENGINE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
