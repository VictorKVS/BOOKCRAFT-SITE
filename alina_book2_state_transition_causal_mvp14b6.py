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

STATE_STORE = CANON / "state_store.json"
EVENT_STORE = CANON / "event_store.json"
TEMPORAL_MODEL = CANON / "temporal_model.json"

TRANSITION_STORE = CANON / "state_transition_store.json"
CAUSAL_STORE = CANON / "causal_link_store.json"
TRANSITION_REVIEW = CANON / "state_transition_review_queue.json"

# Only explicit transition verbs are allowed to create a confirmed transition in v1.
TRANSITION_PREDICATES = {
    "становится",
    "стал",
    "стала",
    "стало",
    "изменяется",
    "изменился",
    "изменилась",
    "перешел",
    "перешла",
    "переходит",
    "начинает",
    "начал",
    "начала",
    "прекращает",
    "прекратил",
    "прекратила",
}

# Only explicit causal markers may create a causal link in v1.
CAUSAL_MARKERS = {
    "потому что",
    "из-за",
    "из за",
    "вследствие",
    "поэтому",
    "в результате",
    "привело к",
    "привел к",
    "привела к",
    "вызвало",
    "вызвал",
    "вызвала",
}

def norm(s: str) -> str:
    s = (s or "").casefold().replace("ё", "е")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(prefix: str, *parts: str) -> str:
    raw = ":".join(norm(str(p)) for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def has_any(text: str, markers: set[str]) -> bool:
    t = norm(text)
    return any(m in t for m in markers)

def state_sort_key(s: dict[str, Any]) -> tuple[int, str]:
    return (int(s.get("sequence_index", 10**9)), str(s.get("state_id", "")))

def detect_transitions(states: list[dict[str, Any]], events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    transitions: list[dict[str, Any]] = []
    causal_links: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []

    by_entity: dict[str, list[dict[str, Any]]] = {}
    for s in states:
        by_entity.setdefault(str(s.get("entity_id", "")), []).append(s)

    events_by_actor: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        events_by_actor.setdefault(str(e.get("actor_entity_id", "")), []).append(e)

    for entity_id, seq in by_entity.items():
        seq = sorted(seq, key=state_sort_key)
        if len(seq) < 2:
            continue

        for before, after in zip(seq, seq[1:]):
            # Textual succession is not enough for a transition.
            if before.get("truth_scope") != after.get("truth_scope"):
                continue

            transition_evidence = []
            candidate_event = None

            # Explicit transition language in the later observation.
            if has_any(str(after.get("predicate", "")), TRANSITION_PREDICATES):
                transition_evidence.append("EXPLICIT_TRANSITION_PREDICATE")

            # Event support: actor matches and event position lies between states.
            for evt in events_by_actor.get(entity_id, []):
                event_seq = evt.get("sequence_index")
                if event_seq is None:
                    continue
                if int(before.get("sequence_index", -1)) <= int(event_seq) <= int(after.get("sequence_index", 10**9)):
                    candidate_event = evt
                    transition_evidence.append("TRUSTED_EVENT_BETWEEN_STATES")
                    break

            if not transition_evidence:
                review.append({
                    "review_id": stable_id("transrev", before.get("state_id", ""), after.get("state_id", "")),
                    "entity_id": entity_id,
                    "before_state_id": before.get("state_id"),
                    "after_state_id": after.get("state_id"),
                    "reason": "TEXTUAL_SUCCESSION_WITHOUT_TRANSITION_EVIDENCE",
                    "status": "NOT_CONFIRMED",
                })
                continue

            transition_id = stable_id(
                "transition",
                entity_id,
                before.get("state_id", ""),
                after.get("state_id", ""),
                ",".join(sorted(transition_evidence)),
            )
            transition = {
                "transition_id": transition_id,
                "entity_id": entity_id,
                "entity_name": before.get("entity_name") or after.get("entity_name"),
                "truth_scope": before.get("truth_scope"),
                "before_state_id": before.get("state_id"),
                "after_state_id": after.get("state_id"),
                "before_sequence_index": before.get("sequence_index"),
                "after_sequence_index": after.get("sequence_index"),
                "transition_basis": sorted(set(transition_evidence)),
                "event_id": candidate_event.get("event_id") if candidate_event else None,
                "causality_status": "NOT_ESTABLISHED",
            }
            transitions.append(transition)

            # Causality requires explicit language in trusted evidence.
            causal_text = " ".join(
                str(e.get("quote", ""))
                for e in (before.get("evidence") or []) + (after.get("evidence") or [])
            )
            if candidate_event:
                causal_text += " " + " ".join(str(e.get("quote", "")) for e in candidate_event.get("evidence") or [])

            if has_any(causal_text, CAUSAL_MARKERS):
                causal_links.append({
                    "causal_link_id": stable_id("cause", transition_id, causal_text),
                    "transition_id": transition_id,
                    "cause_event_id": candidate_event.get("event_id") if candidate_event else None,
                    "effect_state_id": after.get("state_id"),
                    "status": "EXPLICIT_CAUSAL_EVIDENCE",
                    "basis": "SOURCE_TEXT_CAUSAL_MARKER",
                })
                transition["causality_status"] = "EXPLICIT_CAUSAL_EVIDENCE"

    transitions.sort(key=lambda x: x["transition_id"])
    causal_links.sort(key=lambda x: x["causal_link_id"])
    review.sort(key=lambda x: x["review_id"])
    return transitions, causal_links, review

def regression_self_test() -> None:
    def state(sid: str, entity: str, seq: int, pred: str, value: str, quote: str, scope: str = "WORLD_STATE"):
        return {
            "state_id": sid,
            "entity_id": entity,
            "entity_name": entity,
            "sequence_index": seq,
            "truth_scope": scope,
            "predicate": pred,
            "value": value,
            "evidence": [{"quote": quote, "quote_verified": True}],
        }

    # 1. Mere textual succession must NOT become a confirmed transition.
    t, c, r = detect_transitions([
        state("s1", "e1", 0, "находится", "дома", "Он дома."),
        state("s2", "e1", 1, "находится", "в саду", "Он в саду."),
    ], [])
    if t or c or len(r) != 1:
        raise AssertionError("false_transition_guard_failed")

    # 2. Explicit transition predicate must create a transition.
    t, c, r = detect_transitions([
        state("s3", "e2", 0, "является", "спокойным", "Он был спокоен."),
        state("s4", "e2", 1, "становится", "взволнованным", "Он становится взволнованным."),
    ], [])
    if len(t) != 1 or c:
        raise AssertionError("explicit_transition_failed")

    # 3. Explicit causal marker may establish causality.
    t, c, r = detect_transitions([
        state("s5", "e3", 0, "является", "сухим", "Пол был сухим."),
        state("s6", "e3", 1, "становится", "мокрым", "Из-за дождя пол становится мокрым."),
    ], [])
    if len(t) != 1 or len(c) != 1:
        raise AssertionError("explicit_causality_failed")

    # 4. Different truth scopes must never become one transition.
    t, c, r = detect_transitions([
        state("s7", "e4", 0, "считает", "А", "Он считает А.", "CHARACTER_BELIEF"),
        state("s8", "e4", 1, "становится", "Б", "Он становится Б.", "WORLD_STATE"),
    ], [])
    if t or c:
        raise AssertionError("truth_scope_transition_guard_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B6 STATE TRANSITION & CAUSAL LAYER ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    for path, label in [
        (STATE_STORE, "state_store"),
        (EVENT_STORE, "event_store"),
        (TEMPORAL_MODEL, "temporal_model"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    state_data = json.loads(STATE_STORE.read_text(encoding="utf-8"))
    event_data = json.loads(EVENT_STORE.read_text(encoding="utf-8"))
    temporal_data = json.loads(TEMPORAL_MODEL.read_text(encoding="utf-8"))

    states = state_data.get("records") or []
    events = event_data.get("records") or []

    # Enrich trusted events with sequence index when resolvable via claim_id.
    timeline_by_claim = {
        str(t.get("claim_id", "")): t
        for t in temporal_data.get("timeline") or []
    }
    enriched_events = []
    for evt in events:
        e = dict(evt)
        t = timeline_by_claim.get(str(evt.get("claim_id", "")))
        e["sequence_index"] = t.get("sequence_index") if t else None
        enriched_events.append(e)

    transitions, causal_links, review = detect_transitions(states, enriched_events)

    state_ids = {str(s.get("state_id", "")) for s in states}
    event_ids = {str(e.get("event_id", "")) for e in enriched_events}

    for tr in transitions:
        if tr["before_state_id"] not in state_ids or tr["after_state_id"] not in state_ids:
            print(f"FAIL dangling_transition_state: {tr['transition_id']}")
            return 1
        if tr.get("event_id") and tr["event_id"] not in event_ids:
            print(f"FAIL dangling_transition_event: {tr['transition_id']}")
            return 1

    transition_ids = {str(t.get("transition_id", "")) for t in transitions}
    for cl in causal_links:
        if cl["transition_id"] not in transition_ids:
            print(f"FAIL causal_link_without_transition: {cl['causal_link_id']}")
            return 1
        if cl.get("cause_event_id") and cl["cause_event_id"] not in event_ids:
            print(f"FAIL causal_link_unknown_event: {cl['causal_link_id']}")
            return 1

    TRANSITION_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": state_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_STATE_TRANSITIONS",
        "semantics": {
            "confirmed_transition": "Requires explicit transition evidence; textual succession alone is insufficient.",
            "causality": "Requires explicit causal evidence; temporal adjacency never proves causality.",
        },
        "records": transitions,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    CAUSAL_STORE.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": state_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "TRUSTED_CAUSAL_LINKS",
        "records": causal_links,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    TRANSITION_REVIEW.write_text(json.dumps({
        "schema_version": "1.0",
        "work_id": state_data.get("work_id", "sto_let_tomu_vpered"),
        "store_type": "STATE_TRANSITION_REVIEW_QUEUE",
        "records": review,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    run = {
        "stage": "MVP-14B6_STATE_TRANSITION_CAUSAL_LAYER",
        "result": "PASS",
        "state_observations_input": len(states),
        "trusted_events_input": len(events),
        "confirmed_transitions": len(transitions),
        "explicit_causal_links": len(causal_links),
        "review_queue": len(review),
        "regression_tests": {
            "false_transition_guard": "PASS",
            "explicit_transition_detection": "PASS",
            "explicit_causality_detection": "PASS",
            "truth_scope_transition_guard": "PASS",
        },
        "invariants": {
            "textual_succession_is_not_transition": True,
            "temporal_adjacency_is_not_causality": True,
            "truth_scopes_not_mixed": True,
            "known_states_only": True,
            "known_events_only": True,
            "deterministic_transition_ids": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b6_state_transition_causal.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B6 State Transition / Causal Layer",
        "",
        f"- State observations input: {len(states)}",
        f"- Trusted events input: {len(events)}",
        f"- Confirmed transitions: {len(transitions)}",
        f"- Explicit causal links: {len(causal_links)}",
        f"- Review queue: {len(review)}",
        "",
        "## Policy",
        "- Textual succession alone never creates a state transition.",
        "- Temporal adjacency alone never creates a causal link.",
        "- A transition requires explicit transition evidence.",
        "- A causal link requires explicit causal evidence.",
        "- CHARACTER_BELIEF and WORLD_STATE are never merged into one transition.",
        "",
        "## Regression tests",
        "- False transition guard: PASS",
        "- Explicit transition detection: PASS",
        "- Explicit causality detection: PASS",
        "- Truth-scope transition guard: PASS",
    ]
    (REPORTS / "MVP14B6_STATE_TRANSITION_CAUSAL_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS state_observations_input: {len(states)}")
    print(f"PASS trusted_events_input: {len(events)}")
    print(f"CHECK confirmed_transitions: {len(transitions)}")
    print(f"CHECK explicit_causal_links: {len(causal_links)}")
    print(f"CHECK review_queue: {len(review)}")
    print("PASS invariant_textual_succession_is_not_transition")
    print("PASS invariant_temporal_adjacency_is_not_causality")
    print("PASS invariant_truth_scopes_not_mixed")
    print("=== ALINA BOOK 2 MVP-14B6 STATE TRANSITION & CAUSAL LAYER: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
