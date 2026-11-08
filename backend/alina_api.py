from __future__ import annotations

import hashlib
import json
import re
import shutil
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / ".alina-private"
PROJECTS_ROOT = DATA_ROOT / "projects"
PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ALINA Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5180", "http://localhost:5180"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RUNS: dict[str, dict[str, Any]] = {}
LOCK = threading.Lock()

STAGES = [
    ("SOURCE", "Подготовка источников", 8),
    ("SPLIT", "Разделение корпуса", 23),
    ("EVIDENCE", "Извлечение evidence", 47),
    ("ENTITIES", "Сущности и события", 66),
    ("WORLD", "Хронология и мир", 82),
    ("CONFLICTS", "Поиск противоречий", 94),
    ("FINALIZE", "Финализация БЗ", 100),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(text: str) -> str:
    s = re.sub(r"[^0-9A-Za-zА-Яа-яЁё_-]+", "_", text.strip())
    return s.strip("_")[:80] or "project"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def trace(run_id: str, stage: str, action: str, status: str = "INFO", **extra: Any) -> None:
    with LOCK:
        run = RUNS[run_id]
        event = {
            "timestamp": now(),
            "run_id": run_id,
            "stage": stage,
            "action": action,
            "status": status,
            **extra,
        }
        run["trace"].append(event)
        run["updated_at"] = event["timestamp"]


def set_stage(run_id: str, index: int, detail: str) -> None:
    code, label, progress = STAGES[index]
    with LOCK:
        run = RUNS[run_id]
        run.update({
            "stage_index": index,
            "stage": code,
            "stage_label": label,
            "detail": detail,
            "progress": progress,
            "status": "RUNNING",
            "updated_at": now(),
        })
    trace(run_id, code, detail, "RUNNING")


def parse_fb2(path: Path) -> dict[str, Any]:
    tree = ET.parse(path)
    root = tree.getroot()

    def lname(tag: str) -> str:
        return tag.split("}")[-1]

    titles: list[str] = []
    sections: list[dict[str, Any]] = []

    for elem in root.iter():
        if lname(elem.tag) == "section":
            title = None
            paragraphs = []
            for child in elem:
                if lname(child.tag) == "title":
                    parts = ["".join(x.itertext()).strip() for x in child]
                    title = " ".join(x for x in parts if x).strip() or "".join(child.itertext()).strip()
                elif lname(child.tag) == "p":
                    txt = "".join(child.itertext()).strip()
                    if txt:
                        paragraphs.append(txt)
            if title:
                titles.append(title)
                sections.append({"title": title, "paragraph_count": len(paragraphs)})

    all_text = "\n".join("".join(e.itertext()).strip() for e in root.iter() if lname(e.tag) == "p")
    return {
        "format": "fb2",
        "char_count": len(all_text),
        "section_count": len(sections),
        "headings": titles,
        "sections": sections[:2000],
        "text_preview": all_text[:3000],
    }


def parse_txt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        text = raw.decode("utf-8", errors="replace")
    headings = [x.strip() for x in text.splitlines() if 2 <= len(x.strip()) <= 120 and (x.strip().isupper() or re.match(r"^(глава|часть|книга)\b", x.strip(), re.I))]
    return {"format": "txt", "char_count": len(text), "section_count": len(headings), "headings": headings[:2000], "text_preview": text[:3000]}


def parse_pdf(path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise RuntimeError("Для PDF установите pypdf: pip install -r requirements-alina.txt") from e
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    text = "\n".join(texts)
    headings = [x.strip() for x in text.splitlines() if re.match(r"^(глава|часть|книга)\b", x.strip(), re.I)]
    return {"format": "pdf", "page_count": len(reader.pages), "char_count": len(text), "section_count": len(headings), "headings": headings[:2000], "text_preview": text[:3000]}


def parse_docx(path: Path) -> dict[str, Any]:
    try:
        from docx import Document
    except ImportError as e:
        raise RuntimeError("Для DOCX установите python-docx: pip install -r requirements-alina.txt") from e
    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    headings = [p.text.strip() for p in doc.paragraphs if p.text.strip() and (p.style.name.lower().startswith("heading") or re.match(r"^(глава|часть|книга)\b", p.text.strip(), re.I))]
    text = "\n".join(paragraphs)
    return {"format": "docx", "char_count": len(text), "section_count": len(headings), "headings": headings[:2000], "text_preview": text[:3000]}


def parse_epub(path: Path) -> dict[str, Any]:
    texts: list[str] = []
    headings: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.lower().endswith((".xhtml", ".html", ".htm")):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                for h in re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", raw, flags=re.I | re.S):
                    t = re.sub(r"<[^>]+>", " ", h)
                    t = re.sub(r"\s+", " ", t).strip()
                    if t:
                        headings.append(t)
                plain = re.sub(r"<[^>]+>", " ", raw)
                plain = re.sub(r"\s+", " ", plain).strip()
                texts.append(plain)
    text = "\n".join(texts)
    return {"format": "epub", "char_count": len(text), "section_count": len(headings), "headings": headings[:2000], "text_preview": text[:3000]}


def parse_source(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower()
    if ext == ".fb2":
        return parse_fb2(path)
    if ext == ".txt":
        return parse_txt(path)
    if ext == ".pdf":
        return parse_pdf(path)
    if ext == ".docx":
        return parse_docx(path)
    if ext == ".epub":
        return parse_epub(path)
    raise RuntimeError(f"Неподдерживаемый формат: {ext}")


def run_ingest(run_id: str, project_dir: Path, source_files: list[Path]) -> None:
    try:
        set_stage(run_id, 0, "Проверяю файлы, форматы и контрольные суммы")
        source_records = []
        for idx, path in enumerate(source_files, start=1):
            rec = {
                "source_id": f"SRC-{idx:04d}",
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "extension": path.suffix.lower(),
                "status": "AVAILABLE",
            }
            source_records.append(rec)
            trace(run_id, "SOURCE", f"Источник зарегистрирован: {path.name}", file_index=idx, file_total=len(source_files), output_ref=rec["source_id"])
        write_json(project_dir / "kb" / "sources.json", source_records)

        set_stage(run_id, 1, "Ищу произведения, сборники, главы и секции")
        parsed = []
        for idx, path in enumerate(source_files, start=1):
            t0 = time.perf_counter()
            data = parse_source(path)
            item = {
                "source_id": source_records[idx-1]["source_id"],
                "filename": path.name,
                **data,
            }
            parsed.append(item)
            trace(run_id, "SPLIT", f"Разобран {path.name}: {data.get('section_count', 0)} секций", duration_ms=int((time.perf_counter()-t0)*1000), file_index=idx, file_total=len(source_files))
        write_json(project_dir / "kb" / "structure.json", parsed)

        set_stage(run_id, 2, "Создаю доказуемые утверждения из структурных фактов")
        claims = []
        cid = 1
        for item in parsed:
            claims.append({"claim_id": f"CLM-{cid:06d}", "type": "SOURCE_STRUCTURE", "statement": f"{item['filename']} содержит {item.get('section_count', 0)} структурных секций", "source_id": item["source_id"], "confidence": 1.0, "status": "SOURCE_SUPPORTED"})
            cid += 1
            for heading in item.get("headings", [])[:500]:
                claims.append({"claim_id": f"CLM-{cid:06d}", "type": "HEADING", "statement": heading, "source_id": item["source_id"], "confidence": 1.0, "status": "SOURCE_SUPPORTED"})
                cid += 1
        write_json(project_dir / "kb" / "claims.json", claims)
        trace(run_id, "EVIDENCE", f"Создано утверждений: {len(claims)}", output_ref="kb/claims.json")

        set_stage(run_id, 3, "Создаю первичный реестр объектов корпуса")
        entities = []
        eid = 1
        seen = set()
        for item in parsed:
            for heading in item.get("headings", [])[:1000]:
                norm = re.sub(r"\s+", " ", heading).strip().casefold()
                if norm and norm not in seen:
                    seen.add(norm)
                    entities.append({"entity_id": f"ENT-{eid:06d}", "entity_type": "STRUCTURAL_HEADING", "canonical_name": heading, "source_id": item["source_id"], "confidence": 1.0, "status": "REVIEW"})
                    eid += 1
        write_json(project_dir / "kb" / "entities.json", entities)
        write_json(project_dir / "kb" / "events.json", [])
        trace(run_id, "ENTITIES", f"Создан первичный реестр: {len(entities)} объектов", output_ref="kb/entities.json")

        set_stage(run_id, 4, "Строю первичную карту корпуса и временную основу")
        world = {
            "status": "FOUNDATION_ONLY",
            "sources": len(source_records),
            "structural_objects": len(entities),
            "timeline_anchors": [],
            "technologies": [],
            "locations": [],
            "note": "Глубокое извлечение мира подключается следующим аналитическим слоем ALINA.",
        }
        write_json(project_dir / "kb" / "world.json", world)
        write_json(project_dir / "kb" / "graph.json", {"nodes": entities, "edges": []})
        trace(run_id, "WORLD", "Первичный graph/world foundation сохранён", output_ref="kb/graph.json")

        set_stage(run_id, 5, "Проверяю структурные дубли и неоднозначности")
        by_name: dict[str, list[dict[str, Any]]] = {}
        for ent in entities:
            by_name.setdefault(ent["canonical_name"].casefold(), []).append(ent)
        conflicts = [{"type": "DUPLICATE_HEADING", "name": k, "entity_ids": [x["entity_id"] for x in v]} for k, v in by_name.items() if len(v) > 1]
        write_json(project_dir / "kb" / "conflicts.json", conflicts)
        write_json(project_dir / "kb" / "review_queue.json", entities)
        trace(run_id, "CONFLICTS", f"Структурных конфликтов: {len(conflicts)}", output_ref="kb/conflicts.json")

        set_stage(run_id, 6, "Сохраняю индексы и итоговый run manifest")
        manifest = {
            "run_id": run_id,
            "completed_at": now(),
            "status": "PASS",
            "metrics": {
                "sources": len(source_records),
                "works": sum(max(1, p.get("section_count", 0)) for p in parsed),
                "claims": len(claims),
                "entities": len(entities),
                "events": 0,
                "conflicts": len(conflicts),
                "review": len(entities),
            },
            "outputs": [
                "kb/sources.json", "kb/structure.json", "kb/claims.json", "kb/entities.json",
                "kb/events.json", "kb/world.json", "kb/graph.json", "kb/conflicts.json", "kb/review_queue.json",
            ],
        }
        write_json(project_dir / "runs" / f"{run_id}.json", manifest)
        with LOCK:
            run = RUNS[run_id]
            run["status"] = "PASS"
            run["progress"] = 100
            run["metrics"] = manifest["metrics"]
            run["detail"] = "База знаний первого слоя построена"
            run["updated_at"] = now()
        trace(run_id, "FINALIZE", "Run завершён", "PASS", output_ref=f"runs/{run_id}.json")
    except Exception as exc:
        with LOCK:
            RUNS[run_id]["status"] = "FAIL"
            RUNS[run_id]["error"] = str(exc)
            RUNS[run_id]["updated_at"] = now()
        trace(run_id, RUNS[run_id].get("stage", "SYSTEM"), str(exc), "ERROR")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "mode": "PRIVATE_LOCAL", "data_root": str(DATA_ROOT)}


@app.post("/api/projects/ingest")
async def create_project(
    title: str = Form(...),
    mode: str = Form("study-cycle"),
    intent: str = Form(""),
    areas: str = Form("[]"),
    external_research: bool = Form(False),
    files: list[UploadFile] = File(...),
) -> dict[str, Any]:
    if not files:
        raise HTTPException(400, "Нет файлов")
    project_id = f"PRJ-{uuid.uuid4().hex[:10]}"
    run_id = f"RUN-{uuid.uuid4().hex[:12]}"
    project_dir = PROJECTS_ROOT / project_id
    sources_dir = project_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    saved: list[Path] = []
    for upload in files:
        safe = Path(upload.filename or "source.bin").name
        dest = sources_dir / safe
        with dest.open("wb") as out:
            shutil.copyfileobj(upload.file, out)
        saved.append(dest)

    metadata = {
        "project_id": project_id,
        "title": title,
        "mode": mode,
        "intent": intent,
        "areas": json.loads(areas),
        "external_research": bool(external_research),
        "privacy": "PRIVATE_LOCAL",
        "created_at": now(),
    }
    write_json(project_dir / "project.json", metadata)

    RUNS[run_id] = {
        "run_id": run_id,
        "project_id": project_id,
        "status": "QUEUED",
        "progress": 0,
        "stage_index": -1,
        "stage": "QUEUED",
        "stage_label": "В очереди",
        "detail": "Ожидание запуска",
        "trace": [],
        "metrics": {},
        "created_at": now(),
        "updated_at": now(),
        "error": None,
    }
    threading.Thread(target=run_ingest, args=(run_id, project_dir, saved), daemon=True).start()
    return {"project_id": project_id, "run_id": run_id, "status": "QUEUED"}


@app.get("/api/runs/{run_id}")
def run_status(run_id: str) -> dict[str, Any]:
    with LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(404, "Run не найден")
        return json.loads(json.dumps(run, ensure_ascii=False))


@app.get("/api/projects/{project_id}/kb/{name}")
def get_kb(project_id: str, name: str) -> JSONResponse:
    allowed = {"sources", "structure", "claims", "entities", "events", "world", "graph", "conflicts", "review_queue"}
    if name not in allowed:
        raise HTTPException(404, "Неизвестный раздел БЗ")
    path = PROJECTS_ROOT / project_id / "kb" / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, "Раздел ещё не создан")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> JSONResponse:
    path = PROJECTS_ROOT / project_id / "project.json"
    if not path.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))
