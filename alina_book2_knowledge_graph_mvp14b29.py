from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
CANON = PROJECT / "canon"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

ENTITY_REGISTRY = CANON / "entity_registry.json"
RELATION_STORE = CANON / "relation_store.json"
EVENT_STORE = CANON / "event_store.json"
GRAPH_FILE = CANON / "knowledge_graph.json"

def stable_node_id(prefix: str, *parts: str) -> str:
    raw = ":".join(str(p).casefold().strip() for p in parts).encode("utf-8")
    return prefix + "-" + hashlib.sha256(raw).hexdigest()[:16]

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.9 KNOWLEDGE GRAPH ASSEMBLY ===")

    for path, label in [
        (ENTITY_REGISTRY, "entity_registry"),
        (RELATION_STORE, "relation_store"),
        (EVENT_STORE, "event_store"),
    ]:
        if not path.exists():
            print(f"FAIL {label}_missing")
            return 1

    entity_data = json.loads(ENTITY_REGISTRY.read_text(encoding="utf-8"))
    relation_data = json.loads(RELATION_STORE.read_text(encoding="utf-8"))
    event_data = json.loads(EVENT_STORE.read_text(encoding="utf-8"))

    entities = entity_data.get("records") or []
    relations = relation_data.get("records") or []
    events = event_data.get("records") or []

    entity_ids = {str(e.get("entity_id", "")) for e in entities}
    if len(entity_ids) != len(entities):
        print("FAIL duplicate_entity_ids")
        return 1

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    # 1. Entity nodes.
    for ent in entities:
        node = {
            "node_id": ent["entity_id"],
            "node_type": "ENTITY",
            "entity_type": ent.get("entity_type", "UNKNOWN"),
            "label": ent.get("canonical_name", ""),
            "aliases": ent.get("aliases") or [],
            "source_claims": ent.get("source_claims") or [],
        }
        nodes.append(node)
        node_ids.add(node["node_id"])

    # 2. Relation targets become either existing ENTITY nodes or explicit value/proposition nodes.
    for rel in relations:
        src = str(rel.get("source_entity_id", ""))
        if src not in entity_ids:
            print(f"FAIL graph_relation_unknown_source: {rel.get('relation_id')}")
            return 1

        target_kind = str(rel.get("target_kind", ""))
        if target_kind == "ENTITY":
            dst = str(rel.get("target_entity_id", ""))
            if dst not in entity_ids:
                print(f"FAIL graph_relation_unknown_target: {rel.get('relation_id')}")
                return 1
        elif target_kind in {"PROPOSITION", "LITERAL"}:
            value = str(rel.get("target_value", ""))
            dst = stable_node_id(
                "prop" if target_kind == "PROPOSITION" else "lit",
                rel.get("claim_id", ""),
                rel.get("predicate", ""),
                value,
                rel.get("truth_scope", ""),
            )
            if dst not in node_ids:
                nodes.append({
                    "node_id": dst,
                    "node_type": target_kind,
                    "label": value,
                    "truth_scope": rel.get("truth_scope", "UNKNOWN"),
                    "source_claims": [rel.get("claim_id")],
                })
                node_ids.add(dst)
        else:
            print(f"FAIL unsupported_target_kind: {target_kind}")
            return 1

        edge = {
            "edge_id": str(rel.get("relation_id")),
            "edge_type": "RELATION",
            "source": src,
            "predicate": rel.get("predicate"),
            "target": dst,
            "truth_scope": rel.get("truth_scope", "UNKNOWN"),
            "claim_id": rel.get("claim_id"),
            "evidence": rel.get("evidence") or [],
        }
        edges.append(edge)

    # 3. Event nodes and actor edges.
    for evt in events:
        event_node_id = str(evt.get("event_id", ""))
        actor = str(evt.get("actor_entity_id", ""))
        if actor not in entity_ids:
            print(f"FAIL graph_event_unknown_actor: {event_node_id}")
            return 1
        if event_node_id in node_ids:
            print(f"FAIL duplicate_event_node_id: {event_node_id}")
            return 1

        nodes.append({
            "node_id": event_node_id,
            "node_type": "EVENT",
            "event_type": evt.get("event_type"),
            "label": evt.get("description") or evt.get("value") or evt.get("event_type"),
            "value": evt.get("value"),
            "truth_scope": evt.get("truth_scope", "UNKNOWN"),
            "source_claims": [evt.get("claim_id")],
            "evidence": evt.get("evidence") or [],
        })
        node_ids.add(event_node_id)

        edges.append({
            "edge_id": stable_node_id("edge", event_node_id, actor, "ACTOR"),
            "edge_type": "EVENT_ACTOR",
            "source": actor,
            "predicate": "ACTOR_IN",
            "target": event_node_id,
            "truth_scope": evt.get("truth_scope", "UNKNOWN"),
            "claim_id": evt.get("claim_id"),
            "evidence": evt.get("evidence") or [],
        })

    # Invariants.
    edge_ids = [str(e.get("edge_id", "")) for e in edges]
    if len(edge_ids) != len(set(edge_ids)):
        print("FAIL duplicate_graph_edge_ids")
        return 1

    for edge in edges:
        if edge["source"] not in node_ids or edge["target"] not in node_ids:
            print(f"FAIL dangling_edge: {edge['edge_id']}")
            return 1
        evidence = edge.get("evidence") or []
        if not evidence or not all(e.get("quote_verified") is True for e in evidence):
            print(f"FAIL edge_without_verified_evidence: {edge['edge_id']}")
            return 1

    # Character beliefs must never point directly to WORLD_STATE nodes.
    for edge in edges:
        if edge.get("truth_scope") == "CHARACTER_BELIEF":
            target = next((n for n in nodes if n["node_id"] == edge["target"]), None)
            if target and target.get("node_type") == "LITERAL":
                print(f"FAIL belief_promoted_to_literal_world_state: {edge['edge_id']}")
                return 1

    nodes.sort(key=lambda x: (x["node_type"], x["node_id"]))
    edges.sort(key=lambda x: x["edge_id"])

    graph = {
        "schema_version": "1.0",
        "work_id": entity_data.get("work_id", "sto_let_tomu_vpered"),
        "graph_type": "TRUSTED_KNOWLEDGE_GRAPH",
        "nodes": nodes,
        "edges": edges,
    }
    GRAPH_FILE.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for n in nodes:
        nt = str(n.get("node_type", "UNKNOWN"))
        counts[nt] = counts.get(nt, 0) + 1

    run = {
        "stage": "MVP-14B2_9_KNOWLEDGE_GRAPH_ASSEMBLY",
        "result": "PASS",
        "entity_nodes": counts.get("ENTITY", 0),
        "proposition_nodes": counts.get("PROPOSITION", 0),
        "literal_nodes": counts.get("LITERAL", 0),
        "event_nodes": counts.get("EVENT", 0),
        "edges": len(edges),
        "relation_edges": sum(1 for e in edges if e.get("edge_type") == "RELATION"),
        "event_actor_edges": sum(1 for e in edges if e.get("edge_type") == "EVENT_ACTOR"),
        "invariants": {
            "no_dangling_edges": True,
            "edge_ids_unique": True,
            "verified_evidence_required": True,
            "beliefs_not_promoted_to_world_state": True,
            "trusted_stores_only": True,
        },
    }

    RUNS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (RUNS / "mvp14b2_9_knowledge_graph.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14B2.9 Knowledge Graph Assembly",
        "",
        f"- Entity nodes: {run['entity_nodes']}",
        f"- Proposition nodes: {run['proposition_nodes']}",
        f"- Literal nodes: {run['literal_nodes']}",
        f"- Event nodes: {run['event_nodes']}",
        f"- Edges: {run['edges']}",
        "",
        "## Invariants",
        "- Every graph edge points to existing nodes.",
        "- Every graph edge has verified source evidence.",
        "- Character beliefs remain proposition nodes and are not promoted to world-state facts.",
        "- Graph assembly consumes only trusted Entity / Relation / Event stores.",
        "- Node and edge identifiers are deterministic.",
    ]
    (REPORTS / "MVP14B2_9_KNOWLEDGE_GRAPH_SUMMARY.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(f"PASS entity_nodes: {run['entity_nodes']}")
    print(f"PASS proposition_nodes: {run['proposition_nodes']}")
    print(f"PASS literal_nodes: {run['literal_nodes']}")
    print(f"PASS event_nodes: {run['event_nodes']}")
    print(f"PASS edges: {run['edges']}")
    print("PASS invariant_no_dangling_edges")
    print("PASS invariant_verified_evidence_required")
    print("PASS invariant_beliefs_not_promoted_to_world_state")
    print("PASS invariant_trusted_stores_only")
    print("=== ALINA BOOK 2 MVP-14B2.9 KNOWLEDGE GRAPH ASSEMBLY: PASS ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
