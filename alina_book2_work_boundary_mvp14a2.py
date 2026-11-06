from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
STRUCTURE = PROJECT / "structure"
SOURCES = PROJECT / "sources"
RUNS = PROJECT / "runs"


def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14A2 WORK BOUNDARY RESOLVER ===")

    candidates_path = STRUCTURE / "structure_candidates.json"
    chapters_path = STRUCTURE / "chapters.json"
    source_text_path = SOURCES / "source_extracted.txt"

    if not candidates_path.exists() or not chapters_path.exists() or not source_text_path.exists():
        print("FAIL required_structure_artifacts_missing")
        return 1

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    chapters = json.loads(chapters_path.read_text(encoding="utf-8"))
    paragraphs = [p for p in source_text_path.read_text(encoding="utf-8").split("\n\n") if p.strip()]

    primary_title = None
    primary_start = 0
    secondary_candidates = []

    for item in candidates:
        style = (item.get("style") or "").casefold()
        text = item.get("text", "").strip()
        if item.get("paragraph") == 0 and "heading1" in style:
            primary_title = text
            continue
        if "heading2" in style:
            if re.match(r"^часть\s+\d+", text, flags=re.I):
                continue
            secondary_candidates.append(item)

    if not primary_title:
        print("FAIL primary_work_title_not_found")
        return 1

    if not secondary_candidates:
        print("FAIL secondary_work_boundary_not_found")
        return 1

    first_secondary = min(secondary_candidates, key=lambda x: x["paragraph"])
    primary_end = first_secondary["paragraph"] - 1

    works = [
        {
            "work_id": "sto_let_tomu_vpered",
            "title": primary_title,
            "start_paragraph": primary_start,
            "end_paragraph": primary_end,
            "paragraph_count": primary_end - primary_start + 1,
            "status": "PRIMARY_SELECTED",
            "boundary_evidence": {
                "next_work_paragraph": first_secondary["paragraph"],
                "next_work_title": first_secondary["text"],
                "next_work_style": first_secondary.get("style")
            }
        },
        {
            "work_id": "plenniki_asteroida",
            "title": first_secondary["text"],
            "start_paragraph": first_secondary["paragraph"],
            "end_paragraph": len(paragraphs) - 1,
            "paragraph_count": len(paragraphs) - first_secondary["paragraph"],
            "status": "DETECTED_NOT_SELECTED"
        }
    ]

    (STRUCTURE / "work_boundaries.json").write_text(
        json.dumps(works, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Build primary-work chunk index and local chunk files.
    target_chars = 7000
    subset = paragraphs[primary_start:primary_end + 1]
    chunks = []
    buf = []
    start_abs = primary_start
    chars = 0

    def flush(end_abs: int):
        nonlocal buf, start_abs, chars
        if not buf:
            return
        text = "\n\n".join(buf)
        chunks.append({
            "chunk_id": f"primary-{len(chunks)+1:04d}",
            "work_id": "sto_let_tomu_vpered",
            "start_paragraph": start_abs,
            "end_paragraph": end_abs,
            "char_count": len(text),
            "text": text
        })
        buf = []
        chars = 0

    for rel_idx, p in enumerate(subset):
        abs_idx = primary_start + rel_idx
        if not buf:
            start_abs = abs_idx
        projected = chars + len(p) + 2
        if buf and projected > target_chars:
            flush(abs_idx - 1)
            start_abs = abs_idx
        buf.append(p)
        chars += len(p) + 2
    flush(primary_end)

    out_dir = SOURCES / "work_chunks" / "sto_let_tomu_vpered"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.txt"):
        old.unlink()
    for item in chunks:
        (out_dir / f"{item['chunk_id']}.txt").write_text(item["text"], encoding="utf-8")

    index = [{k:v for k,v in item.items() if k != "text"} for item in chunks]
    (STRUCTURE / "primary_work_chunk_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    RUNS.mkdir(parents=True, exist_ok=True)
    run = {
        "stage": "MVP-14A2_WORK_BOUNDARY_RESOLVER",
        "result": "PASS",
        "primary_work": "sto_let_tomu_vpered",
        "primary_title": primary_title,
        "primary_start_paragraph": primary_start,
        "primary_end_paragraph": primary_end,
        "primary_chunk_count": len(chunks),
        "secondary_work_title": first_secondary["text"],
        "secondary_work_start_paragraph": first_secondary["paragraph"]
    }
    (RUNS / "mvp14a2_work_boundary.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"PASS primary_work: {primary_title}")
    print(f"PASS primary_range: {primary_start}..{primary_end}")
    print(f"PASS secondary_work_detected: {first_secondary['text']} @ {first_secondary['paragraph']}")
    print(f"PASS primary_chunks_built: {len(chunks)}")
    print("=== ALINA BOOK 2 MVP-14A2 WORK BOUNDARY: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
