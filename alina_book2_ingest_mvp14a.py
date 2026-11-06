from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
CHAPTER_RE = re.compile(
    r"^(?:часть\s+\d+\.?\s*)?(?:глава\s+)?\d+\.\s+.+$",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_docx_paragraphs(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[dict] = []
    for p in root.iter(W_NS + "p"):
        text = "".join((t.text or "") for t in p.iter(W_NS + "t")).strip()
        if not text:
            continue
        style = None
        ppr = p.find(W_NS + "pPr")
        if ppr is not None:
            pstyle = ppr.find(W_NS + "pStyle")
            if pstyle is not None:
                style = pstyle.attrib.get(W_NS + "val")
        paragraphs.append({"text": text, "style": style})
    return paragraphs


def detect_chapters(paragraphs: list[dict]) -> list[dict]:
    chapters: list[dict] = []
    current = None
    for idx, item in enumerate(paragraphs):
        text = item["text"]
        normalized = " ".join(text.split())
        is_part = normalized.lower().startswith("часть ")
        is_chapter = bool(CHAPTER_RE.match(normalized))
        if is_part and not is_chapter:
            continue
        if is_chapter:
            if current is not None:
                current["end_paragraph"] = idx - 1
                current["paragraph_count"] = current["end_paragraph"] - current["start_paragraph"] + 1
                chapters.append(current)
            current = {
                "chapter_index": len(chapters) + 1,
                "title": normalized,
                "start_paragraph": idx,
            }
    if current is not None:
        current["end_paragraph"] = len(paragraphs) - 1
        current["paragraph_count"] = current["end_paragraph"] - current["start_paragraph"] + 1
        chapters.append(current)
    return chapters


def detect_structure_candidates(paragraphs: list[dict], chapters: list[dict]) -> list[dict]:
    candidates = []
    chapter_starts = {c["start_paragraph"] for c in chapters}
    for idx, item in enumerate(paragraphs):
        text = " ".join(item["text"].split())
        style = (item.get("style") or "").casefold()
        short = len(text) <= 120
        heading_style = any(k in style for k in ("heading", "title", "заголов"))
        looks_title = short and (
            heading_style
            or text.casefold().startswith(("часть ", "книга ", "повесть ", "рассказ "))
            or (text.isupper() and len(text) >= 4)
        )
        if looks_title and idx not in chapter_starts:
            candidates.append({
                "paragraph": idx,
                "text": text,
                "style": item.get("style"),
                "reason": "heading_style_or_title_pattern"
            })
    return candidates


def build_chunks(paragraphs: list[dict], target_chars: int = 7000) -> list[dict]:
    chunks: list[dict] = []
    buf: list[str] = []
    start = 0
    chars = 0

    def flush(end_idx: int):
        nonlocal buf, start, chars
        if not buf:
            return
        text = "\n\n".join(buf)
        chunks.append({
            "chunk_id": f"chunk-{len(chunks)+1:04d}",
            "start_paragraph": start,
            "end_paragraph": end_idx,
            "char_count": len(text),
            "text": text,
        })
        buf = []
        chars = 0

    for idx, item in enumerate(paragraphs):
        p = item["text"]
        if not buf:
            start = idx
        projected = chars + len(p) + 2
        if buf and projected > target_chars:
            flush(idx - 1)
            start = idx
        buf.append(p)
        chars += len(p) + 2
    flush(len(paragraphs) - 1)
    return chunks


def main() -> int:
    project_root = Path(__file__).resolve().parent
    project_dir = project_root / "projects" / "sto_let_tomu_vpered"
    source_dir = project_dir / "sources"
    source_candidates = sorted(source_dir.glob("*.docx"))

    print("=== ALINA BOOK 2 / MVP-14A SOURCE INGEST ===")
    if not source_candidates:
        print("FAIL source_docx_not_found")
        print(f"Expected: {source_dir}")
        return 1

    source = source_candidates[0]
    print(f"PASS source_found: {source.name}")
    print(f"SIZE: {source.stat().st_size} bytes")

    digest = sha256_file(source)
    print(f"PASS sha256: {digest}")

    paragraphs = extract_docx_paragraphs(source)
    if not paragraphs:
        print("FAIL no_paragraphs_extracted")
        return 1
    print(f"PASS paragraphs_extracted: {len(paragraphs)}")

    chapters = detect_chapters(paragraphs)
    if not chapters:
        print("FAIL chapters_not_detected")
        return 1
    print(f"PASS chapters_detected: {len(chapters)}")

    structure_candidates = detect_structure_candidates(paragraphs, chapters)
    print(f"PASS structure_candidates_detected: {len(structure_candidates)}")

    chunks = build_chunks(paragraphs)
    print(f"PASS analysis_chunks_built: {len(chunks)}")

    structure_dir = project_dir / "structure"
    state_dir = project_dir / "state"
    evidence_dir = project_dir / "evidence"
    runs_dir = project_dir / "runs"
    for d in (structure_dir, state_dir, evidence_dir, runs_dir):
        d.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "1.0",
        "project_id": "sto_let_tomu_vpered",
        "source": {
            "filename": source.name,
            "size_bytes": source.stat().st_size,
            "sha256": digest,
            "source_type": "docx",
            "stored_locally_only": True,
        },
        "ingest": {
            "paragraph_count": len(paragraphs),
            "chapter_count": len(chapters),
            "chunk_count": len(chunks),
            "structure_candidate_count": len(structure_candidates),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "status": "SOURCE_INGEST_PASS",
    }

    (project_dir / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (structure_dir / "chapters.json").write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (structure_dir / "structure_candidates.json").write_text(
        json.dumps(structure_candidates, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Full extracted source text stays local and ignored by Git.
    (source_dir / "source_extracted.txt").write_text(
        "\n\n".join(p["text"] for p in paragraphs), encoding="utf-8"
    )

    # Chunks also contain source text and stay local under sources/.
    chunk_dir = source_dir / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    for item in chunks:
        (chunk_dir / f"{item['chunk_id']}.txt").write_text(item["text"], encoding="utf-8")

    chunk_index = [
        {k: v for k, v in item.items() if k != "text"}
        for item in chunks
    ]
    (structure_dir / "chunk_index.json").write_text(
        json.dumps(chunk_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    run_report = {
        "stage": "MVP-14A_SOURCE_INGEST",
        "result": "PASS",
        "source_sha256": digest,
        "paragraph_count": len(paragraphs),
        "chapter_count": len(chapters),
        "chunk_count": len(chunks),
        "structure_candidate_count": len(structure_candidates),
    }
    (runs_dir / "mvp14a_source_ingest.json").write_text(
        json.dumps(run_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("PASS source_manifest_written")
    print("PASS chapter_structure_written")
    print("PASS structure_candidates_written")
    print("PASS chunk_index_written")
    print("PASS local_source_text_written")
    print("=== ALINA BOOK 2 MVP-14A SOURCE INGEST: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
