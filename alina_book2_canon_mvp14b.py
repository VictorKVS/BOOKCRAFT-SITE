from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
SOURCES = PROJECT / "sources"
STRUCTURE = PROJECT / "structure"
STATE = PROJECT / "state"
EVIDENCE = PROJECT / "evidence"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

MODEL = os.environ.get("ALINA_CANON_MODEL", "qwen2.5:7b")
OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MAX_CHUNKS = int(os.environ.get("ALINA_MAX_CHUNKS", "0"))


SYSTEM = """You are ALINA Analyst. Extract canon only from the provided source chunk.
Never invent missing facts. Separate confirmed source facts from hypotheses.
Return STRICT JSON only, no markdown.
Schema:
{
  "characters": [{"name":"","aliases":[],"facts":[],"appearance":[],"traits":[],"knowledge":[],"goals":[],"relationships":[],"evidence":[]}],
  "locations": [{"name":"","facts":[],"evidence":[]}],
  "objects": [{"name":"","facts":[],"evidence":[]}],
  "events": [{"event":"","participants":[],"location":"","causes":[],"consequences":[],"evidence":[]}],
  "world_rules": [{"rule":"","evidence":[]}],
  "unresolved": [{"question":"","reason":""}]
}
Evidence entries must be short direct snippets copied from this chunk, max 20 words each.
Do not infer film/TV canon. This is literary source analysis only.
"""


def ollama_available() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def call_ollama(prompt: str) -> Dict[str, Any]:
    body = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.1}
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        payload = json.loads(r.read().decode("utf-8"))
    content = payload["message"]["content"]
    return json.loads(content)


def normalize_name(s: str) -> str:
    return " ".join((s or "").split()).strip()


def merge_unique_list(dst: List[Any], src: List[Any]) -> None:
    seen = {json.dumps(x, ensure_ascii=False, sort_keys=True) for x in dst}
    for x in src:
        k = json.dumps(x, ensure_ascii=False, sort_keys=True)
        if k not in seen:
            dst.append(x)
            seen.add(k)


def merge_by_name(items: List[Dict[str, Any]], key="name") -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for item in items:
        name = normalize_name(item.get(key, ""))
        if not name:
            continue
        nk = name.casefold()
        if nk not in merged:
            merged[nk] = {key: name}
        target = merged[nk]
        for k, v in item.items():
            if k == key:
                continue
            if isinstance(v, list):
                target.setdefault(k, [])
                merge_unique_list(target[k], v)
            elif v not in ("", None, [], {}):
                target.setdefault(k, v)
    return list(merged.values())


def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B SEMANTIC CANON ANALYZER ===")

    if not ollama_available():
        print(f"FAIL ollama_not_available: {OLLAMA}")
        return 1
    print(f"PASS ollama_available: {OLLAMA}")
    print(f"MODEL: {MODEL}")

    chunk_index_path = STRUCTURE / "chunk_index.json"
    if not chunk_index_path.exists():
        print("FAIL chunk_index_missing")
        return 1

    index = json.loads(chunk_index_path.read_text(encoding="utf-8"))
    if MAX_CHUNKS > 0:
        index = index[:MAX_CHUNKS]
        print(f"MODE: LIMITED {len(index)} chunks")
    else:
        print(f"MODE: FULL {len(index)} chunks")

    for d in (STATE, EVIDENCE, REPORTS, RUNS):
        d.mkdir(parents=True, exist_ok=True)

    partial_dir = EVIDENCE / "chunk_analysis"
    partial_dir.mkdir(parents=True, exist_ok=True)

    all_characters, all_locations, all_objects = [], [], []
    all_events, all_rules, all_unresolved = [], [], []
    completed = 0

    for i, meta in enumerate(index, 1):
        chunk_id = meta["chunk_id"]
        chunk_path = SOURCES / "chunks" / f"{chunk_id}.txt"
        out_path = partial_dir / f"{chunk_id}.json"

        if out_path.exists():
            data = json.loads(out_path.read_text(encoding="utf-8"))
            print(f"[{i}/{len(index)}] REUSE {chunk_id}")
        else:
            text = chunk_path.read_text(encoding="utf-8")
            prompt = f"""SOURCE CHUNK ID: {chunk_id}
PARAGRAPHS: {meta['start_paragraph']}..{meta['end_paragraph']}

{text}
"""
            print(f"[{i}/{len(index)}] ANALYZE {chunk_id}")
            try:
                data = call_ollama(prompt)
            except Exception as e:
                print(f"FAIL chunk_analysis {chunk_id}: {e}")
                return 1
            out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        all_characters.extend(data.get("characters", []))
        all_locations.extend(data.get("locations", []))
        all_objects.extend(data.get("objects", []))
        all_events.extend(data.get("events", []))
        all_rules.extend(data.get("world_rules", []))
        all_unresolved.extend(data.get("unresolved", []))
        completed += 1

    state = {
        "schema_version": "1.0",
        "project_id": "sto_let_tomu_vpered",
        "source_type": "literary_canon_only",
        "model": MODEL,
        "chunks_analyzed": completed,
        "characters": merge_by_name(all_characters),
        "locations": merge_by_name(all_locations),
        "objects": merge_by_name(all_objects),
        "events": all_events,
        "world_rules": all_rules,
        "unresolved": all_unresolved,
    }

    (STATE / "literary_canon_raw.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "characters": len(state["characters"]),
        "locations": len(state["locations"]),
        "objects": len(state["objects"]),
        "events": len(state["events"]),
        "world_rules": len(state["world_rules"]),
        "unresolved": len(state["unresolved"]),
        "chunks_analyzed": completed,
        "model": MODEL,
    }
    (RUNS / "mvp14b_semantic_canon.json").write_text(
        json.dumps({"result": "PASS", **summary}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    lines = [
        "# MVP-14B Semantic Canon Analysis",
        "",
        f"- Model: {MODEL}",
        f"- Chunks analyzed: {completed}",
        f"- Characters: {summary['characters']}",
        f"- Locations: {summary['locations']}",
        f"- Objects: {summary['objects']}",
        f"- Events: {summary['events']}",
        f"- World rules: {summary['world_rules']}",
        f"- Unresolved: {summary['unresolved']}",
        "",
        "Status: PASS for raw literary canon extraction.",
        "",
        "Note: this output is not yet final canon acceptance. MVP-14C must reconcile aliases, contradictions, timeline, knowledge state and user-locked cultural canon."
    ]
    (REPORTS / "MVP14B_SEMANTIC_CANON_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"PASS chunks_analyzed: {completed}")
    print(f"PASS characters_extracted: {summary['characters']}")
    print(f"PASS locations_extracted: {summary['locations']}")
    print(f"PASS objects_extracted: {summary['objects']}")
    print(f"PASS events_extracted: {summary['events']}")
    print(f"PASS world_rules_extracted: {summary['world_rules']}")
    print("PASS literary_canon_raw_written")
    print("=== ALINA BOOK 2 MVP-14B SEMANTIC CANON ANALYZER: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
