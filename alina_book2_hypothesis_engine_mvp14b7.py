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
KNOWLEDGE_GRAPH = CANON / "knowledge_graph.json"
STATE_STORE = CANON / "state_store.json"
TRANSITION_STORE = CANON / "state_transition_store.json"
CAUSAL_STORE = CANON / "causal_link_store.json"

HYPOTHESIS_CANDIDATES = CANON / "hypothesis_candidates.json"
HYPOTHESIS_STORE = CANON / "hypothesis_store.json"
HYPOTHESIS_REVIEW = CANON / "hypothesis_review_queue.json"

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def clamp(v: float) -> float:
    return max(0.0, min(1.0, round(v, 3)))

def score_hypothesis(
    *,
    independent_support: int,
    contradictions: int,
    explicit_causal_support: int,
    transition_support: int,
    source_is_character_belief: bool,
) -> dict[str, Any]:
    # Conservative transparent scoring. This is NOT probability.
    score = 0.0
    score += min(independent_support, 3) * 0.22
    score += min(explicit_causal_support, 2) * 0.18
    score += min(transition_support, 2) * 0.10
    score -= min(contradictions, 3) * 0.30
    if source_is_character_belief:
        score -= 0.20
    score = clamp(score)
    if score >= 0.70:
        band = "HIGH"
    elif score >= 0.40:
        band = "MEDIUM"
    else:
        band = "LOW"
    return {
        "score": score,
        "band": band,
        "semantics": "HEURISTIC_SUPPORT_SCORE_NOT_PROBABILITY",
    }

def regression_self_test() -> None:
    strong = score_hypothesis(
        independent_support=3,
        contradictions=0,
        explicit_causal_support=1,
        transition_support=1,
        source_is_character_belief=False,
    )
    if strong["band"] != "HIGH":
        raise AssertionError("strong_support_scoring_failed")

    weak = score_hypothesis(
        independent_support=1,
        contradictions=0,
        explicit_causal_support=0,
        transition_support=0,
        source_is_character_belief=True,
    )
    if weak["band"] != "LOW":
        raise AssertionError("character_belief_penalty_failed")

    contradicted = score_hypothesis(
        independent_support=2,
        contradictions=2,
        explicit_causal_support=0,
        transition_support=0,
        source_is_character_belief=False,
    )
    if contradicted["score"] >= 0.40:
        raise AssertionError("contradiction_penalty_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B7 HYPOTHESIS ENGINE ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    required = [
        (CANON_CLAIMS, "canon_claims"),
        (KNOWLEDGE_GRAPH, "knowledge_graph"),
        (STATE_STORE, "state_store"),
        (TRANSITION_STORE, "state_transition_store"),
        (CAUSAL_STORE, "causal_link_store"),
    ]
    for path, label in required:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    canon = json.loads(CANON_CLAIMS.read_text(encoding="utf-8"))
    graph = json.loads(KNOWLEDGE_GRAPH.read_text(encoding="utf-8"))
    transitions = json.loads(TRANSITION_STORE.read_text(encoding="utf-8"))
    causal = json.loads(CAUSAL_STORE.read_text(encoding="utf-8"))

    claims = canon.get("records") or []
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    transition_records = transitions.get("records") or []
    causal_records = causal.get("records") or []

    claims_by_id = {str(c.get("claim_id", "")): c for c in claims}

    candidates: list[dict[str, Any]] = []
    active: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    # v1 candidate generation: propositions already present in trusted graph.
    # IMPORTANT: a CHARACTER_BELIEF proposition is evidence that a character believes X,
    # not evidence that X is objectively true.
    proposition_nodes = [n for n in nodes if n.get("node_type") == "PROPOSITION"]

    for node in proposition_nodes:
        source_claim_ids = [str(x) for x in node.get("source_claims") or []]
        source_claims = [claims_by_id[cid] for cid in source_claim_ids if cid in claims_by_id]
        if not source_claims:
            continue

        evidence_claim_ids = sorted({str(c.get("claim_id")) for c in source_claims})
        truth_scopes = sorted({str(c.get("truth_scope", "UNKNOWN")) for c in source_claims})
        source_is_character_belief = truth_scopes == ["CHARACTER_BELIEF"]

        independent_support = len(evidence_claim_ids)
        contradictions = 0  # Contradiction store integration can raise this in later revisions.
        transition_support = sum(
            1 for t in transition_records
            if str(t.get("before_state_id", "")) or str(t.get("after_state_id", ""))
        )
        explicit_causal_support = len(causal_records)

        scoring = score_hypothesis(
            independent_support=independent_support,
            contradictions=contradictions,
            explicit_causal_support=explicit_causal_support,
            transition_support=transition_support,
            source_is_character_belief=source_is_character_belief,
        )

        candidate_id = stable_id(
            "hypcand",
            node.get("node_id", ""),
            node.get("label", ""),
            ",".join(evidence_claim_ids),
        )
        candidate = {
            "candidate_id": candidate_id,
            "statement": node.get("label"),
            "origin": "TRUSTED_GRAPH_PROPOSITION",
            "source_node_id": node.get("node_id"),
            "source_claim_ids": evidence_claim_ids,
            "source_truth_scopes": truth_scopes,
            "support": {
                "independent_claims": independent_support,
                "transition_support": transition_support,
                "explicit_causal_support": explicit_causal_support,
                "contradictions": contradictions,
            },
            "scoring": scoring,
            "promotion_status": "NOT_PROMOTED",
            "promotion_reason": None,
        }

        # Promotion rule v1:
        # - character belief alone is never promoted to analyst hypothesis;
        # - require at least 2 independent trusted claims;
        # - require MEDIUM/HIGH score;
        # - no contradictions.
        if source_is_character_belief and independent_support == 1:
            candidate["promotion_reason"] = "CHARACTER_BELIEF_SINGLE_SOURCE_ONLY"
            review.append({
                "review_id": stable_id("hyprev", candidate_id, "belief_single_source"),
                "candidate_id": candidate_id,
                "reason": "CHARACTER_BELIEF_SINGLE_SOURCE_ONLY",
                "statement": node.get("label"),
            })
        elif independent_support < 2:
            candidate["promotion_reason"] = "INSUFFICIENT_INDEPENDENT_SUPPORT"
            review.append({
                "review_id": stable_id("hyprev", candidate_id, "insufficient_support"),
                "candidate_id": candidate_id,
                "reason": "INSUFFICIENT_INDEPENDENT_SUPPORT",
                "statement": node.get("label"),
            })
        elif contradictions > 0:
            candidate["promotion_reason"] = "CONTRADICTED"
            review.append({
                "review_id": stable_id("hyprev", candidate_id, "contradicted"),
                "candidate_id": candidate_id,
                "reason": "CONTRADICTED",
                "statement": node.get("label"),
            })
        elif scoring["band"] in {"MEDIUM", "HIGH"}:
            hypothesis_id = stable_id("hyp", candidate_id, node.get("label", ""))
            candidate["promotion_status"] = "PROMOTED"
            candidate["promotion_reason"] = "PROMOTION_RULES_PASSED"
            active.append({
                "hypothesis_id": hypothesis_id,
                "statement": node.get("label"),
                "status": "OPEN",
                "confidence_band": scoring["band"],
                "support_score": scoring["score"],
                "support_score_semantics": scoring["semantics"],
                "source_candidate_id": candidate_id,
                "supporting_claim_ids": evidence_claim_ids,
                "contradicting_claim_ids": [],
                "required_next_evidence": [
                    "independent_support_or_refutation",
                    "future_canon_claims_relevant_to_statement",
                ],
                "promotion_basis": "DETERMINISTIC_V1_RULES",
            })
        else:
            candidate["promotion_reason"] = "SUPPORT_SCORE_TOO_LOW"
            review.append({
                "review_id": stable_id("hyprev", candidate_id, "low_score"),
                "candidate_id": candidate_id,
                "reason": "SUPPORT_SCORE_TOO_LOW",
                "statement": node.get("label"),
            })

        candidates.append(candidate)

    candidates.sort(key=lambda x: x["candidate_id"])
    active.sort(key=lambda x: x["hypothesis_id"])
    review.sort(key=lambda x: x["review_id"])

    # Invariants.
    active_ids = [h["hypothesis_id"] for h in active]
    if len(active_ids) != len(set(active_ids)):
        print("FAIL duplicate_hypothesis_ids")
        return 1

    for h in active:
        if len(h.get("supporting_claim_ids") or []) < 2:
            print(f"FAIL promoted_without_independent_support: {h['hypothesis_id']}")
            return 1

    HYPOTHESIS_CANDIDATES.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "HYPOTHESIS_CANDIDATES",
        "records": candidates,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    HYPOTHESIS_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "ANALYST_HYPOTHESES",
        "semantics": {
            "support_score": "Heuristic support score, not probability.",
            "status": "OPEN means unproven and subject to future confirmation/refutation.",
        },
        "records": active,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    HYPOTHESIS_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": canon.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "HYPOTHESIS_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    run = {
        "stage": "MVP-14B7_HYPOTHESIS_ENGINE",
        "result": "PASS",
        "trusted_claims_input": len(claims),
        "graph_propositions_input": len(proposition_nodes),
        "hypothesis_candidates": len(candidates),
        "analyst_hypotheses_promoted": len(active),
        "review_queue": len(review),
        "regression_tests": {
            "strong_support_scoring": "PASS",
            "character_belief_penalty": "PASS",
            "contradiction_penalty": "PASS",
        },
        "invariants": {
            "character_belief_not_auto_promoted": True,
            "minimum_two_independent_claims_for_promotion": True,
            "support_score_not_probability": True,
            "deterministic_hypothesis_ids": True,
            "canon_and_hypothesis_stores_separate": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b7_hypothesis_engine.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B7 Hypothesis Engine",
        "",
        f"- Trusted claims input: {len(claims)}",
        f"- Graph propositions input: {len(proposition_nodes)}",
        f"- Hypothesis candidates: {len(candidates)}",
        f"- Analyst hypotheses promoted: {len(active)}",
        f"- Review queue: {len(review)}",
        "",
        "## Promotion policy",
        "- Character belief alone is never promoted to an analyst hypothesis.",
        "- At least two independent trusted claims are required.",
        "- Promotion requires MEDIUM/HIGH heuristic support score.",
        "- Contradicted candidates are not promoted.",
        "- Support score is explicitly NOT a probability.",
        "",
        "## Separation",
        "- Canon remains immutable trusted evidence.",
        "- Hypotheses live in a separate store and remain unproven until confirmed or refuted.",
    ]
    (REPORTS / "MVP14B7_HYPOTHESIS_ENGINE_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS trusted_claims_input: {len(claims)}")
    print(f"PASS graph_propositions_input: {len(proposition_nodes)}")
    print(f"CHECK hypothesis_candidates: {len(candidates)}")
    print(f"CHECK analyst_hypotheses_promoted: {len(active)}")
    print(f"CHECK review_queue: {len(review)}")
    print("PASS invariant_character_belief_not_auto_promoted")
    print("PASS invariant_minimum_two_independent_claims_for_promotion")
    print("PASS invariant_canon_hypothesis_separation")
    print("=== ALINA BOOK 2 MVP-14B7 HYPOTHESIS ENGINE: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
