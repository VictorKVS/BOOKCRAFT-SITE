from __future__ import annotations

import hashlib
from difflib import SequenceMatcher
import json
import os
import re
import shutil
import subprocess
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

from backend.deep_analysis import detect_local_model, extract_units, chunk_units, analyze_chunk, merge_extractions, save_model_config, load_model_config

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
DEBUG_TRACE_LOCK = threading.Lock()
DEBUG_GIT_LOCK = threading.Lock()
DEBUG_GIT_STATE_LOCK = threading.Lock()
PROJECT_STATE_LOCK = threading.RLock()
DEBUG_GIT_STATE = {"status":"WAITING","updated_at":None,"error":None}
DEBUG_TRACE_FILE = ROOT / "projects" / "sto_let_tomu_vpered" / "debug" / "alina_ui_trace.jsonl"
ADMIN_SETTINGS_FILE = DATA_ROOT / "admin_settings.json"
DEFAULT_ADMIN_SETTINGS = {
    "github_debug_trace": False,
    "local_trace": True,
    "updated_at": None,
}

def load_admin_settings() -> dict[str, Any]:
    current = read_json(ADMIN_SETTINGS_FILE, {}) or {}
    merged = {**DEFAULT_ADMIN_SETTINGS, **current}
    return merged


def save_admin_settings(settings: dict[str, Any]) -> dict[str, Any]:
    merged = {**DEFAULT_ADMIN_SETTINGS, **settings, "updated_at": now()}
    write_json(ADMIN_SETTINGS_FILE, merged)
    return merged


def sanitize_debug_value(value: Any) -> Any:
    if isinstance(value, dict):
        allowed = {}
        for key, item in value.items():
            if key in {
                "action_id","event_type","status","project_id","project_code","run_id",
                "workspace_view","phase","method","endpoint","http_status","sequence",
                "step","result","reason","source_count","kb_version","analysis_profile",
                "product_type","product_id","button","duration_ms"
            }:
                allowed[key] = sanitize_debug_value(item)
        return allowed
    if isinstance(value, list):
        return [sanitize_debug_value(x) for x in value[:20]]
    if isinstance(value, (str,int,float,bool)) or value is None:
        text = str(value) if isinstance(value, str) else value
        if isinstance(text, str):
            return text[:240]
        return text
    return str(value)[:240]


def append_debug_trace(event: dict[str, Any]) -> dict[str, Any]:
    safe = sanitize_debug_value(event)
    record = {
        "timestamp": now(),
        **safe,
        "privacy": "SAFE_DEBUG_NO_BOOK_TEXT_NO_SOURCE_FILENAMES",
    }
    DEBUG_TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    with DEBUG_TRACE_LOCK:
        with DEBUG_TRACE_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    return record


def publish_debug_trace_to_git() -> dict[str, Any]:
    with DEBUG_GIT_LOCK:
        try:
            rel = str(DEBUG_TRACE_FILE.relative_to(ROOT)).replace("\\", "/")
            subprocess.run(["git","add","--",rel], cwd=ROOT, check=True, capture_output=True, text=True)
            diff = subprocess.run(["git","diff","--cached","--quiet"], cwd=ROOT)
            if diff.returncode == 0:
                return {"status":"NO_CHANGES"}
            subprocess.run(
                ["git","commit","-m","debug(alina): append UI/API trace","--",rel],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            push = subprocess.run(
                ["git","push","origin","alina-book-2"],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            return {"status":"PUSHED","detail":(push.stderr.strip() or push.stdout.strip())[:500]}
        except Exception as exc:
            return {"status":"WARN","error":str(exc)[:500]}


def publish_debug_trace_background() -> None:
    with DEBUG_GIT_STATE_LOCK:
        if DEBUG_GIT_STATE.get("status") == "PUBLISHING":
            return
        DEBUG_GIT_STATE["status"] = "PUBLISHING"
        DEBUG_GIT_STATE["updated_at"] = now()
        DEBUG_GIT_STATE["error"] = None

    def worker() -> None:
        result = publish_debug_trace_to_git()
        with DEBUG_GIT_STATE_LOCK:
            DEBUG_GIT_STATE["status"] = result.get("status","WARN")
            DEBUG_GIT_STATE["updated_at"] = now()
            DEBUG_GIT_STATE["error"] = result.get("error")

    threading.Thread(target=worker, daemon=True).start()


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


def infer_title_from_files(source_files: list[Path]) -> str:
    if not source_files:
        return "Новый проект"
    stems = [re.sub(r"[_\\-]+", " ", p.stem).strip() for p in source_files]
    if len(stems) == 1:
        name = stems[0]
        name = re.sub(r"\\b(original|litmir|club|edition|fb2|pdf|docx|epub)\\b", " ", name, flags=re.I)
        name = re.sub(r"\\s+", " ", name).strip(" _-")
        return name[:100] or "Новый проект"
    common = stems[0]
    for other in stems[1:]:
        prefix = []
        for a, c in zip(common.split(), other.split()):
            if normalize_title(a) != normalize_title(c):
                break
            prefix.append(a)
        common = " ".join(prefix)
        if not common:
            break
    return (common or f"Цикл из {len(source_files)} книг")[:100]


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def project_state_path(project_dir: Path) -> Path:
    return project_dir / "project_state.json"


def project_events_path(project_dir: Path) -> Path:
    return project_dir / "project_events.jsonl"


def scan_project_sources(project_dir: Path) -> list[dict[str, Any]]:
    sources_dir = project_dir / "sources"
    if not sources_dir.exists():
        return []
    rows = []
    manifest = read_json(project_dir / "kb" / "source_manifest.json", {}) or {}
    manifest_by_name = {str(x.get("filename")): x for x in manifest.get("sources", []) if x.get("filename")}
    for path in sorted((p for p in sources_dir.iterdir() if p.is_file()), key=lambda p:p.name.casefold()):
        known = manifest_by_name.get(path.name, {})
        rows.append({
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "extension": path.suffix.lower(),
            "sha256": known.get("sha256") or sha256(path),
            "status": "AVAILABLE",
            "added_at": known.get("added_at"),
        })
    return rows


def rebuild_project_state(project_dir: Path, last_event: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = read_json(project_dir / "project.json", {}) or {}
    sources = scan_project_sources(project_dir)
    works = read_json(project_dir / "kb" / "works.json", {}) or {}
    research = research_dashboard(project_dir) if (project_dir / "research" / "research_index.json").exists() else {
        "totals":{"works":0,"research_ready":0,"running":0,"blocked":0,"pass_tasks":0,"review_tasks":0,"failed_tasks":0},
        "programs":[],
        "continuity":{},
    }
    products = project_products(project_dir)

    run_files = sorted((project_dir / "runs").glob("*.state.json")) if (project_dir / "runs").exists() else []
    runs = [read_json(p,{}) or {} for p in run_files]
    runs = [r for r in runs if r]
    runs.sort(key=lambda x:x.get("created_at",""), reverse=True)
    latest_run = runs[0] if runs else None

    state = {
        "schema_version":"1.0",
        "project_id":meta.get("project_id"),
        "project_code":meta.get("short_code"),
        "title":meta.get("title"),
        "description":meta.get("description") or meta.get("intent") or "",
        "mode":meta.get("mode"),
        "intent":meta.get("intent"),
        "privacy":meta.get("privacy","PRIVATE_LOCAL"),
        "status":meta.get("status","PROJECT_CREATED"),
        "analysis_level":meta.get("analysis_level","NONE"),
        "active_analysis_profile":meta.get("active_analysis_profile"),
        "source_set":{
            "version":meta.get("source_set_version",0),
            "fingerprint":meta.get("source_fingerprint",""),
            "foundation_fingerprint":meta.get("foundation_fingerprint",""),
            "foundation_stale":bool(meta.get("foundation_stale",False)),
            "count":len(sources),
            "sources":sources,
        },
        "knowledge_base":{
            "version":meta.get("kb_version",0),
            "foundation_ready":meta.get("analysis_level") in {"FOUNDATION_ONLY","DEEP_SEMANTIC"},
            "works_matched":works.get("matched_count",0),
            "works_expected":works.get("expected"),
            "works_review":works.get("review_count",0),
            "works_missing":works.get("missing_count",0),
        },
        "research":{
            "status":(research.get("index") or {}).get("status"),
            "totals":research.get("totals",{}),
            "continuity_status":(research.get("continuity") or {}).get("program_status"),
        },
        "runs":{
            "count":len(runs),
            "latest":{
                "run_id":latest_run.get("run_id"),
                "run_type":latest_run.get("run_type"),
                "status":latest_run.get("status"),
                "progress":latest_run.get("progress"),
                "stage":latest_run.get("stage"),
                "updated_at":latest_run.get("updated_at"),
                "error":latest_run.get("error"),
            } if latest_run else None,
        },
        "products":{
            "count":len(products),
            "items":[
                {
                    "product_id":p.get("product_id"),
                    "type":p.get("type"),
                    "title":p.get("title"),
                    "status":p.get("status"),
                    "updated_at":p.get("updated_at"),
                } for p in products
            ],
        },
        "last_event":last_event,
        "created_at":meta.get("created_at"),
        "updated_at":now(),
    }
    write_json(project_state_path(project_dir), state)
    return state


def record_project_event(
    project_dir: Path,
    event_type: str,
    *,
    status: str = "PASS",
    actor: str = "ALINA",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with PROJECT_STATE_LOCK:
        event = {
            "event_id":f"EVT-{uuid.uuid4().hex[:12]}",
            "timestamp":now(),
            "event_type":event_type,
            "status":status,
            "actor":actor,
            "details":details or {},
        }
        path = project_events_path(project_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a",encoding="utf-8") as fh:
            fh.write(json.dumps(event,ensure_ascii=False)+"\n")
        rebuild_project_state(project_dir,last_event=event)
        return event


def read_project_events(project_dir: Path, limit: int = 200) -> list[dict[str, Any]]:
    path = project_events_path(project_dir)
    if not path.exists():
        return []
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines()[-max(1,min(limit,2000)):]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def next_project_short_code() -> str:
    used = []
    for project_dir in PROJECTS_ROOT.iterdir():
        if not project_dir.is_dir():
            continue
        meta = read_json(project_dir / "project.json", {}) or {}
        code = str(meta.get("short_code") or "")
        match = re.fullmatch(r"A(\d+)", code, re.I)
        if match:
            used.append(int(match.group(1)))
    return f"A{(max(used) + 1) if used else 1}"


def source_set_fingerprint(source_files: list[Path]) -> str:
    rows = []
    for path in sorted(source_files, key=lambda p: p.name.casefold()):
        if path.is_file():
            rows.append(f"{path.name}\t{sha256(path)}\t{path.stat().st_size}")
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest() if rows else ""


def project_products(project_dir: Path) -> list[dict[str, Any]]:
    path = project_dir / "products" / "index.json"
    return read_json(path, []) or []


def analysis_fingerprint(source_fingerprint: str, profile: str, config: dict[str, Any], model: dict[str, Any]) -> str:
    payload = {
        "source_fingerprint": source_fingerprint,
        "profile": profile,
        "config": config,
        "provider": model.get("provider"),
        "model": model.get("model"),
        "engine_version": "DEEP_V2",
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_research_task_catalog() -> dict[str, Any]:
    path = ROOT / "projects" / "sto_let_tomu_vpered" / "research" / "work_research_task_catalog_v1.json"
    return read_json(path, {"catalog_id":"ALINA_WORK_RESEARCH_V1","task_limit":30,"tasks":[]}) or {}


def load_cycle_continuity_catalog() -> dict[str, Any]:
    path = ROOT / "projects" / "sto_let_tomu_vpered" / "research" / "cycle_continuity_task_catalog_v1.json"
    return read_json(path, {"catalog_id":"ALINA_CYCLE_CONTINUITY_V1","task_limit":30,"tasks":[]}) or {}


def build_work_research_program(project_dir: Path, meta: dict[str, Any], work: dict[str, Any], blocked: bool = False) -> dict[str, Any]:
    catalog = load_research_task_catalog()
    tasks = []
    for raw in catalog.get("tasks", [])[:30]:
        task = {
            "task_id": raw.get("task_id"),
            "name": raw.get("name"),
            "research_question": raw.get("research_question", ""),
            "status": "BLOCKED" if blocked else "PLANNED",
            "progress": 0,
            "depends_on": list(raw.get("depends_on", [])),
            "executor": raw.get("executor", "WORK_SCOPED_SEMANTIC_V1"),
            "inputs": [],
            "outputs": [],
            "evidence_required": True,
            "metrics": {
                "items_found": 0,
                "items_accepted": 0,
                "items_review": 0,
                "evidence_coverage": 0.0,
            },
            "last_run_id": None,
            "started_at": None,
            "finished_at": None,
            "duration_ms": None,
            "blockers": ["WORK_BOUNDARY_REVIEW_REQUIRED"] if blocked else [],
            "quality_gate": "NOT_CHECKED",
        }
        tasks.append(task)

    work_id = work.get("work_id") or slug(str(work.get("title") or "work"))
    program = {
        "schema_version": "1.0",
        "project_id": meta.get("project_id"),
        "project_code": meta.get("short_code"),
        "work_id": work_id,
        "work_title": work.get("title") or work.get("candidate_heading") or work_id,
        "program_status": "BLOCKED" if blocked else "PLANNED",
        "created_at": now(),
        "updated_at": now(),
        "source_set_version": meta.get("source_set_version", 0),
        "source_fingerprint": meta.get("source_fingerprint", ""),
        "research_profile": "LITERARY_FULL_V1",
        "task_limit": 30,
        "summary": {
            "total": len(tasks),
            "planned": 0 if blocked else len(tasks),
            "running": 0,
            "pass": 0,
            "review": 0,
            "blocked": len(tasks) if blocked else 0,
            "failed": 0,
            "reused": 0,
            "completion_pct": 0,
        },
        "source_match": {
            "status": work.get("status"),
            "matched_heading": work.get("matched_heading") or work.get("candidate_heading"),
            "confidence": work.get("confidence"),
        },
        "tasks": tasks,
    }
    path = project_dir / "research" / work_id / "research_program.json"
    write_json(path, program)
    return program


def initialize_project_research_complex(project_dir: Path, meta: dict[str, Any], work_match: dict[str, Any] | None) -> dict[str, Any]:
    research_root = project_dir / "research"
    research_root.mkdir(parents=True, exist_ok=True)
    programs = []

    if work_match:
        for work in work_match.get("matched", []):
            programs.append(build_work_research_program(project_dir, meta, work, blocked=False))
        for work in work_match.get("review", []):
            programs.append(build_work_research_program(project_dir, meta, work, blocked=True))

    index = {
        "schema_version": "1.0",
        "project_id": meta.get("project_id"),
        "project_code": meta.get("short_code"),
        "status": "RESEARCH_COMPLEX_INITIALIZED",
        "task_limit_per_work": 30,
        "work_count": len(programs),
        "ready_to_start": sum(1 for p in programs if p.get("program_status") == "PLANNED"),
        "blocked": sum(1 for p in programs if p.get("program_status") == "BLOCKED"),
        "programs": [
            {
                "work_id": p.get("work_id"),
                "work_title": p.get("work_title"),
                "program_status": p.get("program_status"),
                "summary": p.get("summary"),
                "path": f"research/{p.get('work_id')}/research_program.json",
            }
            for p in programs
        ],
        "updated_at": now(),
    }
    write_json(research_root / "research_index.json", index)

    cycle_catalog = load_cycle_continuity_catalog()
    cycle_tasks = []
    for raw in cycle_catalog.get("tasks", [])[:30]:
        cycle_tasks.append({
            "task_id": raw.get("task_id"),
            "name": raw.get("name"),
            "status": "BLOCKED",
            "progress": 0,
            "blockers": ["WORK_RESEARCH_R30_NOT_READY"],
            "quality_gate": "NOT_CHECKED",
        })
    continuity = {
        "schema_version": "1.0",
        "project_id": meta.get("project_id"),
        "project_code": meta.get("short_code"),
        "program_status": "BLOCKED",
        "reason": "Cycle analysis starts only after eligible works pass R30.",
        "work_programs_total": len(programs),
        "work_programs_ready": 0,
        "task_limit": 30,
        "summary": {
            "total": len(cycle_tasks),
            "pass": 0,
            "blocked": len(cycle_tasks),
            "completion_pct": 0,
        },
        "tasks": cycle_tasks,
        "updated_at": now(),
    }
    write_json(research_root / "continuity_program.json", continuity)
    return {"index": index, "continuity": continuity}


def research_dashboard(project_dir: Path) -> dict[str, Any]:
    index = read_json(project_dir / "research" / "research_index.json", {}) or {}
    programs = []
    for row in index.get("programs", []):
        work_id = row.get("work_id")
        program = read_json(project_dir / "research" / str(work_id) / "research_program.json", {}) or {}
        if program:
            programs.append(program)
    totals = {
        "works": len(programs),
        "research_ready": sum(1 for p in programs if p.get("program_status") == "RESEARCH_READY"),
        "running": sum(1 for p in programs if p.get("program_status") == "RUNNING"),
        "blocked": sum(1 for p in programs if p.get("program_status") == "BLOCKED"),
        "pass_tasks": sum(int((p.get("summary") or {}).get("pass",0)) for p in programs),
        "review_tasks": sum(int((p.get("summary") or {}).get("review",0)) for p in programs),
        "failed_tasks": sum(int((p.get("summary") or {}).get("failed",0)) for p in programs),
    }
    return {
        "index": index,
        "totals": totals,
        "programs": programs,
        "continuity": read_json(project_dir / "research" / "continuity_program.json", {}) or {},
    }


def recalc_research_program(program: dict[str, Any]) -> dict[str, Any]:
    tasks = program.get("tasks", [])
    by_id = {t.get("task_id"): t for t in tasks}
    terminal_ok = {"PASS", "REUSED"}

    for task in tasks:
        if task.get("status") in {"PASS","REUSED","RUNNING","FAILED","REVIEW"}:
            continue
        deps = task.get("depends_on", [])
        if not deps:
            if task.get("status") == "PLANNED":
                task["status"] = "READY"
                task["blockers"] = []
            continue
        unmet = [d for d in deps if (by_id.get(d) or {}).get("status") not in terminal_ok]
        if unmet:
            task["status"] = "BLOCKED"
            task["blockers"] = [f"DEPENDENCY:{d}" for d in unmet]
        else:
            if task.get("executor") == "WORK_SCOPED_SEMANTIC_V1":
                task["status"] = "READY"
                task["blockers"] = []
            else:
                task["status"] = "READY"
                task["blockers"] = []

    counts = {k:0 for k in ("planned","ready","running","pass","review","blocked","failed","reused","skipped")}
    for task in tasks:
        key = str(task.get("status","PLANNED")).lower()
        if key in counts:
            counts[key] += 1
    finished_equiv = counts["pass"] + counts["reused"] + 0.5 * counts["review"]
    summary = program.setdefault("summary", {})
    summary.update({
        "total": len(tasks),
        **counts,
        "completion_pct": round((finished_equiv / max(1,len(tasks))) * 100),
    })

    r30 = by_id.get("R30")
    if r30 and r30.get("status") in terminal_ok:
        program["program_status"] = "RESEARCH_READY"
    elif counts["running"]:
        program["program_status"] = "RUNNING"
    elif counts["failed"]:
        program["program_status"] = "FAILED"
    elif counts["review"]:
        program["program_status"] = "REVIEW"
    elif counts["blocked"] == len(tasks):
        program["program_status"] = "BLOCKED"
    else:
        program["program_status"] = "ACTIVE"
    program["updated_at"] = now()
    return program


def sync_research_index(project_dir: Path, program: dict[str, Any]) -> None:
    index_path = project_dir / "research" / "research_index.json"
    index = read_json(index_path, {}) or {}
    for row in index.get("programs", []):
        if row.get("work_id") == program.get("work_id"):
            row["program_status"] = program.get("program_status")
            row["summary"] = program.get("summary")
    index["ready_to_start"] = sum(
        1 for row in index.get("programs", [])
        if row.get("program_status") in {"PLANNED","ACTIVE","REVIEW"}
    )
    index["blocked"] = sum(
        1 for row in index.get("programs", [])
        if row.get("program_status") == "BLOCKED"
    )
    index["updated_at"] = now()
    write_json(index_path, index)


def _xml_local_name(tag: str) -> str:
    return tag.split("}")[-1]


def _section_title(section: Any) -> str:
    for child in section:
        if _xml_local_name(child.tag) == "title":
            return re.sub(r"\s+", " ", " ".join(child.itertext())).strip()
    return ""


def _section_direct_paragraphs(section: Any) -> list[str]:
    rows = []
    for child in section:
        if _xml_local_name(child.tag) == "p":
            text = re.sub(r"\s+", " ", "".join(child.itertext())).strip()
            if text:
                rows.append(text)
    return rows


def _fb2_work_units(path: Path, target_title: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tree = ET.parse(path)
    root = tree.getroot()
    target_norm = normalize_title(target_title)
    candidates = []
    for section in root.iter():
        if _xml_local_name(section.tag) != "section":
            continue
        title = _section_title(section)
        if not title:
            continue
        norm = normalize_title(title)
        if norm == target_norm:
            score = 1.0
        elif target_norm and (target_norm in norm or norm in target_norm):
            score = min(len(target_norm), len(norm)) / max(1, max(len(target_norm), len(norm)))
        else:
            score = SequenceMatcher(None, target_norm, norm).ratio()
        if score >= 0.78:
            candidates.append((score, section, title))

    if not candidates:
        return [], {"status":"BOUNDARY_NOT_FOUND","target_title":target_title}

    candidates.sort(key=lambda x:x[0], reverse=True)
    score, target_section, matched_title = candidates[0]
    units = []
    ordinal = 0

    def walk(section: Any, inherited_title: str) -> None:
        nonlocal ordinal
        own_title = _section_title(section) or inherited_title
        direct = _section_direct_paragraphs(section)
        if direct:
            ordinal += 1
            units.append({
                "ordinal":ordinal,
                "section_title":own_title,
                "text":"\n".join(direct),
            })
        for child in section:
            if _xml_local_name(child.tag) == "section":
                walk(child, own_title)

    walk(target_section, matched_title)
    return units, {
        "status":"MATCHED_SECTION_SUBTREE",
        "target_title":target_title,
        "matched_title":matched_title,
        "confidence":round(score,4),
        "unit_count":len(units),
    }


def extract_work_scoped_units(project_dir: Path, work_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    works = read_json(project_dir / "kb" / "works.json", {}) or {}
    match = next((w for w in works.get("matched", []) if w.get("work_id") == work_id), None)
    if not match:
        raise RuntimeError("WORK_NOT_TRUSTED_OR_NOT_MATCHED")

    source_id = match.get("source_id")
    sources = read_json(project_dir / "kb" / "sources.json", []) or []
    source = next((x for x in sources if x.get("source_id") == source_id), None)
    if not source:
        raise RuntimeError("WORK_SOURCE_NOT_FOUND")

    source_name = source.get("filename")
    path = project_dir / "sources" / str(source_name)
    if not path.exists():
        raise RuntimeError("WORK_SOURCE_FILE_MISSING")

    matched_title = match.get("matched_heading") or match.get("title") or work_id
    if path.suffix.lower() == ".fb2":
        units, boundary = _fb2_work_units(path, matched_title)
        if not units:
            raise RuntimeError("WORK_BOUNDARY_NOT_FOUND_IN_FB2")
    else:
        units = extract_units(path)
        boundary = {
            "status":"WHOLE_SOURCE_SCOPED",
            "target_title":matched_title,
            "matched_title":matched_title,
            "confidence":match.get("confidence"),
            "unit_count":len(units),
            "note":"Non-FB2 source uses the whole matched source file as work scope.",
        }

    safe_index = []
    char_count = 0
    for unit in units:
        text = unit.get("text","")
        char_count += len(text)
        safe_index.append({
            "ordinal":unit.get("ordinal"),
            "section_title":unit.get("section_title"),
            "char_count":len(text),
            "text_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })

    boundary.update({
        "work_id":work_id,
        "source_id":source_id,
        "source_name":source_name,
        "char_count":char_count,
        "unit_count":len(units),
        "safe_unit_index":safe_index,
    })
    return units, boundary


def build_work_scoped_chunks(project_dir: Path, work_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    units, boundary = extract_work_scoped_units(project_dir, work_id)
    source_id = f"{work_id}-SRC"
    chunks = chunk_units(source_id, work_id, units)
    boundary["chunk_count"] = len(chunks)
    boundary["chunk_index"] = [
        {k:v for k,v in ch.items() if k != "text"} for ch in chunks
    ]
    out = project_dir / "research" / work_id / "work_scope.json"
    write_json(out, boundary)
    return chunks, boundary


def run_work_semantic_extraction(project_dir: Path, work_id: str, research_run_id: str) -> None:
    program_path = project_dir / "research" / work_id / "research_program.json"
    program = read_json(program_path, {}) or {}
    task = next((t for t in program.get("tasks", []) if t.get("task_id") == "R03"), None)
    if not task:
        return

    try:
        model = detect_local_model()
        if not model.get("available"):
            task["status"] = "BLOCKED"
            task["quality_gate"] = "BLOCKED"
            task["blockers"] = ["LOCAL_LLM_REQUIRED"]
            task["progress"] = 0
            task["finished_at"] = now()
            write_json(program_path, recalc_research_program(program))
            sync_research_index(project_dir, program)
            return

        chunks, boundary = build_work_scoped_chunks(project_dir, work_id)
        if not chunks:
            raise RuntimeError("WORK_SCOPE_EMPTY")

        run_dir = project_dir / "research" / work_id / "semantic" / research_run_id
        chunk_dir = run_dir / "chunks"
        chunk_dir.mkdir(parents=True, exist_ok=True)
        write_json(run_dir / "contract.json", {
            "research_run_id":research_run_id,
            "task_id":"R03",
            "work_id":work_id,
            "model":{"provider":model.get("provider"),"model":model.get("model")},
            "source_fingerprint":program.get("source_fingerprint"),
            "boundary":{k:v for k,v in boundary.items() if k not in {"chunk_index","safe_unit_index"}},
            "created_at":now(),
        })

        extractions = []
        started = time.perf_counter()
        total = len(chunks)
        for idx, chunk in enumerate(chunks, start=1):
            result_path = chunk_dir / f"{chunk['chunk_id']}.json"
            if result_path.exists():
                result = read_json(result_path, {}) or {}
            else:
                result = analyze_chunk(model, chunk)
                result["_chunk"] = {k:v for k,v in chunk.items() if k != "text"}
                result["_extractor"] = {
                    "provider":model.get("provider"),
                    "model":model.get("model"),
                    "task_id":"R03",
                    "work_id":work_id,
                    "research_run_id":research_run_id,
                }
                write_json(result_path, result)
            if "_chunk" not in result:
                result["_chunk"] = {k:v for k,v in chunk.items() if k != "text"}
            extractions.append(result)
            task["progress"] = max(5, int(idx / total * 95))
            task["metrics"]["chunks_total"] = total
            task["metrics"]["chunks_processed"] = idx
            task["metrics"]["chars_scoped"] = boundary.get("char_count",0)
            program["program_status"] = "RUNNING"
            program["updated_at"] = now()
            write_json(program_path, program)

        merged = merge_extractions(extractions)
        outputs_dir = project_dir / "research" / work_id / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        package = {
            "schema_version":"1.0",
            "research_run_id":research_run_id,
            "task_id":"R03",
            "work_id":work_id,
            "boundary":boundary,
            "model":{"provider":model.get("provider"),"model":model.get("model")},
            "metrics":{
                "chunks":total,
                "chars_scoped":boundary.get("char_count",0),
                "characters":len(merged.get("characters",[])),
                "events":len(merged.get("events",[])),
                "relations":len(merged.get("relations",[])),
                "locations":len(merged.get("locations",[])),
                "technologies":len(merged.get("technologies",[])),
                "organizations":len(merged.get("organizations",[])),
                "time_anchors":len(merged.get("time_anchors",[])),
                "claims":len(merged.get("claims",[])),
                "open_threads":len(merged.get("open_threads",[])),
                "elapsed_seconds":round(time.perf_counter()-started,1),
            },
            "created_at":now(),
        }
        write_json(outputs_dir / "R03_semantic_package.json", package)
        for key in ("characters","events","relations","locations","technologies","organizations","time_anchors","claims","open_threads"):
            write_json(outputs_dir / f"R03_{key}.json", merged.get(key,[]))
        weighted_graph = build_weighted_research_graph(project_dir, work_id)
        package["metrics"]["graph_nodes"] = weighted_graph.get("node_count",0)
        package["metrics"]["graph_edges"] = weighted_graph.get("edge_count",0)
        write_json(outputs_dir / "R03_semantic_package.json", package)

        task["status"] = "PASS"
        task["quality_gate"] = "PASS"
        task["progress"] = 100
        task["finished_at"] = now()
        task["duration_ms"] = int((time.perf_counter()-started)*1000)
        task["outputs"] = [
            f"research/{work_id}/outputs/R03_semantic_package.json",
            f"research/{work_id}/semantic/{research_run_id}",
        ]
        task["blockers"] = []
        task["metrics"].update({
            "items_found":len(merged.get("claims",[])),
            "items_accepted":0,
            "items_review":len(merged.get("claims",[])),
            "evidence_coverage":0.0,
            **package["metrics"],
        })
        program = recalc_research_program(program)
        write_json(program_path, program)
        sync_research_index(project_dir, program)

        run_record = {
            "schema_version":"1.0",
            "research_run_id":research_run_id,
            "project_id":program.get("project_id"),
            "project_code":program.get("project_code"),
            "work_id":work_id,
            "work_title":program.get("work_title"),
            "task_id":"R03",
            "task_name":task.get("name"),
            "executor":"WORK_SCOPED_SEMANTIC_V1",
            "status":"PASS",
            "quality_gate":"PASS",
            "started_at":task.get("started_at"),
            "finished_at":task.get("finished_at"),
            "duration_ms":task.get("duration_ms"),
            "outputs":task.get("outputs",[]),
            "metrics":task.get("metrics",{}),
            "blockers":[],
            "source_fingerprint":program.get("source_fingerprint"),
        }
        write_json(project_dir / "research" / work_id / "runs" / f"{research_run_id}.json", run_record)
        record_project_event(project_dir,"RESEARCH_TASK_FINISHED",status="PASS",details={
            "work_id":work_id,
            "task_id":"R03",
            "research_run_id":research_run_id,
            "quality_gate":"PASS",
            "metrics":task.get("metrics",{}),
            "outputs":task.get("outputs",[]),
        })

        # Continue dependency-ordered execution automatically after the long semantic stage.
        refreshed = read_json(program_path, {}) or {}
        if refreshed.get("auto_mode"):
            threading.Thread(
                target=execute_research_auto,
                args=(project_dir, work_id, 30),
                daemon=True,
            ).start()

    except Exception as exc:
        task["status"] = "FAILED"
        task["quality_gate"] = "FAILED"
        task["progress"] = 0
        task["finished_at"] = now()
        task["blockers"] = [str(exc)[:240]]
        program = recalc_research_program(program)
        write_json(program_path, program)
        sync_research_index(project_dir, program)
        record_project_event(project_dir,"RESEARCH_TASK_FINISHED",status="FAILED",details={
            "work_id":work_id,
            "task_id":"R03",
            "research_run_id":research_run_id,
            "error":str(exc)[:240],
        })


def normalize_evidence_text(value: str) -> str:
    value = value.casefold().replace("ё","е")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[«»„“”\"'—–-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def execute_r04_evidence_verification(project_dir: Path, work_id: str, task: dict[str, Any]) -> None:
    outputs_dir = project_dir / "research" / work_id / "outputs"
    claims = read_json(outputs_dir / "R03_claims.json", []) or []
    chunks, _ = build_work_scoped_chunks(project_dir, work_id)
    chunk_map = {ch.get("chunk_id"): ch.get("text","") for ch in chunks}

    # Claims generated by merge_extractions carry chunk_id.
    verified = []
    supported = 0
    partial = 0
    rejected = 0

    for idx, claim in enumerate(claims, start=1):
        chunk_id = claim.get("chunk_id")
        evidence = str(claim.get("evidence") or "").strip()
        chunk_text = chunk_map.get(chunk_id, "")
        norm_evidence = normalize_evidence_text(evidence)
        norm_chunk = normalize_evidence_text(chunk_text)

        if not evidence or not chunk_text:
            verdict = "NO_EVIDENCE"
            rejected += 1
            score = 0.0
        elif norm_evidence and norm_evidence in norm_chunk:
            verdict = "VERIFIED_EXACT"
            supported += 1
            score = 1.0
        else:
            # Conservative token overlap only routes to REVIEW, never PASS.
            e_tokens = set(norm_evidence.split())
            c_tokens = set(norm_chunk.split())
            overlap = len(e_tokens & c_tokens) / max(1, len(e_tokens))
            if overlap >= 0.85:
                verdict = "REVIEW_NEAR_MATCH"
                partial += 1
                score = round(overlap,4)
            else:
                verdict = "REJECTED_NOT_FOUND"
                rejected += 1
                score = round(overlap,4)

        verified.append({
            **claim,
            "evidence_verification":{
                "verdict":verdict,
                "match_score":score,
                "chunk_id":chunk_id,
            }
        })
        task["progress"] = int(idx / max(1,len(claims)) * 95)

    total = len(claims)
    coverage = supported / max(1,total)
    result = {
        "schema_version":"1.0",
        "task_id":"R04",
        "work_id":work_id,
        "claims_total":total,
        "verified_exact":supported,
        "review_near_match":partial,
        "rejected":rejected,
        "evidence_coverage":round(coverage,4),
        "quality_rule":"Only exact normalized source matches count as evidence-verified PASS.",
        "created_at":now(),
        "claims":verified,
    }
    write_json(outputs_dir / "R04_evidence_verification.json", result)

    task["outputs"] = [f"research/{work_id}/outputs/R04_evidence_verification.json"]
    task["metrics"].update({
        "items_found":total,
        "items_accepted":supported,
        "items_review":partial,
        "items_rejected":rejected,
        "evidence_coverage":round(coverage,4),
    })
    if total == 0:
        task["status"] = "REVIEW"
        task["quality_gate"] = "REVIEW"
        task["blockers"] = ["NO_CLAIMS_EXTRACTED"]
    elif coverage >= 0.80 and rejected == 0:
        task["status"] = "PASS"
        task["quality_gate"] = "PASS"
        task["blockers"] = []
    else:
        task["status"] = "REVIEW"
        task["quality_gate"] = "REVIEW"
        task["blockers"] = ["EVIDENCE_COVERAGE_OR_REJECTIONS_REQUIRE_REVIEW"]


def extract_object_evidence(item: dict[str, Any]) -> list[tuple[str | None, str]]:
    evidence = item.get("evidence")
    rows = []
    if isinstance(evidence, list):
        for e in evidence:
            if isinstance(e, dict):
                rows.append((e.get("chunk_id") or item.get("chunk_id"), str(e.get("text") or e.get("evidence") or "")))
            elif e:
                rows.append((item.get("chunk_id"), str(e)))
    elif isinstance(evidence, dict):
        rows.append((evidence.get("chunk_id") or item.get("chunk_id"), str(evidence.get("text") or evidence.get("evidence") or "")))
    elif evidence:
        rows.append((item.get("chunk_id"), str(evidence)))
    return [(cid, txt.strip()) for cid,txt in rows if txt.strip()]


def execute_verified_registry_task(
    project_dir: Path,
    work_id: str,
    task: dict[str, Any],
    source_file: str,
    output_file: str,
    registry_type: str,
) -> None:
    source = read_json(project_dir / "research" / work_id / "outputs" / source_file, []) or []
    chunks, _ = build_work_scoped_chunks(project_dir, work_id)
    chunk_map = {ch.get("chunk_id"): ch.get("text","") for ch in chunks}

    accepted = []
    review = []
    rejected = []
    for idx,item in enumerate(source, start=1):
        evidence_rows = extract_object_evidence(item)
        exact = False
        best = 0.0
        for chunk_id,evidence in evidence_rows:
            chunk_text = chunk_map.get(chunk_id, "")
            ne = normalize_evidence_text(evidence)
            nc = normalize_evidence_text(chunk_text)
            if ne and ne in nc:
                exact = True
                best = 1.0
                break
            e_tokens=set(ne.split())
            c_tokens=set(nc.split())
            overlap=len(e_tokens & c_tokens)/max(1,len(e_tokens))
            best=max(best,overlap)

        record={**item,"research_evidence":{"verified":exact,"match_score":round(best,4)}}
        if exact:
            accepted.append(record)
        elif best >= 0.85:
            review.append(record)
        else:
            rejected.append(record)
        task["progress"] = int(idx / max(1,len(source)) * 95)

    result = {
        "schema_version":"1.0",
        "task_id":task.get("task_id"),
        "work_id":work_id,
        "registry_type":registry_type,
        "total":len(source),
        "accepted_count":len(accepted),
        "review_count":len(review),
        "rejected_count":len(rejected),
        "evidence_coverage":round(len(accepted)/max(1,len(source)),4),
        "accepted":accepted,
        "review":review,
        "rejected":rejected,
        "created_at":now(),
    }
    out=project_dir / "research" / work_id / "outputs" / output_file
    write_json(out,result)
    task["outputs"]=[str(out.relative_to(project_dir)).replace("\\","/")]
    task["metrics"].update({
        "items_found":len(source),
        "items_accepted":len(accepted),
        "items_review":len(review),
        "items_rejected":len(rejected),
        "evidence_coverage":result["evidence_coverage"],
    })
    if not source:
        task["status"]="REVIEW"
        task["quality_gate"]="REVIEW"
        task["blockers"]=["NO_ITEMS_EXTRACTED"]
    elif len(rejected)==0 and result["evidence_coverage"] >= 0.80:
        task["status"]="PASS"
        task["quality_gate"]="PASS"
        task["blockers"]=[]
    else:
        task["status"]="REVIEW"
        task["quality_gate"]="REVIEW"
        task["blockers"]=["REGISTRY_EVIDENCE_REQUIRES_REVIEW"]


def build_weighted_research_graph(project_dir: Path, work_id: str) -> dict[str, Any]:
    outputs = project_dir / "research" / work_id / "outputs"
    chars = read_json(outputs / "R03_characters.json", []) or []
    events = read_json(outputs / "R03_events.json", []) or []
    relations = read_json(outputs / "R03_relations.json", []) or []
    locations = read_json(outputs / "R03_locations.json", []) or []
    technologies = read_json(outputs / "R03_technologies.json", []) or []
    organizations = read_json(outputs / "R03_organizations.json", []) or []

    nodes = []
    edges = []
    node_index = {}

    def evidence_weight(item: dict[str, Any]) -> float:
        ev = extract_object_evidence(item)
        if not ev:
            return 0.35
        return min(1.0, 0.6 + 0.1 * len(ev))

    def add_node(kind: str, label: str, item: dict[str, Any]) -> str | None:
        clean = str(label or "").strip()
        if not clean:
            return None
        key = (kind, normalize_title(clean))
        if key in node_index:
            node = node_index[key]
            node["mentions"] += 1
            node["weight"] = round(min(1.0, node["weight"] + 0.04), 4)
            return node["id"]
        node_id = f"{kind[:3].upper()}-{len(nodes)+1:05d}"
        node = {
            "id":node_id,
            "type":kind,
            "label":clean,
            "weight":round(evidence_weight(item),4),
            "mentions":1,
            "confidence":float(item.get("confidence") or 0.5),
            "chunk_id":item.get("chunk_id"),
        }
        nodes.append(node)
        node_index[key] = node
        return node_id

    for item in chars:
        add_node("CHARACTER", item.get("name"), item)
    for item in events:
        add_node("EVENT", item.get("event"), item)
    for item in locations:
        add_node("LOCATION", item.get("name"), item)
    for item in technologies:
        add_node("TECHNOLOGY", item.get("name"), item)
    for item in organizations:
        add_node("ORGANIZATION", item.get("name"), item)

    def lookup(kind: str, label: str) -> str | None:
        node = node_index.get((kind, normalize_title(str(label or ""))))
        return node.get("id") if node else None

    for rel in relations:
        source = lookup("CHARACTER", rel.get("source"))
        target = lookup("CHARACTER", rel.get("target"))
        if source and target:
            edges.append({
                "id":f"EDGE-{len(edges)+1:06d}",
                "source":source,
                "target":target,
                "type":rel.get("relation_type") or "RELATED",
                "weight":round(evidence_weight(rel),4),
                "confidence":float(rel.get("confidence") or 0.5),
                "chunk_id":rel.get("chunk_id"),
                "evidence":str(rel.get("evidence") or "")[:500],
            })

    for event in events:
        event_id = lookup("EVENT", event.get("event"))
        if not event_id:
            continue
        for participant in event.get("participants", []) or []:
            char_id = lookup("CHARACTER", participant)
            if char_id:
                edges.append({
                    "id":f"EDGE-{len(edges)+1:06d}",
                    "source":char_id,
                    "target":event_id,
                    "type":"PARTICIPATES_IN",
                    "weight":round(evidence_weight(event),4),
                    "confidence":float(event.get("confidence") or 0.5),
                    "chunk_id":event.get("chunk_id"),
                })
        loc_id = lookup("LOCATION", event.get("location"))
        if event_id and loc_id:
            edges.append({
                "id":f"EDGE-{len(edges)+1:06d}",
                "source":event_id,
                "target":loc_id,
                "type":"OCCURS_AT",
                "weight":round(evidence_weight(event),4),
                "confidence":float(event.get("confidence") or 0.5),
                "chunk_id":event.get("chunk_id"),
            })

    graph = {
        "schema_version":"1.0",
        "graph_type":"EVIDENCE_WEIGHTED_RESEARCH_GRAPH",
        "work_id":work_id,
        "node_count":len(nodes),
        "edge_count":len(edges),
        "weight_semantics":{
            "node_weight":"evidence presence + repeated mentions, capped at 1.0",
            "edge_weight":"evidence strength for extracted relation/event link",
            "confidence":"extractor confidence when available; otherwise conservative default 0.5",
        },
        "nodes":nodes,
        "edges":edges,
        "created_at":now(),
    }
    write_json(outputs / "research_graph.json", graph)
    return graph


def project_research_scheduler(project_dir: Path) -> None:
    index = read_json(project_dir / "research" / "research_index.json", {}) or {}
    for row in index.get("programs", []):
        work_id = row.get("work_id")
        if not work_id:
            continue
        program_path = project_dir / "research" / work_id / "research_program.json"
        program = read_json(program_path, {}) or {}
        if program.get("program_status") == "BLOCKED":
            continue

        record_project_event(project_dir,"WORK_RESEARCH_STARTED",status="RUNNING",details={"work_id":work_id})
        execute_research_auto(project_dir, work_id, 30)

        # Do not run multiple LLM work analyses concurrently.
        for _ in range(60 * 60):
            current = read_json(program_path, {}) or {}
            if current.get("program_status") != "RUNNING":
                break
            time.sleep(1)

        current = read_json(program_path, {}) or {}
        graph = build_weighted_research_graph(project_dir, work_id)
        record_project_event(project_dir,"WORK_RESEARCH_UPDATED",status=current.get("program_status") or "PASS",details={
            "work_id":work_id,
            "program_status":current.get("program_status"),
            "completion_pct":(current.get("summary") or {}).get("completion_pct",0),
            "graph_nodes":graph.get("node_count",0),
            "graph_edges":graph.get("edge_count",0),
        })

        # Stop on review/failed/blocking condition; preserve evidence for human inspection.
        if current.get("program_status") in {"FAILED","REVIEW"}:
            continue


def start_project_research_scheduler(project_dir: Path) -> None:
    threading.Thread(target=project_research_scheduler, args=(project_dir,), daemon=True).start()


def execute_research_task(project_dir: Path, work_id: str, task_id: str) -> dict[str, Any]:
    program_path = project_dir / "research" / work_id / "research_program.json"
    program = read_json(program_path, None)
    if program is None:
        raise HTTPException(404, "Исследовательская программа произведения не найдена")

    program = recalc_research_program(program)
    tasks = {t.get("task_id"): t for t in program.get("tasks", [])}
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(404, "Исследовательская задача не найдена")
    if task.get("status") in {"PASS","REUSED"}:
        return {"status":"REUSED","task":task,"program":program}
    if task.get("status") == "BLOCKED":
        raise HTTPException(409, "Задача заблокирована: " + ", ".join(task.get("blockers", [])))

    started = time.perf_counter()
    task["status"] = "RUNNING"
    task["progress"] = 5
    task["started_at"] = now()
    task["last_run_id"] = f"RSR-{uuid.uuid4().hex[:10]}"
    task["blockers"] = []
    program["program_status"] = "RUNNING"
    write_json(program_path, program)
    record_project_event(project_dir,"RESEARCH_TASK_STARTED",status="RUNNING",details={
        "work_id":work_id,
        "task_id":task_id,
        "research_run_id":task.get("last_run_id"),
        "task_name":task.get("name"),
    })

    try:
        if task_id == "R01":
            meta = read_json(project_dir / "project.json", {}) or {}
            manifest = read_json(project_dir / "kb" / "source_manifest.json", {}) or {}
            works = read_json(project_dir / "kb" / "works.json", {}) or {}
            matched = next((w for w in works.get("matched", []) if w.get("work_id") == work_id), None)
            review = next((w for w in works.get("review", []) if w.get("work_id") == work_id), None)
            item = matched or review
            if not item or not meta.get("source_fingerprint") or not manifest.get("source_fingerprint"):
                raise RuntimeError("SOURCE_IDENTITY_INCOMPLETE")
            result = {
                "task_id":"R01",
                "work_id":work_id,
                "source_fingerprint":meta.get("source_fingerprint"),
                "source_set_version":meta.get("source_set_version"),
                "work_match_status":item.get("status"),
                "work_match_confidence":item.get("confidence"),
                "matched_heading":item.get("matched_heading") or item.get("candidate_heading"),
                "source_manifest_count":manifest.get("source_count"),
                "result":"PASS" if matched else "REVIEW",
                "created_at":now(),
            }
            out = project_dir / "research" / work_id / "outputs" / "R01_source_integrity.json"
            write_json(out, result)
            task["outputs"] = [str(out.relative_to(project_dir)).replace("\\","/")]
            task["metrics"].update({
                "items_found": 1,
                "items_accepted": 1 if matched else 0,
                "items_review": 0 if matched else 1,
                "evidence_coverage": 1.0,
            })
            task["status"] = "PASS" if matched else "REVIEW"
            task["quality_gate"] = task["status"]

        elif task_id == "R02":
            structure = read_json(project_dir / "kb" / "structure.json", []) or []
            works = read_json(project_dir / "kb" / "works.json", {}) or {}
            match = next((w for w in works.get("matched", []) if w.get("work_id") == work_id), None)
            if not match:
                raise RuntimeError("WORK_BOUNDARY_NOT_TRUSTED")
            source_id = match.get("source_id")
            source_struct = next((x for x in structure if x.get("source_id") == source_id), None)
            if not source_struct:
                raise RuntimeError("SOURCE_STRUCTURE_NOT_FOUND")
            result = {
                "task_id":"R02",
                "work_id":work_id,
                "matched_heading":match.get("matched_heading"),
                "source_id":source_id,
                "source_format":source_struct.get("format"),
                "source_section_count":source_struct.get("section_count",0),
                "boundary_status":"FOUNDATION_MATCHED_WORK",
                "note":"Current foundation confirms work identity inside source. Exact work-scoped paragraph boundary requires semantic slicer for full deep execution.",
                "result":"PASS",
                "created_at":now(),
            }
            out = project_dir / "research" / work_id / "outputs" / "R02_structural_map.json"
            write_json(out, result)
            task["outputs"] = [str(out.relative_to(project_dir)).replace("\\","/")]
            task["metrics"].update({
                "items_found": int(source_struct.get("section_count",0)),
                "items_accepted": 1,
                "items_review": 0,
                "evidence_coverage": 1.0,
            })
            task["status"] = "PASS"
            task["quality_gate"] = "PASS"

        elif task_id == "R04":
            execute_r04_evidence_verification(project_dir, work_id, task)

        elif task_id == "R07":
            execute_verified_registry_task(
                project_dir, work_id, task,
                "R03_characters.json", "R07_entity_registry.json", "CHARACTER_ENTITY_REGISTRY"
            )

        elif task_id == "R14":
            execute_verified_registry_task(
                project_dir, work_id, task,
                "R03_events.json", "R14_event_registry.json", "EVENT_REGISTRY"
            )

        elif task_id == "R17":
            execute_verified_registry_task(
                project_dir, work_id, task,
                "R03_locations.json", "R17_location_registry.json", "LOCATION_REGISTRY"
            )

        elif task_id == "R20":
            execute_verified_registry_task(
                project_dir, work_id, task,
                "R03_technologies.json", "R20_technology_registry.json", "TECHNOLOGY_REGISTRY"
            )

        elif task_id == "R22":
            execute_verified_registry_task(
                project_dir, work_id, task,
                "R03_organizations.json", "R22_organization_registry.json", "ORGANIZATION_REGISTRY"
            )

        elif task_id == "R30":
            prereq = [tasks.get(f"R{i:02d}") for i in range(1,30)]
            bad = [x.get("task_id") for x in prereq if not x or x.get("status") not in {"PASS","REUSED"}]
            if bad:
                task["status"] = "BLOCKED"
                task["quality_gate"] = "BLOCKED"
                task["blockers"] = [f"NOT_PASS:{x}" for x in bad]
            else:
                result = {
                    "task_id":"R30",
                    "work_id":work_id,
                    "quality_gate":"PASS",
                    "research_ready":True,
                    "completed_tasks":29,
                    "created_at":now(),
                }
                out = project_dir / "research" / work_id / "outputs" / "R30_quality_gate.json"
                write_json(out, result)
                task["outputs"] = [str(out.relative_to(project_dir)).replace("\\","/")]
                task["metrics"].update({"items_found":29,"items_accepted":29,"items_review":0,"evidence_coverage":1.0})
                task["status"] = "PASS"
                task["quality_gate"] = "PASS"

        elif task_id == "R03":
            model = detect_local_model()
            if not model.get("available"):
                task["status"] = "BLOCKED"
                task["progress"] = 0
                task["quality_gate"] = "BLOCKED"
                task["blockers"] = ["LOCAL_LLM_REQUIRED"]
            else:
                task["status"] = "RUNNING"
                task["progress"] = 1
                task["quality_gate"] = "RUNNING"
                task["blockers"] = []
                program["program_status"] = "RUNNING"
                write_json(program_path, program)
                threading.Thread(
                    target=run_work_semantic_extraction,
                    args=(project_dir, work_id, task.get("last_run_id")),
                    daemon=True,
                ).start()
                return {
                    "status":"QUEUED",
                    "task":task,
                    "program":program,
                    "research_run_id":task.get("last_run_id"),
                }

        else:
            task["status"] = "BLOCKED"
            task["progress"] = 0
            task["quality_gate"] = "BLOCKED"
            task["blockers"] = ["TASK_EXECUTOR_NOT_CONNECTED"]
            task["executor_note"] = "Task contract exists; its dedicated executor is not connected yet."

    except Exception as exc:
        task["status"] = "FAILED"
        task["quality_gate"] = "FAILED"
        task["blockers"] = [str(exc)[:200]]

    task["finished_at"] = now()
    task["duration_ms"] = int((time.perf_counter()-started)*1000)
    if task.get("status") in {"PASS","REUSED","REVIEW"}:
        task["progress"] = 100 if task.get("status") in {"PASS","REUSED"} else max(task.get("progress",0),50)

    program = recalc_research_program(program)
    write_json(program_path, program)
    sync_research_index(project_dir, program)

    run_record = {
        "schema_version":"1.0",
        "research_run_id":task.get("last_run_id"),
        "project_id":program.get("project_id"),
        "project_code":program.get("project_code"),
        "work_id":work_id,
        "work_title":program.get("work_title"),
        "task_id":task_id,
        "task_name":task.get("name"),
        "executor":task.get("executor"),
        "status":task.get("status"),
        "quality_gate":task.get("quality_gate"),
        "started_at":task.get("started_at"),
        "finished_at":task.get("finished_at"),
        "duration_ms":task.get("duration_ms"),
        "outputs":task.get("outputs",[]),
        "metrics":task.get("metrics",{}),
        "blockers":task.get("blockers",[]),
        "source_fingerprint":program.get("source_fingerprint"),
    }
    run_path = project_dir / "research" / work_id / "runs" / f"{task.get('last_run_id')}.json"
    write_json(run_path, run_record)
    history = program.setdefault("execution_history", [])
    history.append({
        "research_run_id":task.get("last_run_id"),
        "task_id":task_id,
        "status":task.get("status"),
        "finished_at":task.get("finished_at"),
        "duration_ms":task.get("duration_ms"),
        "run_file":str(run_path.relative_to(project_dir)).replace("\\","/"),
    })
    program["execution_history"] = history[-200:]
    write_json(program_path, program)
    record_project_event(project_dir,"RESEARCH_TASK_FINISHED",status=task.get("status") or "PASS",details={
        "work_id":work_id,
        "task_id":task_id,
        "research_run_id":task.get("last_run_id"),
        "quality_gate":task.get("quality_gate"),
        "duration_ms":task.get("duration_ms"),
        "outputs":task.get("outputs",[]),
        "blockers":task.get("blockers",[]),
    })

    return {"status":task.get("status"),"task":task,"program":program,"run":run_record}


def execute_next_research_task(project_dir: Path, work_id: str) -> dict[str, Any]:
    program_path = project_dir / "research" / work_id / "research_program.json"
    program = read_json(program_path, None)
    if program is None:
        raise HTTPException(404, "Исследовательская программа произведения не найдена")
    program = recalc_research_program(program)
    write_json(program_path, program)
    sync_research_index(project_dir, program)

    for task in program.get("tasks", []):
        if task.get("status") == "READY":
            return execute_research_task(project_dir, work_id, task.get("task_id"))
    return {"status":"NO_READY_TASKS","program":program}


def execute_research_auto(project_dir: Path, work_id: str, max_steps: int = 30) -> dict[str, Any]:
    program_path = project_dir / "research" / work_id / "research_program.json"
    program = read_json(program_path, {}) or {}
    program["auto_mode"] = True
    program["auto_updated_at"] = now()
    write_json(program_path, program)

    executed = []
    for _ in range(max(1,min(max_steps,30))):
        result = execute_next_research_task(project_dir, work_id)
        status = result.get("status")
        if status == "NO_READY_TASKS":
            break
        task = result.get("task") or {}
        executed.append({
            "task_id":task.get("task_id"),
            "status":task.get("status"),
            "quality_gate":task.get("quality_gate"),
            "blockers":task.get("blockers",[]),
        })
        if task.get("status") in {"FAILED"}:
            break

    program = read_json(project_dir / "research" / work_id / "research_program.json", {}) or {}
    return {
        "status":"AUTO_STOPPED" if not executed or (executed[-1].get("status") == "BLOCKED") else "AUTO_PROGRESS",
        "executed":executed,
        "program":program,
        "stop_reason": (
            executed[-1].get("blockers",[]) if executed and executed[-1].get("status") == "BLOCKED"
            else ["NO_READY_TASKS"] if not any(t.get("status") == "READY" for t in program.get("tasks",[]))
            else []
        ),
    }


def normalize_title(value: str) -> str:
    value = value.casefold().replace("ё", "е")
    value = re.sub(r"[«»„“”\"'.,:;!?()\[\]{}—–-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def load_known_catalog(title: str, parsed: list[dict[str, Any]]) -> dict[str, Any] | None:
    headings = " ".join(h for item in parsed for h in item.get("headings", [])[:400])
    filenames = " ".join(str(item.get("filename") or "") for item in parsed)
    probe = normalize_title(title + " " + filenames + " " + headings)
    alice_path = ROOT / "projects" / "sto_let_tomu_vpered" / "alice_cycle" / "alice_works_manifest.json"
    if ("алиса" in probe or "bulychev" in probe or "булычев" in probe) and alice_path.exists():
        return json.loads(alice_path.read_text(encoding="utf-8"))
    return None


def match_catalog(catalog: dict[str, Any], parsed: list[dict[str, Any]]) -> dict[str, Any]:
    source_titles: list[dict[str, str]] = []
    for item in parsed:
        for heading in item.get("headings", []):
            key = normalize_title(heading)
            if key:
                source_titles.append({"key": key, "heading": heading, "source_id": item["source_id"]})
        for candidate in item.get("title_candidates", []):
            key = normalize_title(candidate)
            if key:
                source_titles.append({"key": key, "heading": candidate, "source_id": item["source_id"]})

    matched = []
    review = []
    missing = []
    used_source_keys: set[tuple[str, str]] = set()

    for work in catalog.get("works", []):
        candidates = [work.get("title", ""), *work.get("aliases", [])]
        normalized_candidates = [(c, normalize_title(c)) for c in candidates if normalize_title(c)]
        best = None

        for original, key in normalized_candidates:
            for src in source_titles:
                pair = (src["source_id"], src["key"])
                if pair in used_source_keys:
                    continue

                if key == src["key"]:
                    score = 1.0
                    match_type = "TITLE_OR_ALIAS_EXACT"
                elif len(key) >= 8 and (key in src["key"] or src["key"] in key):
                    shorter = min(len(key), len(src["key"]))
                    longer = max(len(key), len(src["key"]))
                    score = 0.94 * (shorter / longer) + 0.05
                    match_type = "TITLE_CONTAINMENT"
                else:
                    ratio = SequenceMatcher(None, key, src["key"]).ratio()
                    tokens_a = set(key.split())
                    tokens_b = set(src["key"].split())
                    token_overlap = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))
                    score = 0.72 * ratio + 0.28 * token_overlap
                    match_type = "TITLE_FUZZY"

                if best is None or score > best["score"]:
                    best = {
                        "score": score,
                        "match_type": match_type,
                        "candidate": original,
                        "source": src,
                    }

        if best and best["score"] >= 0.86:
            src = best["source"]
            used_source_keys.add((src["source_id"], src["key"]))
            matched.append({
                "work_id": work["work_id"],
                "title": work["title"],
                "publication_year": work.get("publication_year"),
                "form": work.get("form"),
                "matched_heading": src["heading"],
                "source_id": src["source_id"],
                "match_type": best["match_type"],
                "confidence": round(best["score"], 4),
                "status": "MATCHED" if best["score"] >= 0.92 else "MATCHED_WITH_VARIANT",
            })
        elif best and best["score"] >= 0.72:
            review.append({
                "work_id": work["work_id"],
                "title": work["title"],
                "candidate_heading": best["source"]["heading"],
                "source_id": best["source"]["source_id"],
                "confidence": round(best["score"], 4),
                "status": "REVIEW_MATCH",
            })
        else:
            missing.append({
                "work_id": work["work_id"],
                "title": work["title"],
                "status": "MISSING_OR_UNRESOLVED",
            })

    return {
        "catalog_id": catalog.get("project_id"),
        "cycle": catalog.get("cycle"),
        "expected": catalog.get("catalog_count", len(catalog.get("works", []))),
        "matched_count": len(matched),
        "review_count": len(review),
        "missing_count": len(missing),
        "matched": matched,
        "review": review,
        "missing": missing,
    }


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
    persist_run_state(run_id)


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
            "current_item": 0,
            "current_total": 0,
            "current_name": "",
            "updated_at": now(),
        })
    persist_run_state(run_id)
    trace(run_id, code, detail, "RUNNING")


def set_item_progress(run_id: str, current: int, total: int, name: str, action: str | None = None) -> None:
    with LOCK:
        run = RUNS[run_id]
        run["current_item"] = current
        run["current_total"] = total
        run["current_name"] = name
        run["updated_at"] = now()
    if action:
        trace(run_id, RUNS[run_id].get("stage", "TEXT"), action, "INFO", current=current, total=total, name=name)


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
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines() if x.strip()]
    headings = [x for x in lines if re.match(r"^(глава|часть|книга)\b", x, re.I)]
    title_candidates = [x for x in lines[:160] if 3 <= len(x) <= 100]
    return {"format": "pdf", "page_count": len(reader.pages), "char_count": len(text), "section_count": len(headings), "headings": headings[:2000], "title_candidates": title_candidates[:160], "text_preview": text[:3000]}


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


def build_safe_run_report(project_dir: Path, run_id: str, project_title: str, manifest: dict[str, Any], work_match: dict[str, Any] | None, trace_events: list[dict[str, Any]]) -> tuple[Path, Path]:
    export_dir = ROOT / "projects" / "sto_let_tomu_vpered" / "alice_cycle" / "run_reports"
    export_dir.mkdir(parents=True, exist_ok=True)
    safe_trace = [
        {
            "timestamp": e.get("timestamp"),
            "stage": e.get("stage"),
            "status": e.get("status"),
            "action": e.get("action"),
            "current": e.get("current"),
            "total": e.get("total"),
            "name": e.get("name"),
        }
        for e in trace_events[-500:]
    ]
    payload = {
        "project_title": project_title,
        "run_id": run_id,
        "completed_at": manifest.get("completed_at"),
        "status": manifest.get("status"),
        "metrics": manifest.get("metrics"),
        "works": {
            "cycle": (work_match or {}).get("cycle"),
            "expected": (work_match or {}).get("expected"),
            "matched_count": (work_match or {}).get("matched_count"),
            "review_count": (work_match or {}).get("review_count"),
            "missing_count": (work_match or {}).get("missing_count"),
            "matched": [
                {
                    "work_id": x.get("work_id"),
                    "title": x.get("title"),
                    "matched_heading": x.get("matched_heading"),
                    "confidence": x.get("confidence"),
                    "status": x.get("status"),
                }
                for x in (work_match or {}).get("matched", [])
            ],
            "review": (work_match or {}).get("review", []),
            "missing": (work_match or {}).get("missing", []),
        },
        "trace_summary": safe_trace,
        "privacy": "SAFE_DERIVED_ONLY_NO_SOURCE_TEXT",
    }
    json_path = export_dir / f"{run_id}.json"
    md_path = export_dir / f"{run_id}.md"
    write_json(json_path, payload)
    md = [
        f"# ALINA SAFE RUN REPORT — {run_id}",
        "",
        f"Project: **{project_title}**",
        f"Status: **{manifest.get('status')}**",
        "",
        "## Metrics",
        "",
    ]
    for k, v in (manifest.get("metrics") or {}).items():
        md.append(f"- {k}: {v}")
    md += [
        "",
        "## Work matching",
        "",
        f"- cycle: {(work_match or {}).get('cycle')}",
        f"- matched: {(work_match or {}).get('matched_count')}",
        f"- review: {(work_match or {}).get('review_count')}",
        f"- missing: {(work_match or {}).get('missing_count')}",
        "",
        "## Privacy",
        "",
        "No source book text or private excerpts are included in this report.",
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return json_path, md_path


def git_publish_safe_report(run_id: str, files: list[Path]) -> dict[str, Any]:
    rels = [str(p.relative_to(ROOT)).replace("\\", "/") for p in files]
    try:
        for rel in rels:
            subprocess.run(["git", "add", "--", rel], cwd=ROOT, check=True, capture_output=True, text=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if diff.returncode == 0:
            return {"status": "NO_CHANGES", "files": rels}
        subprocess.run(["git", "commit", "-m", f"data(alina): publish safe run report {run_id}"], cwd=ROOT, check=True, capture_output=True, text=True)
        push = subprocess.run(["git", "push", "origin", "alina-book-2"], cwd=ROOT, check=True, capture_output=True, text=True)
        return {"status": "PUSHED", "files": rels, "detail": push.stderr.strip() or push.stdout.strip()}
    except Exception as exc:
        return {"status": "WARN", "files": rels, "error": str(exc)}


def persist_run_state(run_id: str) -> None:
    with LOCK:
        run = json.loads(json.dumps(RUNS.get(run_id, {}), ensure_ascii=False))
    if not run:
        return
    project_id = run.get("project_id")
    if not project_id:
        return
    project_dir = PROJECTS_ROOT / project_id
    write_json(project_dir / "runs" / f"{run_id}.state.json", run)
    if (project_dir / "project.json").exists():
        with PROJECT_STATE_LOCK:
            rebuild_project_state(project_dir)


def run_ingest(run_id: str, project_dir: Path, source_files: list[Path], project_title: str) -> None:
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
            total_sections = data.get("section_count", 0)
            trace(run_id, "SPLIT", f"Разобран {path.name}: {total_sections} секций", duration_ms=int((time.perf_counter()-t0)*1000), file_index=idx, file_total=len(source_files))
            for sec_idx, sec in enumerate(data.get("sections", [])[:2000], start=1):
                if sec_idx == 1 or sec_idx % 25 == 0 or sec_idx == total_sections:
                    set_item_progress(
                        run_id,
                        sec_idx,
                        total_sections,
                        sec.get("title", ""),
                        f"TEXT section {sec_idx}/{total_sections}: {sec.get('title', '')}",
                    )
        write_json(project_dir / "kb" / "structure.json", parsed)

        catalog = load_known_catalog(project_title, parsed)
        work_match = None
        if catalog:
            work_match = match_catalog(catalog, parsed)
            project_meta = read_json(project_dir / "project.json", {}) or {}
            if project_meta.get("title_mode") == "AUTO":
                project_meta["title"] = f"{catalog.get('cycle', project_meta.get('title', 'Проект'))} — цикл"
                project_meta["title_detected_from"] = "KNOWN_CATALOG"
                project_meta["updated_at"] = now()
                write_json(project_dir / "project.json", project_meta)
                with LOCK:
                    RUNS[run_id]["project_title"] = project_meta["title"]
            write_json(project_dir / "kb" / "works.json", work_match)
            trace(
                run_id,
                "SPLIT",
                f"Каталог {work_match.get('cycle')}: найдено {work_match['matched_count']} из {work_match['expected']} произведений",
                output_ref="kb/works.json",
            )
            for idx, w in enumerate(work_match.get("matched", []), start=1):
                trace(run_id, "MATCH", f"{w['work_id']} → {w['matched_heading']} ({round(w['confidence']*100)}%)", "INFO", current=idx, total=work_match["matched_count"], name=w["title"])
            for w in work_match.get("review", []):
                trace(run_id, "MATCH", f"{w['work_id']} → REVIEW: {w.get('candidate_heading')} ({round(w['confidence']*100)}%)", "WARN", name=w["title"])
        else:
            write_json(project_dir / "kb" / "works.json", {
                "catalog_id": None,
                "cycle": None,
                "expected": None,
                "matched_count": 0,
                "missing_count": 0,
                "matched": [],
                "missing": [],
                "status": "NO_CATALOG_SELECTED",
            })

        project_meta_for_research = read_json(project_dir / "project.json", {}) or {}
        research_init = initialize_project_research_complex(project_dir, project_meta_for_research, work_match)
        trace(
            run_id,
            "RESEARCH",
            f"Research Complex: произведений={research_init['index'].get('work_count',0)}, задач до 30 на произведение",
            "PASS",
            output_ref="research/research_index.json",
        )

        set_stage(run_id, 2, "Создаю доказуемые утверждения из структурных фактов")
        claims = []
        cid = 1
        for item in parsed:
            claims.append({"claim_id": f"CLM-{cid:06d}", "type": "SOURCE_STRUCTURE", "statement": f"{item['filename']} содержит {item.get('section_count', 0)} структурных секций", "source_id": item["source_id"], "confidence": 1.0, "status": "SOURCE_SUPPORTED"})
            cid += 1
            headings_for_claims = item.get("headings", [])[:500]
            total_claim_headings = len(headings_for_claims)
            for hidx, heading in enumerate(headings_for_claims, start=1):
                claims.append({"claim_id": f"CLM-{cid:06d}", "type": "HEADING", "statement": heading, "source_id": item["source_id"], "confidence": 1.0, "status": "SOURCE_SUPPORTED"})
                cid += 1
                if hidx == 1 or hidx % 25 == 0 or hidx == total_claim_headings:
                    set_item_progress(run_id, hidx, total_claim_headings, heading, f"CLAIM {hidx}/{total_claim_headings}: {heading}")
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
            "analysis_level": project_meta_for_research.get("analysis_level", "FOUNDATION_ONLY"),
            "deep_semantic_analysis": False,
            "metrics": {
                "sources": len(source_records),
                "sections": sum(p.get("section_count", 0) for p in parsed),
                "works": work_match["matched_count"] if work_match else 0,
                "works_expected": work_match["expected"] if work_match else None,
                "works_review": work_match["review_count"] if work_match else None,
                "works_missing": work_match["missing_count"] if work_match else None,
                "claims": len(claims),
                "entities": len(entities),
                "events": 0,
                "conflicts": len(conflicts),
                "review": len(entities),
            },
            "outputs": [
                "kb/sources.json", "kb/structure.json", "kb/works.json", "kb/claims.json", "kb/entities.json",
                "kb/events.json", "kb/world.json", "kb/graph.json", "kb/conflicts.json", "kb/review_queue.json",
            ],
        }
        write_json(project_dir / "runs" / f"{run_id}.json", manifest)

        with LOCK:
            trace_snapshot = list(RUNS[run_id]["trace"])
        safe_files = build_safe_run_report(project_dir, run_id, project_title, manifest, work_match, trace_snapshot)
        trace(run_id, "GITHUB", "SAFE RUN REPORT сформирован без текста книг", "INFO", name=safe_files[0].name)
        git_result = git_publish_safe_report(run_id, list(safe_files))
        if git_result.get("status") == "PUSHED":
            trace(run_id, "GITHUB", "SAFE RUN REPORT отправлен в GitHub/alina-book-2", "PASS")
        elif git_result.get("status") == "NO_CHANGES":
            trace(run_id, "GITHUB", "GitHub: изменений для отправки нет", "INFO")
        else:
            trace(run_id, "GITHUB", f"GitHub publish warning: {git_result.get('error')}", "WARN")

        project_meta = read_json(project_dir / "project.json", {}) or {}
        project_meta["status"] = "FOUNDATION_READY"
        project_meta["analysis_level"] = "FOUNDATION_ONLY"
        project_meta["foundation_fingerprint"] = source_set_fingerprint(source_files)
        project_meta["foundation_stale"] = False
        project_meta["kb_version"] = int(project_meta.get("kb_version") or 0) + 1
        project_meta["active_analysis_profile"] = "FOUNDATION"
        project_meta["updated_at"] = now()
        write_json(project_dir / "project.json", project_meta)

        record_project_event(project_dir,"FOUNDATION_COMPLETED",details={
            "run_id":run_id,
            "kb_version":project_meta.get("kb_version"),
            "analysis_level":project_meta.get("analysis_level"),
            "metrics":manifest.get("metrics",{}),
        })

        # Foundation prepares the corpus. Research is the real analytical stage.
        start_project_research_scheduler(project_dir)
        record_project_event(project_dir,"RESEARCH_SCHEDULER_STARTED",status="RUNNING",details={
            "work_count":research_init["index"].get("work_count",0)
        })
        trace(run_id, "RESEARCH", "Автоматическая исследовательская очередь запущена после Foundation", "PASS", output_ref="research/research_index.json")

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
        record_project_event(project_dir,"FOUNDATION_FAILED",status="FAIL",details={"run_id":run_id,"error":str(exc)[:500]})


def run_deep_analysis(run_id: str, project_dir: Path, analysis_key: str, profile: str, analysis_config: dict[str, Any]) -> None:
    record_project_event(project_dir,"DEEP_ANALYSIS_STARTED",status="RUNNING",details={
        "run_id":run_id,"analysis_key":analysis_key,"profile":profile
    })
    try:
        model = detect_local_model()
        with LOCK:
            RUNS[run_id]["model"] = model
            RUNS[run_id]["stage"] = "MODEL"
            RUNS[run_id]["stage_label"] = "Проверка локальной LLM"
            RUNS[run_id]["detail"] = "Ищу локальную модель для глубокого анализа"
            RUNS[run_id]["status"] = "RUNNING"
            RUNS[run_id]["progress"] = 1
        persist_run_state(run_id)
        trace(run_id, "MODEL", f"Provider: {model.get('provider')} / model: {model.get('model')}", "INFO")

        if not model.get("available"):
            with LOCK:
                RUNS[run_id]["status"] = "NEEDS_MODEL"
                RUNS[run_id]["detail"] = "Локальная LLM не обнаружена. Глубокий анализ не запускался."
                RUNS[run_id]["progress"] = 0
            persist_run_state(run_id)
            trace(run_id, "MODEL", "Deep analysis остановлен: локальная модель не найдена", "WARN")
            return

        sources = read_json(project_dir / "kb" / "sources.json", []) or []
        source_by_name = {x.get("filename"): x for x in sources}
        source_paths = [p for p in (project_dir / "sources").iterdir() if p.is_file()]
        all_chunks = []

        with LOCK:
            RUNS[run_id].update({
                "stage":"CHUNKING","stage_label":"Подготовка полного текста","detail":"Разбиваю полный корпус на аналитические chunks","progress":3,
            })
        persist_run_state(run_id)

        for file_index, path in enumerate(source_paths, start=1):
            source = source_by_name.get(path.name, {})
            source_id = source.get("source_id") or f"SRC-{file_index:04d}"
            trace(run_id, "CHUNKING", f"Читаю полный текст: {path.name}", "RUNNING", current=file_index, total=len(source_paths), name=path.name)
            units = extract_units(path)
            chunks = chunk_units(source_id, path.name, units)
            all_chunks.extend(chunks)
            trace(run_id, "CHUNKING", f"{path.name}: units={len(units)}, chunks={len(chunks)}", "PASS")

        deep_dir = project_dir / "deep"
        common_dir = deep_dir / "source_cache"
        run_dir = deep_dir / "analysis_runs" / analysis_key
        chunk_dir = run_dir / "chunks"
        common_dir.mkdir(parents=True, exist_ok=True)
        chunk_dir.mkdir(parents=True, exist_ok=True)
        write_json(common_dir / "chunk_index.json", [
            {k:v for k,v in ch.items() if k != "text"} for ch in all_chunks
        ])

        total = len(all_chunks)
        if total == 0:
            raise RuntimeError("Не удалось получить текстовые chunks")

        write_json(run_dir / "analysis_contract.json", {
            "analysis_fingerprint": analysis_key,
            "profile": profile,
            "config": analysis_config,
            "model": {"provider": model.get("provider"), "model": model.get("model")},
            "source_fingerprint": (read_json(project_dir / "project.json", {}) or {}).get("source_fingerprint"),
            "created_at": now(),
        })

        checkpoint_path = run_dir / "checkpoint.json"
        checkpoint = read_json(checkpoint_path, {}) or {
            "analysis_fingerprint":analysis_key,
            "run_id":run_id,
            "status":"RUNNING",
            "total_chunks":total,
            "completed_chunks":0,
            "last_attempted":None,
            "last_completed":None,
            "updated_at":now(),
        }
        checkpoint["run_id"] = run_id
        checkpoint["status"] = "RUNNING"
        checkpoint["total_chunks"] = total
        checkpoint["updated_at"] = now()
        write_json(checkpoint_path, checkpoint)

        extractions = []
        chars_processed = 0
        started = time.perf_counter()

        for idx, chunk in enumerate(all_chunks, start=1):
            result_path = chunk_dir / f"{chunk['chunk_id']}.json"
            with LOCK:
                run = RUNS[run_id]
                run["stage"] = "DEEP_TEXT"
                run["stage_label"] = "Глубокий анализ текста"
                run["detail"] = f"Модель анализирует chunk {idx}/{total}"
                run["current_item"] = idx
                run["current_total"] = total
                run["current_name"] = chunk.get("section_title") or chunk["source_name"]
                run["progress"] = min(92, 5 + int((idx - 1) / total * 87))
                run["chars_processed"] = chars_processed
                run["model_name"] = model.get("model")
            persist_run_state(run_id)

            checkpoint.update({
                "status":"RUNNING",
                "current_index":idx,
                "current_total":total,
                "last_attempted":chunk["chunk_id"],
                "current_section":chunk.get("section_title") or chunk["source_name"],
                "completed_chunks":sum(1 for p in chunk_dir.glob("*.json")),
                "updated_at":now(),
            })
            write_json(checkpoint_path, checkpoint)

            if result_path.exists():
                result = read_json(result_path, {}) or {}
                trace(run_id, "DEEP_TEXT", f"RESUME {chunk['chunk_id']} — уже обработан", "INFO", current=idx, total=total, name=chunk.get("section_title"))
            else:
                t0 = time.perf_counter()
                result = analyze_chunk(model, chunk)
                result["_chunk"] = {k:v for k,v in chunk.items() if k != "text"}
                result["_extractor"] = {"provider":model.get("provider"),"model":model.get("model"),"profile":profile,"analysis_fingerprint":analysis_key}
                write_json(result_path, result)
                elapsed = int((time.perf_counter() - t0) * 1000)
                trace(
                    run_id, "DEEP_TEXT",
                    f"ANALYZED {chunk['chunk_id']} — chars={chunk['char_count']} — events={len(result.get('events',[]))} — characters={len(result.get('characters',[]))}",
                    "PASS", current=idx, total=total, name=chunk.get("section_title"), duration_ms=elapsed,
                )
            if "_chunk" not in result:
                result["_chunk"] = {k:v for k,v in chunk.items() if k != "text"}
            extractions.append(result)
            chars_processed += chunk["char_count"]
            checkpoint.update({
                "status":"RUNNING",
                "last_completed":chunk["chunk_id"],
                "completed_chunks":sum(1 for p in chunk_dir.glob("*.json")),
                "chars_processed":chars_processed,
                "updated_at":now(),
            })
            write_json(checkpoint_path, checkpoint)

        with LOCK:
            RUNS[run_id].update({
                "stage":"MERGE","stage_label":"Сборка семантической БЗ","detail":"Объединяю персонажей, события, связи и мир","progress":94,
            })
        persist_run_state(run_id)
        merged = merge_extractions(extractions)

        write_json(project_dir / "kb" / "characters.json", merged["characters"])
        write_json(project_dir / "kb" / "events.json", merged["events"])
        write_json(project_dir / "kb" / "relations.json", merged["relations"])
        write_json(project_dir / "kb" / "locations.json", merged["locations"])
        write_json(project_dir / "kb" / "technologies.json", merged["technologies"])
        write_json(project_dir / "kb" / "organizations.json", merged["organizations"])
        write_json(project_dir / "kb" / "time_anchors.json", merged["time_anchors"])
        write_json(project_dir / "kb" / "deep_claims.json", merged["claims"])
        write_json(project_dir / "kb" / "open_threads.json", merged["open_threads"])

        graph_nodes = []
        graph_edges = []
        for idx, c in enumerate(merged["characters"], start=1):
            graph_nodes.append({"id":f"CHAR-{idx:05d}","type":"CHARACTER","label":c.get("name"),"chunks":c.get("chunks",[])})
        for idx, e in enumerate(merged["events"], start=1):
            graph_nodes.append({"id":f"EVT-{idx:06d}","type":"EVENT","label":e.get("event",""),"chunk_id":e.get("chunk_id")})
        for idx, rel in enumerate(merged["relations"], start=1):
            graph_edges.append({"id":f"REL-{idx:06d}","source":rel.get("source"),"target":rel.get("target"),"type":rel.get("relation_type"),"chunk_id":rel.get("chunk_id")})
        write_json(project_dir / "kb" / "deep_graph.json", {"nodes":graph_nodes,"edges":graph_edges})

        metrics = {
            "chunks":total,
            "chars_processed":chars_processed,
            "characters":len(merged["characters"]),
            "events":len(merged["events"]),
            "relations":len(merged["relations"]),
            "locations":len(merged["locations"]),
            "technologies":len(merged["technologies"]),
            "time_anchors":len(merged["time_anchors"]),
            "claims":len(merged["claims"]),
            "open_threads":len(merged["open_threads"]),
            "elapsed_seconds":round(time.perf_counter()-started, 1),
            "analysis_profile":profile,
            "analysis_fingerprint":analysis_key,
        }
        project_meta = read_json(project_dir / "project.json", {}) or {}
        project_meta["analysis_level"] = "DEEP_SEMANTIC"
        project_meta["deep_analysis_completed_at"] = now()
        project_meta["deep_model"] = model.get("model")
        project_meta["active_analysis_profile"] = profile
        project_meta["active_analysis_fingerprint"] = analysis_key
        project_meta["analysis_config"] = analysis_config
        project_meta["kb_version"] = int(project_meta.get("kb_version") or 0) + 1
        project_meta["updated_at"] = now()
        write_json(project_dir / "project.json", project_meta)

        with LOCK:
            RUNS[run_id].update({
                "stage":"DEEP_FINALIZE","stage_label":"Глубокий анализ завершён","detail":"Семантическая база знаний построена",
                "status":"PASS","progress":100,"metrics":metrics,"chars_processed":chars_processed,
            })
        persist_run_state(run_id)
        checkpoint.update({
            "status":"PASS",
            "completed_chunks":total,
            "last_completed":all_chunks[-1]["chunk_id"] if all_chunks else None,
            "chars_processed":chars_processed,
            "metrics":metrics,
            "updated_at":now(),
        })
        write_json(checkpoint_path, checkpoint)
        record_project_event(project_dir,"DEEP_ANALYSIS_FINISHED",status="PASS",details={
            "run_id":run_id,
            "analysis_key":analysis_key,
            "profile":profile,
            "metrics":metrics,
        })
        trace(run_id, "DEEP_FINALIZE", f"PASS: chunks={total}, characters={metrics['characters']}, events={metrics['events']}, relations={metrics['relations']}", "PASS")

    except Exception as exc:
        with LOCK:
            RUNS[run_id]["status"] = "FAIL"
            RUNS[run_id]["error"] = str(exc)
            RUNS[run_id]["detail"] = "Deep analysis failed"
        persist_run_state(run_id)
        try:
            cp_path = locals().get("checkpoint_path")
            cp = locals().get("checkpoint", {}) or {}
            if cp_path:
                cp.update({
                    "status":"FAIL",
                    "error":str(exc)[:1000],
                    "failed_at":now(),
                    "completed_chunks":sum(1 for p in locals().get("chunk_dir", Path()).glob("*.json")) if locals().get("chunk_dir") else 0,
                    "updated_at":now(),
                })
                write_json(cp_path, cp)
        except Exception:
            pass
        record_project_event(project_dir,"DEEP_ANALYSIS_FINISHED",status="FAIL",details={
            "run_id":run_id,
            "analysis_key":analysis_key,
            "profile":profile,
            "error":str(exc)[:500],
        })
        trace(run_id, RUNS[run_id].get("stage","DEEP"), str(exc), "ERROR")


@app.get("/api/deep/model-status")
def deep_model_status() -> JSONResponse:
    return JSONResponse(detect_local_model())


@app.post("/api/deep/select-gguf")
def select_gguf_model() -> JSONResponse:
    if os.name != "nt":
        raise HTTPException(400, "Автовыбор GGUF сейчас поддержан для Windows")
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Выберите локальную GGUF-модель для ALINA",
            filetypes=[("GGUF model", "*.gguf"), ("All files", "*.*")],
        )
        root.destroy()
    except Exception as exc:
        raise HTTPException(500, f"Не удалось открыть выбор модели: {exc}")
    if not path:
        return JSONResponse({"status":"CANCELLED", **detect_local_model()})
    save_model_config({"gguf_path": path, "selected_at": now(), "provider": "LLAMA_CPP"})
    return JSONResponse({"status":"SELECTED", **detect_local_model()})


@app.post("/api/deep/clear-model")
def clear_gguf_model() -> JSONResponse:
    config = load_model_config()
    config.pop("gguf_path", None)
    config["cleared_at"] = now()
    save_model_config(config)
    return JSONResponse({"status":"CLEARED", **detect_local_model()})


@app.post("/api/projects/{project_id}/import-alice-benchmark")
def import_alice_benchmark(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")

    seed_path = ROOT / "projects" / "sto_let_tomu_vpered" / "alice_cycle" / "alice_benchmark_seed.json"
    manifest_path = ROOT / "projects" / "sto_let_tomu_vpered" / "alice_cycle" / "alice_works_manifest.json"
    audit_path = ROOT / "projects" / "sto_let_tomu_vpered" / "alice_cycle" / "source_audits" / "alice_fb2_audit.json"
    if not seed_path.exists() or not manifest_path.exists() or not audit_path.exists():
        raise HTTPException(500, "Эталонный пакет Алисы неполон в репозитории")

    seed = read_json(seed_path, {}) or {}
    manifest = read_json(manifest_path, {}) or {}
    audit = read_json(audit_path, {}) or {}
    project_meta = read_json(project_dir / "project.json", {}) or {}
    sources = read_json(project_dir / "kb" / "sources.json", []) or []
    source_names = [str(x.get("filename") or "") for x in sources]
    source_probe = normalize_title(" ".join(source_names))

    is_alice = (
        "bulychev" in source_probe
        or "булычев" in source_probe
        or "841804" in source_probe
        or "алиса" in normalize_title(project_meta.get("title",""))
    )
    if not is_alice:
        raise HTTPException(409, "Проект не похож на корпус Алисы; benchmark не импортирован")

    has_star_dog_pdf = any(
        ("edition371535" in name.lower()) or ("звезд" in normalize_title(name) and "пес" in normalize_title(name))
        for name in source_names
    )
    matched_ids = set()
    missing = []
    for work in manifest.get("works", []):
        if work.get("work_id") == "ALICE-029":
            if has_star_dog_pdf:
                matched_ids.add("ALICE-029")
            else:
                missing.append({
                    "work_id":"ALICE-029",
                    "title":"Звёздный пёс",
                    "status":"MISSING_FROM_CURRENT_PROJECT_BUT_PRESENT_IN_BENCHMARK_AS_SEPARATE_SOURCE"
                })
        else:
            matched_ids.add(work.get("work_id"))

    works_seed = []
    for work in manifest.get("works", []):
        status = "BENCHMARK_MATCHED" if work.get("work_id") in matched_ids else "BENCHMARK_MISSING"
        works_seed.append({
            "work_id":work.get("work_id"),
            "title":work.get("title"),
            "aliases":work.get("aliases",[]),
            "publication_year":work.get("publication_year"),
            "form":work.get("form"),
            "status":status,
            "source":"MANUAL_VERIFIED_BENCHMARK"
        })

    imported = {
        "seed_id": seed.get("seed_id"),
        "status":"IMPORTED",
        "imported_at":now(),
        "project_id":project_id,
        "project_sources":source_names,
        "benchmark_status":"MANUAL_VERIFIED_BENCHMARK",
        "cycle_expected":manifest.get("catalog_count",52),
        "current_project_expected_matches":52 if has_star_dog_pdf else 51,
        "current_project_missing":missing,
        "source_audit":audit,
        "historical_deep_benchmark":seed.get("historical_deep_benchmark"),
        "star_dog_anchors":seed.get("star_dog_anchors"),
        "works":works_seed,
        "rule":"Benchmark data is reference/seed only. Current automated runs remain separately traceable."
    }

    write_json(project_dir / "kb" / "benchmark_seed.json", imported)

    current_works = read_json(project_dir / "kb" / "works.json", {}) or {}
    current_works["benchmark"] = {
        "seed_id":seed.get("seed_id"),
        "expected":manifest.get("catalog_count",52),
        "verified_in_big_fb2":audit.get("matched_works",51),
        "missing_from_big_fb2":audit.get("missing_from_source",[]),
        "separate_star_dog_source_present":has_star_dog_pdf,
        "expected_current_total":52 if has_star_dog_pdf else 51,
        "status":"MANUAL_VERIFIED_BENCHMARK"
    }
    write_json(project_dir / "kb" / "works.json", current_works)

    project_meta["benchmark_seed"] = seed.get("seed_id")
    project_meta["benchmark_status"] = "MANUAL_VERIFIED_BENCHMARK"
    project_meta["updated_at"] = now()
    write_json(project_dir / "project.json", project_meta)

    return JSONResponse(imported)


@app.post("/api/projects/{project_id}/import-alice-reference-analysis")
def import_alice_reference_analysis(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")

    meta = read_json(project_dir / "project.json", {}) or {}
    source_manifest = read_json(project_dir / "kb" / "source_manifest.json", {}) or {}
    probe = normalize_title(
        str(meta.get("title","")) + " " +
        " ".join(str(x.get("filename","")) for x in source_manifest.get("sources",[]))
    )
    if not any(token in probe for token in ("алиса","булычев","bulychev","841804")):
        raise HTTPException(409, "Reference analysis доступен только для корпуса Алисы")

    reference_root = ROOT / "projects" / "sto_let_tomu_vpered"
    source_files = {
        "canon_claims": reference_root / "canon" / "canon_claims.json",
        "entity_registry": reference_root / "canon" / "entity_registry.json",
        "event_store": reference_root / "canon" / "event_store.json",
        "relation_store": reference_root / "canon" / "relation_store.json",
        "knowledge_graph": reference_root / "canon" / "knowledge_graph.json",
        "temporal_model": reference_root / "canon" / "temporal_model.json",
        "state_store": reference_root / "canon" / "state_store.json",
        "state_transition_store": reference_root / "canon" / "state_transition_store.json",
        "causal_link_store": reference_root / "canon" / "causal_link_store.json",
        "hypothesis_candidates": reference_root / "canon" / "hypothesis_candidates.json",
        "prediction_run_manifest": reference_root / "canon" / "prediction_run_manifest.json",
        "backtest_manifest": reference_root / "canon" / "backtest_manifest.json",
        "quality_scorecard": reference_root / "reports" / "ALINA_QUALITY_SCORECARD.json",
    }

    missing = [name for name,path in source_files.items() if not path.exists()]
    if missing:
        raise HTTPException(500, "Reference analysis package incomplete: " + ", ".join(missing))

    out_dir = project_dir / "kb" / "reference_analysis" / "sto_let_tomu_vpered"
    out_dir.mkdir(parents=True, exist_ok=True)
    imported = {}
    for name,path in source_files.items():
        data = read_json(path, {}) or {}
        write_json(out_dir / f"{name}.json", data)
        imported[name] = {
            "source": str(path.relative_to(ROOT)).replace("\\","/"),
            "target": str((out_dir / f"{name}.json").relative_to(project_dir)).replace("\\","/"),
        }

    chunk_dir = reference_root / "evidence" / "chunk_claims_v2"
    chunk_files = sorted(chunk_dir.glob("primary-*.json"))
    target_chunks = out_dir / "chunk_claims_v2"
    target_chunks.mkdir(parents=True, exist_ok=True)
    for path in chunk_files:
        shutil.copy2(path, target_chunks / path.name)

    score = read_json(source_files["quality_scorecard"], {}) or {}
    summary = {
        "reference_id": "ALICE-STO-LET-TOMU-VPERED-359c692",
        "status": "REFERENCE_ANALYSIS_IMPORTED",
        "scope": "Сто лет тому вперёд",
        "provenance_commit": "359c692",
        "chunk_count": len(chunk_files),
        "maturity": score.get("current_maturity"),
        "prediction_maturity": score.get("prediction_learning_maturity"),
        "pipeline_counts": score.get("pipeline_counts",{}),
        "layer_status": score.get("layer_status",{}),
        "files": imported,
        "rule": "Reference analysis is trusted historical output and remains separate from current automated run.",
        "imported_at": now(),
    }
    write_json(out_dir / "reference_summary.json", summary)

    # Reflect verified historical capabilities in the work research program.
    research_program_path = project_dir / "research" / "ALICE-005" / "research_program.json"
    research_program = read_json(research_program_path, {}) or {}
    if research_program:
        pass_tasks = {
            "R02": "Historical chunk structure and paragraph boundaries available.",
            "R03": "565 claims extracted in historical run.",
            "R04": "Evidence Critic completed.",
            "R05": "Narrative Mode Guard completed.",
            "R06": "Canon Admission completed.",
            "R07": "Trusted entity registry available.",
            "R08": "Entity aliases/resolution registry available.",
            "R12": "State observations and transition layer available.",
            "R13": "Trusted relation store available.",
            "R14": "Trusted event store available.",
            "R15": "Textual event ordering available.",
            "R16": "Temporal anchors available; world-time normalization still immature.",
            "R24": "Causal layer completed with explicit causal links separated from adjacency.",
            "R25": "Contradiction engine completed.",
            "R29": "Hypothesis candidates available as forecast input, but predictions not mature.",
        }
        review_tasks = {
            "R01": "Historical analysis exists, but current project source identity must be revalidated.",
            "R09": "Character registry exists; full profile completeness not independently scored.",
            "R10": "Goals/motives were not a dedicated historical quality gate.",
            "R11": "Character knowledge model was not a dedicated historical quality gate.",
            "R17": "Locations were not a dedicated historical quality gate.",
            "R18": "Movement/travel was not a dedicated historical quality gate.",
            "R19": "World rules were not a dedicated historical quality gate.",
            "R20": "Technology registry was not a dedicated historical quality gate.",
            "R21": "Technology capability model was not a dedicated historical quality gate.",
            "R22": "Organizations were not a dedicated historical quality gate.",
            "R23": "Objects/artifacts were not a dedicated historical quality gate.",
            "R26": "Open threads were not a dedicated historical quality gate.",
            "R27": "Themes/narrative functions were not a dedicated historical quality gate.",
            "R28": "Sceneability/visual analysis was not part of the historical run.",
            "R30": "Historical maturity is trusted analytical foundation, but the new 30-task gate is not fully satisfied.",
        }

        for task in research_program.get("tasks", []):
            tid = task.get("task_id")
            if tid in pass_tasks:
                task["status"] = "PASS"
                task["progress"] = 100
                task["quality_gate"] = "PASS"
                task["metrics"]["reference_imported"] = True
                task["metrics"]["reference_commit"] = "359c692"
                task["outputs"] = ["kb/reference_analysis/sto_let_tomu_vpered"]
                task["blockers"] = []
                task["reference_note"] = pass_tasks[tid]
            elif tid in review_tasks:
                task["status"] = "REVIEW"
                task["progress"] = 50
                task["quality_gate"] = "REVIEW"
                task["metrics"]["reference_imported"] = True
                task["metrics"]["reference_commit"] = "359c692"
                task["blockers"] = ["NEW_RESEARCH_TASK_NOT_FULLY_COVERED_BY_HISTORICAL_RUN"]
                task["reference_note"] = review_tasks[tid]

        tasks = research_program.get("tasks", [])
        pass_count = sum(1 for t in tasks if t.get("status") == "PASS")
        review_count = sum(1 for t in tasks if t.get("status") == "REVIEW")
        blocked_count = sum(1 for t in tasks if t.get("status") == "BLOCKED")
        failed_count = sum(1 for t in tasks if t.get("status") == "FAILED")
        completed_equiv = pass_count + 0.5 * review_count
        research_program["program_status"] = "REVIEW"
        research_program["reference_analysis_id"] = summary["reference_id"]
        research_program["updated_at"] = now()
        research_program["summary"].update({
            "total": len(tasks),
            "planned": sum(1 for t in tasks if t.get("status") == "PLANNED"),
            "running": sum(1 for t in tasks if t.get("status") == "RUNNING"),
            "pass": pass_count,
            "review": review_count,
            "blocked": blocked_count,
            "failed": failed_count,
            "reused": 0,
            "completion_pct": round((completed_equiv / max(1,len(tasks))) * 100),
        })
        write_json(research_program_path, research_program)

        research_index_path = project_dir / "research" / "research_index.json"
        research_index = read_json(research_index_path, {}) or {}
        for row in research_index.get("programs", []):
            if row.get("work_id") == "ALICE-005":
                row["program_status"] = research_program["program_status"]
                row["summary"] = research_program["summary"]
        research_index["updated_at"] = now()
        write_json(research_index_path, research_index)

    meta["reference_analysis"] = {
        "id": summary["reference_id"],
        "scope": summary["scope"],
        "status": summary["status"],
        "chunk_count": summary["chunk_count"],
        "maturity": summary["maturity"],
    }
    meta["updated_at"] = now()
    write_json(project_dir / "project.json", meta)

    return JSONResponse(summary)


@app.post("/api/projects/{project_id}/deep-analysis")
async def start_deep_analysis(
    project_id: str,
    profile: str = Form("CANON_FULL"),
    config: str = Form("{}"),
) -> dict[str, Any]:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")

    active = [rid for rid, run in RUNS.items() if run.get("project_id")==project_id and run.get("status") in {"QUEUED","RUNNING"}]
    if active:
        raise HTTPException(409, f"У проекта уже идёт run: {active[0]}")

    meta = read_json(project_dir / "project.json", {}) or {}
    if meta.get("foundation_stale"):
        raise HTTPException(409, "Источники изменились. Сначала обновите первичную БЗ.")
    if not meta.get("foundation_fingerprint"):
        raise HTTPException(409, "Сначала выполните первичный разбор источников.")

    try:
        analysis_config = json.loads(config) if config else {}
    except Exception:
        raise HTTPException(400, "Некорректный JSON параметров анализа")

    model = detect_local_model()
    if not model.get("available"):
        return {
            "project_id": project_id,
            "status": "NEEDS_MODEL",
            "run_type": "DEEP_ANALYSIS",
            "model": model,
        }

    analysis_key = analysis_fingerprint(
        str(meta.get("source_fingerprint") or ""),
        profile,
        analysis_config,
        model,
    )

    if (
        analysis_key == str(meta.get("active_analysis_fingerprint") or "")
        and meta.get("analysis_level") == "DEEP_SEMANTIC"
        and (project_dir / "kb" / "characters.json").exists()
    ):
        return {
            "project_id": project_id,
            "status": "REUSED",
            "run_type": "DEEP_ANALYSIS",
            "reason": "SOURCE_AND_ANALYSIS_PARAMETERS_UNCHANGED",
            "analysis_profile": profile,
            "analysis_fingerprint": analysis_key,
            "kb_version": meta.get("kb_version", 0),
            "model": model.get("model"),
        }

    run_id = f"DEEP-{uuid.uuid4().hex[:12]}"
    RUNS[run_id] = {
        "run_id":run_id,
        "run_type":"DEEP_ANALYSIS",
        "project_id":project_id,
        "project_title":meta.get("title","Проект"),
        "analysis_profile":profile,
        "analysis_config":analysis_config,
        "analysis_fingerprint":analysis_key,
        "status":"QUEUED",
        "progress":0,
        "stage_index":0,
        "stage":"QUEUED",
        "stage_label":"Глубокий анализ в очереди",
        "detail":"Ожидание запуска",
        "trace":[],
        "metrics":{},
        "created_at":now(),
        "updated_at":now(),
        "error":None,
        "current_item":0,
        "current_total":0,
        "current_name":"",
        "chars_processed":0,
    }
    persist_run_state(run_id)
    threading.Thread(
        target=run_deep_analysis,
        args=(run_id,project_dir,analysis_key,profile,analysis_config),
        daemon=True,
    ).start()
    return {
        "project_id":project_id,
        "run_id":run_id,
        "status":"QUEUED",
        "run_type":"DEEP_ANALYSIS",
        "analysis_profile":profile,
        "analysis_fingerprint":analysis_key,
    }

@app.post("/api/debug/trace")
async def debug_trace_event(
    event: str = Form(...),
    payload: str = Form("{}"),
) -> JSONResponse:
    try:
        data = json.loads(payload) if payload else {}
    except Exception:
        data = {}

    settings = load_admin_settings()
    record = None
    if settings.get("local_trace", True):
        record = append_debug_trace({
            "event_type": event,
            **(data if isinstance(data, dict) else {}),
        })

    if settings.get("github_debug_trace", False):
        publish_debug_trace_background()
    else:
        with DEBUG_GIT_STATE_LOCK:
            DEBUG_GIT_STATE["status"] = "DISABLED"
            DEBUG_GIT_STATE["updated_at"] = now()
            DEBUG_GIT_STATE["error"] = None

    with DEBUG_GIT_STATE_LOCK:
        git_state = dict(DEBUG_GIT_STATE)

    return JSONResponse({
        "status":"RECORDED" if record else "LOCAL_TRACE_DISABLED",
        "record":record,
        "github":git_state,
        "admin_settings":settings,
    })

@app.get("/api/admin/settings")
def get_admin_settings() -> JSONResponse:
    return JSONResponse(load_admin_settings())


@app.patch("/api/admin/settings")
async def update_admin_settings(
    github_debug_trace: bool | None = Form(None),
    local_trace: bool | None = Form(None),
) -> JSONResponse:
    settings = load_admin_settings()
    if github_debug_trace is not None:
        settings["github_debug_trace"] = github_debug_trace
    if local_trace is not None:
        settings["local_trace"] = local_trace
    saved = save_admin_settings(settings)

    if not saved.get("github_debug_trace", False):
        with DEBUG_GIT_STATE_LOCK:
            DEBUG_GIT_STATE["status"] = "DISABLED"
            DEBUG_GIT_STATE["updated_at"] = now()
            DEBUG_GIT_STATE["error"] = None

    append_debug_trace({
        "event_type":"ADMIN_SETTINGS",
        "status":"PASS",
        "result":"GITHUB_TRACE_ON" if saved.get("github_debug_trace") else "GITHUB_TRACE_OFF",
    })
    return JSONResponse(saved)


@app.get("/api/debug/trace")
def get_debug_trace(limit: int = 200) -> JSONResponse:
    if not DEBUG_TRACE_FILE.exists():
        return JSONResponse([])
    lines = DEBUG_TRACE_FILE.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines[-max(1,min(limit,1000)):]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return JSONResponse(rows)


@app.get("/api/debug/github-status")
def debug_github_status() -> JSONResponse:
    settings = load_admin_settings()
    with DEBUG_GIT_STATE_LOCK:
        state = dict(DEBUG_GIT_STATE)
    state["enabled"] = bool(settings.get("github_debug_trace", False))
    if not state["enabled"]:
        state["status"] = "DISABLED"
    return JSONResponse(state)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "PRIVATE_LOCAL",
        "api_version": "0.3.0-project-contract",
        "project_create_route": "POST /api/projects",
        "data_root": str(DATA_ROOT),
    }


@app.post("/api/projects")
async def create_empty_project(
    title: str = Form(...),
    mode: str = Form("study-cycle"),
    intent: str = Form(""),
    description: str = Form(""),
) -> JSONResponse:
    clean_title = title.strip()
    if not clean_title:
        raise HTTPException(400, "Сначала задайте название проекта")

    project_id = f"PRJ-{uuid.uuid4().hex[:10]}"
    project_dir = PROJECTS_ROOT / project_id
    for folder in ("sources", "kb", "runs", "deep", "products", "research"):
        (project_dir / folder).mkdir(parents=True, exist_ok=True)

    short_code = next_project_short_code()
    metadata = {
        "project_id": project_id,
        "short_code": short_code,
        "title": clean_title,
        "title_mode": "MANUAL",
        "mode": mode,
        "intent": intent,
        "description": description.strip() or intent.strip(),
        "privacy": "PRIVATE_LOCAL",
        "status": "PROJECT_CREATED",
        "analysis_level": "NONE",
        "source_count": 0,
        "source_set_version": 0,
        "source_fingerprint": "",
        "foundation_fingerprint": "",
        "kb_version": 0,
        "active_analysis_profile": None,
        "created_at": now(),
        "updated_at": now(),
    }
    write_json(project_dir / "project.json", metadata)
    write_json(project_dir / "kb" / "project_contract.json", {
        "project_id": project_id,
        "title": clean_title,
        "description": description.strip() or intent.strip(),
        "contract_version": "1.2",
        "short_code": short_code,
        "folders": ["sources", "kb", "runs", "deep", "products", "research"],
        "service_files": ["project_state.json","project_events.jsonl"],
        "created_at": metadata["created_at"],
        "status": "READY_FOR_SOURCES",
    })
    record_project_event(project_dir,"PROJECT_CREATED",details={
        "project_id":project_id,"short_code":short_code,"title":clean_title,"mode":mode
    })
    return JSONResponse({**metadata,"project_state":read_json(project_state_path(project_dir),{})})


@app.post("/api/projects/{project_id}/sources")
async def add_project_sources(
    project_id: str,
    files: list[UploadFile] = File(...),
) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    meta_path = project_dir / "project.json"
    meta = read_json(meta_path, None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    if not files:
        raise HTTPException(400, "Нет файлов")

    sources_dir = project_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for upload in files:
        safe = Path(upload.filename or "source.bin").name
        dest = sources_dir / safe
        with dest.open("wb") as out:
            shutil.copyfileobj(upload.file, out)
        saved.append({
            "filename": safe,
            "size_bytes": dest.stat().st_size,
            "extension": dest.suffix.lower(),
            "sha256": sha256(dest),
        })

    all_files = [p for p in sources_dir.iterdir() if p.is_file()]
    new_fingerprint = source_set_fingerprint(all_files)
    old_fingerprint = str(meta.get("source_fingerprint") or "")
    source_changed = new_fingerprint != old_fingerprint

    meta["source_count"] = len(all_files)
    meta["source_fingerprint"] = new_fingerprint
    if source_changed:
        meta["source_set_version"] = int(meta.get("source_set_version") or 0) + 1
        meta["foundation_stale"] = True
        meta["status"] = "SOURCES_CHANGED" if old_fingerprint else "SOURCES_ATTACHED"
    else:
        meta["status"] = meta.get("status") or "SOURCES_ATTACHED"
    meta["updated_at"] = now()
    write_json(meta_path, meta)
    write_json(project_dir / "kb" / "source_manifest.json", {
        "project_id": project_id,
        "source_count": len(all_files),
        "source_set_version": meta.get("source_set_version"),
        "source_fingerprint": new_fingerprint,
        "changed": source_changed,
        "sources": [
            {
                "filename": p.name,
                "size_bytes": p.stat().st_size,
                "extension": p.suffix.lower(),
                "sha256": sha256(p),
                "added_at": now(),
            }
            for p in all_files
        ],
        "updated_at": now(),
    })
    event = record_project_event(project_dir,"SOURCES_ATTACHED",details={
        "added":[{"filename":x.get("filename"),"size_bytes":x.get("size_bytes"),"sha256":x.get("sha256")} for x in saved],
        "source_count":len(all_files),
        "source_set_version":meta.get("source_set_version"),
        "source_fingerprint":new_fingerprint,
        "source_changed":source_changed,
    })
    return JSONResponse({
        "project": meta,
        "added": saved,
        "source_changed": source_changed,
        "source_fingerprint": new_fingerprint,
        "project_state": read_json(project_state_path(project_dir),{}),
        "event":event,
    })


@app.post("/api/projects/{project_id}/foundation-analysis")
def start_foundation_analysis(project_id: str) -> dict[str, Any]:
    project_dir = PROJECTS_ROOT / project_id
    meta = read_json(project_dir / "project.json", None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    source_files = [p for p in (project_dir / "sources").iterdir() if p.is_file()]
    if not source_files:
        raise HTTPException(400, "Сначала добавьте книги в проект")

    current_fingerprint = source_set_fingerprint(source_files)
    if (
        current_fingerprint
        and current_fingerprint == str(meta.get("foundation_fingerprint") or "")
        and meta.get("analysis_level") in {"FOUNDATION_ONLY", "DEEP_SEMANTIC"}
        and (project_dir / "kb" / "structure.json").exists()
    ):
        return {
            "project_id": project_id,
            "status": "REUSED",
            "run_type": "FOUNDATION_ANALYSIS",
            "reason": "SOURCE_SET_UNCHANGED",
            "source_fingerprint": current_fingerprint,
            "kb_version": meta.get("kb_version", 0),
        }

    active = [rid for rid, run in RUNS.items() if run.get("project_id")==project_id and run.get("status") in {"QUEUED","RUNNING"}]
    if active:
        raise HTTPException(409, f"У проекта уже идёт run: {active[0]}")

    run_id = f"RUN-{uuid.uuid4().hex[:12]}"
    RUNS[run_id] = {
        "run_id": run_id,
        "run_type": "FOUNDATION_ANALYSIS",
        "project_id": project_id,
        "project_title": meta.get("title"),
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
        "current_item": 0,
        "current_total": 0,
        "current_name": "",
    }
    persist_run_state(run_id)
    record_project_event(project_dir,"FOUNDATION_QUEUED",status="QUEUED",details={"run_id":run_id})
    threading.Thread(
        target=run_ingest,
        args=(run_id, project_dir, source_files, meta.get("title","Проект")),
        daemon=True,
    ).start()
    return {"project_id":project_id,"run_id":run_id,"status":"QUEUED","run_type":"FOUNDATION_ANALYSIS"}


@app.post("/api/projects/ingest")
async def create_project(
    title: str = Form(""),
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

    auto_title = infer_title_from_files(saved)
    effective_title = title.strip() or auto_title
    metadata = {
        "project_id": project_id,
        "title": effective_title,
        "title_mode": "MANUAL" if title.strip() else "AUTO",
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
        "project_title": effective_title,
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
        "current_item": 0,
        "current_total": 0,
        "current_name": "",
    }
    threading.Thread(target=run_ingest, args=(run_id, project_dir, saved, effective_title), daemon=True).start()
    return {"project_id": project_id, "run_id": run_id, "status": "QUEUED", "title": effective_title, "title_mode": metadata["title_mode"]}


@app.get("/api/runs/{run_id}")
def run_status(run_id: str) -> dict[str, Any]:
    with LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(404, "Run не найден")
        return json.loads(json.dumps(run, ensure_ascii=False))


@app.get("/api/projects/{project_id}/kb/{name}")
def get_kb(project_id: str, name: str) -> JSONResponse:
    allowed = {"sources","structure","works","claims","entities","events","world","graph","conflicts","review_queue","characters","relations","locations","technologies","organizations","time_anchors","deep_claims","open_threads","deep_graph","benchmark_seed"}
    if name not in allowed:
        raise HTTPException(404, "Неизвестный раздел БЗ")
    path = PROJECTS_ROOT / project_id / "kb" / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, "Раздел ещё не создан")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/projects")
def list_projects() -> JSONResponse:
    projects = []
    for project_dir in PROJECTS_ROOT.iterdir():
        if not project_dir.is_dir():
            continue
        meta = read_json(project_dir / "project.json", {}) or {}
        if not meta:
            continue
        if not meta.get("short_code"):
            meta["short_code"] = next_project_short_code()
            meta["updated_at"] = now()
            write_json(project_dir / "project.json", meta)
        run_files = sorted((project_dir / "runs").glob("*.state.json")) if (project_dir / "runs").exists() else []
        runs = [read_json(p, {}) or {} for p in run_files]
        runs = [r for r in runs if r]
        runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        latest = runs[0] if runs else None
        if not meta.get("description"):
            meta["description"] = str(meta.get("intent") or "").strip()
        state = rebuild_project_state(project_dir)
        projects.append({
            **meta,
            "project_state": state,
            "source_count": state.get("source_set",{}).get("count", meta.get("source_count",0)),
            "analysis_level": meta.get("analysis_level", "NONE"),
            "product_count": len(project_products(project_dir)),
            "products": project_products(project_dir),
            "folders": {
                "project": str(project_dir),
                "sources": str(project_dir / "sources"),
                "knowledge_base": str(project_dir / "kb"),
                "runs": str(project_dir / "runs"),
                "products": str(project_dir / "products"),
            },
            "run_count": len(runs),
            "latest_run": {
                "run_id": latest.get("run_id"),
                "status": latest.get("status"),
                "progress": latest.get("progress"),
                "created_at": latest.get("created_at"),
                "updated_at": latest.get("updated_at"),
                "metrics": latest.get("metrics", {}),
            } if latest else None,
        })
    projects.sort(key=lambda x: x.get("updated_at") or x.get("created_at") or "", reverse=True)
    return JSONResponse(projects)


@app.post("/api/projects/{project_id}/open-folder/{folder_name}")
def open_project_folder(project_id: str, folder_name: str) -> dict[str, Any]:
    project_dir = PROJECTS_ROOT / project_id
    folders = {
        "project": project_dir,
        "sources": project_dir / "sources",
        "kb": project_dir / "kb",
        "runs": project_dir / "runs",
        "products": project_dir / "products",
        "research": project_dir / "research",
    }
    target = folders.get(folder_name)
    if target is None:
        raise HTTPException(404, "Неизвестная папка")
    target.mkdir(parents=True, exist_ok=True)
    try:
        if os.name == "nt":
            os.startfile(str(target))
        else:
            subprocess.Popen(["xdg-open", str(target)])
    except Exception as exc:
        raise HTTPException(500, f"Не удалось открыть папку: {exc}")
    return {"status": "OPENED", "folder": folder_name, "path": str(target)}


@app.get("/api/projects/{project_id}/runs")
def project_runs(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    run_dir = project_dir / "runs"
    runs = []
    if run_dir.exists():
        for path in run_dir.glob("*.state.json"):
            item = read_json(path, {}) or {}
            if item:
                runs.append(item)
    runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return JSONResponse(runs)


@app.get("/api/projects/{project_id}/research")
def get_project_research_dashboard(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(research_dashboard(project_dir))


@app.get("/api/projects/{project_id}/research/{work_id}")
def get_work_research_program(project_id: str, work_id: str) -> JSONResponse:
    path = PROJECTS_ROOT / project_id / "research" / work_id / "research_program.json"
    if not path.exists():
        raise HTTPException(404, "Исследовательская программа произведения не найдена")
    return JSONResponse(read_json(path, {}) or {})


@app.post("/api/projects/{project_id}/research/{work_id}/tasks/{task_id}/run")
def run_work_research_task(project_id: str, work_id: str, task_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(execute_research_task(project_dir, work_id, task_id))


@app.post("/api/projects/{project_id}/research/{work_id}/next")
def run_next_work_research_task(project_id: str, work_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(execute_next_research_task(project_dir, work_id))


@app.post("/api/projects/{project_id}/research/{work_id}/auto")
def run_work_research_auto(project_id: str, work_id: str, max_steps: int = 30) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(execute_research_auto(project_dir, work_id, max_steps=max_steps))


@app.get("/api/projects/{project_id}/research/{work_id}/graph")
def get_work_research_graph(project_id: str, work_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    path = project_dir / "research" / work_id / "outputs" / "research_graph.json"
    if not path.exists():
        raise HTTPException(404, "Research graph ещё не построен")
    return JSONResponse(read_json(path, {}) or {})


@app.post("/api/projects/{project_id}/research/rebuild")
def rebuild_project_research_complex(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    meta = read_json(project_dir / "project.json", None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    works = read_json(project_dir / "kb" / "works.json", {}) or {}
    result = initialize_project_research_complex(project_dir, meta, works)
    return JSONResponse(result)


@app.get("/api/projects/{project_id}/products")
def list_project_products(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(project_products(project_dir))


@app.post("/api/projects/{project_id}/products")
async def create_creative_product(
    project_id: str,
    product_type: str = Form(...),
    title: str = Form(...),
    profile: str = Form(""),
    config: str = Form("{}"),
) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    meta = read_json(project_dir / "project.json", None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    if meta.get("analysis_level") not in {"FOUNDATION_ONLY", "DEEP_SEMANTIC"}:
        raise HTTPException(409, "Сначала постройте базу знаний проекта")

    products_dir = project_dir / "products"
    products_dir.mkdir(parents=True, exist_ok=True)
    products = project_products(project_dir)
    type_prefix = {
        "BOOK":"B", "COMIC":"C", "VISUAL_NOVEL":"VN", "SHORT_VIDEO":"V",
        "FILM":"F", "GAME_SCENARIO":"G",
    }.get(product_type.upper(), "P")
    same_type = [p for p in products if str(p.get("product_id","")).startswith(type_prefix)]
    product_id = f"{type_prefix}{len(same_type)+1}"
    try:
        parsed_config = json.loads(config)
    except Exception:
        parsed_config = {}

    product = {
        "product_id": product_id,
        "project_id": project_id,
        "project_short_code": meta.get("short_code"),
        "type": product_type.upper(),
        "title": title.strip() or product_id,
        "profile": profile or f"{product_type.upper()}_PREP",
        "source_kb_version": meta.get("kb_version", 0),
        "source_fingerprint": meta.get("source_fingerprint", ""),
        "status": "DRAFT",
        "config": parsed_config,
        "pipeline": [
            "AUTHOR_INTENT","STORY_ARC","SCENES","VISUAL_BIBLE",
            "PROMPT_PACK","RAG_CONTEXT","GENERATION","CONTINUITY_QC"
        ],
        "created_at": now(),
        "updated_at": now(),
    }
    (products_dir / product_id).mkdir(parents=True, exist_ok=True)
    write_json(products_dir / product_id / "product.json", product)
    products.append(product)
    write_json(products_dir / "index.json", products)
    meta["updated_at"] = now()
    write_json(project_dir / "project.json", meta)
    record_project_event(project_dir,"PRODUCT_CREATED",details={
        "product_id":product_id,"type":product.get("type"),"title":product.get("title")
    })
    return JSONResponse(product)


@app.delete("/api/projects/{project_id}/runs/{run_id}")
def delete_project_run(project_id: str, run_id: str) -> dict[str, Any]:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    active = RUNS.get(run_id)
    if active and active.get("status") in {"QUEUED", "RUNNING"}:
        raise HTTPException(409, "Нельзя удалить выполняющийся run")
    removed = []
    for candidate in [
        project_dir / "runs" / f"{run_id}.state.json",
        project_dir / "runs" / f"{run_id}.json",
    ]:
        if candidate.exists():
            candidate.unlink()
            removed.append(candidate.name)
    with LOCK:
        RUNS.pop(run_id, None)
    if not removed:
        raise HTTPException(404, "Run не найден")
    return {"status": "DELETED", "project_id": project_id, "run_id": run_id, "files": removed}


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str) -> dict[str, Any]:
    project_dir = PROJECTS_ROOT / project_id
    if not project_dir.exists():
        raise HTTPException(404, "Проект не найден")
    active = [rid for rid, run in RUNS.items() if run.get("project_id") == project_id and run.get("status") in {"QUEUED", "RUNNING"}]
    if active:
        raise HTTPException(409, f"Проект сейчас выполняется: {', '.join(active)}")
    shutil.rmtree(project_dir)
    with LOCK:
        for rid in [rid for rid, run in RUNS.items() if run.get("project_id") == project_id]:
            RUNS.pop(rid, None)
    return {"status": "DELETED", "project_id": project_id}


@app.patch("/api/projects/{project_id}/description")
async def update_project_description(project_id: str, description: str = Form(...)) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    path = project_dir / "project.json"
    meta = read_json(path, None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    meta["description"] = description.strip()[:500]
    meta["updated_at"] = now()
    write_json(path, meta)
    record_project_event(project_dir,"PROJECT_DESCRIPTION_UPDATED",details={"description":meta.get("description","")[:500]})
    return JSONResponse(meta)


@app.patch("/api/projects/{project_id}/title")
async def rename_project(project_id: str, title: str = Form(...)) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    path = project_dir / "project.json"
    meta = read_json(path, None)
    if meta is None:
        raise HTTPException(404, "Проект не найден")
    clean = title.strip()
    if not clean:
        raise HTTPException(400, "Название пустое")
    meta["title"] = clean
    meta["title_mode"] = "MANUAL"
    meta["updated_at"] = now()
    write_json(path, meta)
    record_project_event(project_dir,"PROJECT_TITLE_UPDATED",details={"title":clean})
    return JSONResponse(meta)


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    path = project_dir / "project.json"
    if not path.exists():
        raise HTTPException(404, "Проект не найден")
    meta = read_json(path,{}) or {}
    state = rebuild_project_state(project_dir)
    return JSONResponse({
        **meta,
        "saved_sources":state.get("source_set",{}).get("sources",[]),
        "project_state":state,
    })


@app.get("/api/projects/{project_id}/state")
def get_project_state(project_id: str) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not (project_dir / "project.json").exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(rebuild_project_state(project_dir))


@app.get("/api/projects/{project_id}/events")
def get_project_events(project_id: str, limit: int = 200) -> JSONResponse:
    project_dir = PROJECTS_ROOT / project_id
    if not (project_dir / "project.json").exists():
        raise HTTPException(404, "Проект не найден")
    return JSONResponse(read_project_events(project_dir,limit=limit))
