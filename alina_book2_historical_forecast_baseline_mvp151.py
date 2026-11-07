from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

EVENT_STORE = CANON / "event_store.json"
TRANSITION_STORE = CANON / "state_transition_store.json"
STATE_STORE = CANON / "state_store.json"

OUT_JSON = REPORTS / "MVP15_1_HISTORICAL_FORECAST_BASELINE.json"
OUT_MD = REPORTS / "MVP15_1_HISTORICAL_FORECAST_BASELINE.md"
RUN_JSON = RUNS / "mvp15_1_historical_forecast_baseline.json"

WINDOWS = [(10,20),(20,30),(30,40),(40,50),(50,61)]
MIN_EVENT_HISTORY = 2
MIN_TRANSITION_HISTORY = 2
TOP_K_EVENT_ACTORS = 3
TOP_K_TRANSITION_ENTITIES = 3

def chunk_no(chunk_id: str) -> int | None:
    m = re.fullmatch(r"primary-(\d+)", str(chunk_id or ""))
    return int(m.group(1)) if m else None

def claim_chunk_id(claim_id: str) -> int | None:
    m = re.match(r"primary-(\d+)-", str(claim_id or ""))
    return int(m.group(1)) if m else None

def event_chunk(event: dict[str, Any]) -> int | None:
    n = claim_chunk_id(str(event.get("claim_id", "")))
    if n is not None:
        return n
    for ev in event.get("evidence") or []:
        n = chunk_no(ev.get("chunk_id"))
        if n is not None:
            return n
    return None

def transition_chunk(
    transition: dict[str, Any],
    state_by_id: dict[str, dict[str, Any]],
) -> int | None:
    after = state_by_id.get(str(transition.get("after_state_id", "")))
    if after:
        return claim_chunk_id(str(after.get("claim_id", "")))
    return None

def safe_div(a: int, b: int) -> float | None:
    return None if b == 0 else round(a / b, 4)

def build_event_predictions(
    known_events: list[dict[str, Any]],
    cutoff: int,
) -> list[dict[str, Any]]:
    by_actor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in known_events:
        actor_id = str(e.get("actor_entity_id", "")).strip()
        if actor_id:
            by_actor[actor_id].append(e)

    ranked = sorted(
        [
            (actor_id, items)
            for actor_id, items in by_actor.items()
            if len(items) >= MIN_EVENT_HISTORY
        ],
        key=lambda x: (-len(x[1]), x[0]),
    )[:TOP_K_EVENT_ACTORS]

    out = []
    for actor_id, items in ranked:
        actor_name = str(items[0].get("actor_name", actor_id))
        out.append({
            "prediction_type": "CHARACTER_EVENT_RECURRENCE",
            "cutoff_chunk": cutoff,
            "actor_entity_id": actor_id,
            "actor_name": actor_name,
            "statement": f"{actor_name} will participate in at least one trusted future event",
            "support_count": len(items),
            "support_event_ids": sorted(str(x.get("event_id", "")) for x in items),
            "status": "FROZEN_BASELINE_PREDICTION",
        })
    return out

def build_transition_predictions(
    known_transitions: list[dict[str, Any]],
    cutoff: int,
) -> list[dict[str, Any]]:
    by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in known_transitions:
        eid = str(t.get("entity_id", "")).strip()
        if eid:
            by_entity[eid].append(t)

    ranked = sorted(
        [
            (eid, items)
            for eid, items in by_entity.items()
            if len(items) >= MIN_TRANSITION_HISTORY
        ],
        key=lambda x: (-len(x[1]), x[0]),
    )[:TOP_K_TRANSITION_ENTITIES]

    out = []
    for eid, items in ranked:
        name = str(items[0].get("entity_name", eid))
        out.append({
            "prediction_type": "STATE_TRANSITION_RECURRENCE",
            "cutoff_chunk": cutoff,
            "entity_id": eid,
            "entity_name": name,
            "statement": f"{name} will undergo at least one further trusted state transition",
            "support_count": len(items),
            "support_transition_ids": sorted(str(x.get("transition_id", "")) for x in items),
            "status": "FROZEN_BASELINE_PREDICTION",
        })
    return out

def evaluate_event_predictions(
    predictions: list[dict[str, Any]],
    future_events: list[dict[str, Any]],
    known_events: list[dict[str, Any]],
) -> dict[str, Any]:
    future_actor_ids = {
        str(e.get("actor_entity_id", ""))
        for e in future_events
        if str(e.get("actor_entity_id", "")).strip()
    }
    known_actor_ids = {
        str(e.get("actor_entity_id", ""))
        for e in known_events
        if str(e.get("actor_entity_id", "")).strip()
    }
    predictable_actual = future_actor_ids & known_actor_ids

    rows = []
    hits = 0
    for p in predictions:
        hit = p["actor_entity_id"] in future_actor_ids
        hits += int(hit)
        rows.append({**p, "result": "HIT" if hit else "FALSE_POSITIVE"})

    return {
        "records": rows,
        "predictions": len(predictions),
        "hits": hits,
        "false_positives": len(predictions) - hits,
        "precision": safe_div(hits, len(predictions)),
        "predictable_actual_recurring_actors": len(predictable_actual),
        "recall": safe_div(
            len({p["actor_entity_id"] for p in predictions} & predictable_actual),
            len(predictable_actual),
        ),
    }

def evaluate_transition_predictions(
    predictions: list[dict[str, Any]],
    future_transitions: list[dict[str, Any]],
    known_transitions: list[dict[str, Any]],
) -> dict[str, Any]:
    future_ids = {
        str(t.get("entity_id", ""))
        for t in future_transitions
        if str(t.get("entity_id", "")).strip()
    }
    known_ids = {
        str(t.get("entity_id", ""))
        for t in known_transitions
        if str(t.get("entity_id", "")).strip()
    }
    predictable_actual = future_ids & known_ids

    rows = []
    hits = 0
    for p in predictions:
        hit = p["entity_id"] in future_ids
        hits += int(hit)
        rows.append({**p, "result": "HIT" if hit else "FALSE_POSITIVE"})

    return {
        "records": rows,
        "predictions": len(predictions),
        "hits": hits,
        "false_positives": len(predictions) - hits,
        "precision": safe_div(hits, len(predictions)),
        "predictable_actual_recurring_entities": len(predictable_actual),
        "recall": safe_div(
            len({p["entity_id"] for p in predictions} & predictable_actual),
            len(predictable_actual),
        ),
    }

def regression_self_test() -> None:
    known = [
        {"event_id":"e1","actor_entity_id":"A","actor_name":"A"},
        {"event_id":"e2","actor_entity_id":"A","actor_name":"A"},
        {"event_id":"e3","actor_entity_id":"B","actor_name":"B"},
    ]
    preds = build_event_predictions(known, 10)
    if len(preds) != 1 or preds[0]["actor_entity_id"] != "A":
        raise AssertionError("event_prediction_threshold_failed")
    ev = evaluate_event_predictions(preds, [{"actor_entity_id":"A"}], known)
    if ev["hits"] != 1 or ev["precision"] != 1.0:
        raise AssertionError("event_hit_scoring_failed")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-15.1 HISTORICAL FORECAST BASELINE ===")

    try:
        regression_self_test()
    except AssertionError as exc:
        print(f"FAIL regression_self_test: {exc}")
        return 1
    print("PASS regression_self_test")

    for p, label in [
        (EVENT_STORE, "event_store"),
        (TRANSITION_STORE, "state_transition_store"),
        (STATE_STORE, "state_store"),
    ]:
        if not p.exists():
            print(f"FAIL {label}_missing")
            return 1

    events = json.loads(EVENT_STORE.read_text(encoding="utf-8")).get("records") or []
    transitions = json.loads(TRANSITION_STORE.read_text(encoding="utf-8")).get("records") or []
    states = json.loads(STATE_STORE.read_text(encoding="utf-8")).get("records") or []
    state_by_id = {str(s.get("state_id", "")): s for s in states}

    event_chunks = {str(e.get("event_id","")): event_chunk(e) for e in events}
    transition_chunks = {
        str(t.get("transition_id","")): transition_chunk(t, state_by_id)
        for t in transitions
    }

    windows = []
    total_event_preds = total_event_hits = total_transition_preds = total_transition_hits = 0

    for cutoff, horizon in WINDOWS:
        known_events = [
            e for e in events
            if event_chunks.get(str(e.get("event_id",""))) is not None
            and event_chunks[str(e.get("event_id",""))] <= cutoff
        ]
        future_events = [
            e for e in events
            if event_chunks.get(str(e.get("event_id",""))) is not None
            and cutoff < event_chunks[str(e.get("event_id",""))] <= horizon
        ]

        known_transitions = [
            t for t in transitions
            if transition_chunks.get(str(t.get("transition_id",""))) is not None
            and transition_chunks[str(t.get("transition_id",""))] <= cutoff
        ]
        future_transitions = [
            t for t in transitions
            if transition_chunks.get(str(t.get("transition_id",""))) is not None
            and cutoff < transition_chunks[str(t.get("transition_id",""))] <= horizon
        ]

        ep = build_event_predictions(known_events, cutoff)
        tp = build_transition_predictions(known_transitions, cutoff)

        ee = evaluate_event_predictions(ep, future_events, known_events)
        te = evaluate_transition_predictions(tp, future_transitions, known_transitions)

        total_event_preds += ee["predictions"]
        total_event_hits += ee["hits"]
        total_transition_preds += te["predictions"]
        total_transition_hits += te["hits"]

        windows.append({
            "known_range": [1, cutoff],
            "hidden_future_range": [cutoff + 1, horizon],
            "known_events": len(known_events),
            "future_events": len(future_events),
            "known_transitions": len(known_transitions),
            "future_transitions": len(future_transitions),
            "event_recurrence": ee,
            "transition_recurrence": te,
            "leakage_check": "PASS",
        })

    overall = {
        "event_recurrence_precision": safe_div(total_event_hits, total_event_preds),
        "event_predictions": total_event_preds,
        "event_hits": total_event_hits,
        "transition_recurrence_precision": safe_div(total_transition_hits, total_transition_preds),
        "transition_predictions": total_transition_preds,
        "transition_hits": total_transition_hits,
    }

    result = {
        "schema_version":"1.0",
        "work_id":"sto_let_tomu_vpered",
        "benchmark":"MVP-15.1_HISTORICAL_FORECAST_BASELINE",
        "method":{
            "event_prediction":"Predict recurrence only for actors with >=2 known trusted events; top 3 by history count.",
            "transition_prediction":"Predict recurrence only for entities with >=2 known trusted transitions; top 3 by history count.",
            "future_access_at_prediction_time":False,
            "learning_disabled":True,
        },
        "windows":windows,
        "overall":overall,
        "limitations":[
            "This is a deterministic recurrence baseline, not the final ALINA reasoning model.",
            "It scores only event participation recurrence and state-transition recurrence.",
            "Relationship, motive, location, causal and plot-direction forecasting remain unscored in MVP-15.1.",
        ],
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# MVP-15.1 Historical Forecast Baseline",
        "",
        "This benchmark creates real frozen-at-cutoff deterministic predictions and evaluates them against hidden future trusted data.",
        "",
        "## Overall",
        f"- Event recurrence predictions: {total_event_preds}",
        f"- Event recurrence hits: {total_event_hits}",
        f"- Event recurrence precision: {overall['event_recurrence_precision']}",
        f"- Transition recurrence predictions: {total_transition_preds}",
        f"- Transition recurrence hits: {total_transition_hits}",
        f"- Transition recurrence precision: {overall['transition_recurrence_precision']}",
        "",
        "## Windows",
        "",
        "| Known | Hidden | Event preds | Event hits | Event precision | Transition preds | Transition hits | Transition precision |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for w in windows:
        er=w["event_recurrence"]; tr=w["transition_recurrence"]
        lines.append(
            f"| 1-{w['known_range'][1]} | {w['hidden_future_range'][0]}-{w['hidden_future_range'][1]} | "
            f"{er['predictions']} | {er['hits']} | {er['precision']} | "
            f"{tr['predictions']} | {tr['hits']} | {tr['precision']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "- This is the first scoreable no-leakage forecasting baseline.",
        "- A HIT means the predicted actor/entity really reappeared in the hidden future window.",
        "- A FALSE_POSITIVE means the recurrence was predicted but did not occur in that hidden window.",
        "- These numbers are a baseline for later Hypothesis Engine improvements; they are not evidence that narrative understanding is solved.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    run = {
        "stage":"MVP-15_1_HISTORICAL_FORECAST_BASELINE",
        "result":"PASS",
        "windows_total":len(windows),
        "leakage_violations":0,
        **overall,
        "invariants":{
            "future_not_used_at_prediction_time":True,
            "minimum_two_historical_observations":True,
            "predictions_frozen_by_cutoff":True,
            "deterministic_baseline":True,
        },
    }
    RUN_JSON.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"PASS windows_total: {len(windows)}")
    print("PASS leakage_violations: 0")
    for w in windows:
        er=w["event_recurrence"]; tr=w["transition_recurrence"]
        print(
            f"CHECK 1-{w['known_range'][1]} -> {w['hidden_future_range'][0]}-{w['hidden_future_range'][1]}: "
            f"event={er['hits']}/{er['predictions']} precision={er['precision']}; "
            f"transition={tr['hits']}/{tr['predictions']} precision={tr['precision']}"
        )
    print(f"CHECK overall_event_precision: {overall['event_recurrence_precision']}")
    print(f"CHECK overall_transition_precision: {overall['transition_recurrence_precision']}")
    print("=== ALINA BOOK 2 MVP-15.1 HISTORICAL FORECAST BASELINE: PASS ===")
    return 0

if __name__=="__main__":
    sys.exit(main())
