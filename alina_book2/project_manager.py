from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_TYPES = {
    "SINGLE_BOOK",
    "MULTI_VOLUME_BOOK",
    "BOOK_SERIES",
    "UNIVERSE",
    "COMPARATIVE_STUDY",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9а-яё_-]+", "-", value, flags=re.IGNORECASE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "project"


class AnalysisProjectManager:
    def __init__(self, root: str | Path = "projects"):
        self.root = Path(root)

    def create_project(
        self,
        project_id: str,
        title: str,
        project_type: str = "SINGLE_BOOK",
        language: str = "ru",
    ) -> Path:
        if project_type not in PROJECT_TYPES:
            raise ValueError(f"Unsupported project_type: {project_type}")

        pid = slugify(project_id)
        project_dir = self.root / pid

        if (project_dir / "project.json").exists():
            raise FileExistsError(f"Project already exists: {pid}")

        for relative in (
            "sources",
            "structure",
            "state",
            "graph",
            "evidence",
            "reports",
            "branches",
            "runs",
        ):
            (project_dir / relative).mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()
        manifest: Dict[str, Any] = {
            "project_id": pid,
            "title": title,
            "project_type": project_type,
            "language": language,
            "status": "CREATED",
            "created_at": now,
            "updated_at": now,
            "source_files": [],
            "structure": {
                "volumes": 0,
                "parts": 0,
                "chapters": 0,
                "scenes": 0,
            },
            "models": {
                "analyst": "qwen2.5:7b",
                "writer": "qwen2.5:7b",
                "semantic_critic": "qwen2.5:7b",
            },
            "settings": {
                "evidence_required": True,
                "strict_character_knowledge": True,
                "strict_canon": True,
                "allow_branching": True,
            },
        }

        (project_dir / "project.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return project_dir

    def list_projects(self) -> list[Dict[str, Any]]:
        if not self.root.exists():
            return []

        projects = []
        for manifest_path in sorted(self.root.glob("*/project.json")):
            try:
                projects.append(json.loads(manifest_path.read_text(encoding="utf-8")))
            except Exception:
                projects.append({
                    "project_id": manifest_path.parent.name,
                    "status": "BROKEN_MANIFEST",
                })
        return projects
