from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from alina_book2.llm_runtime import ollama_generate


class StoryIngestor:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model

    def ingest_text(self, text: str, source_id: str = "story") -> Dict[str, Any]:
        prompt = f"""
Ты ALINA ANALYST v2.

Преобразуй художественный фрагмент в структурированное Narrative State.

ИСТОЧНИК ID: {source_id}

ТЕКСТ:
{text}

Верни ТОЛЬКО JSON строго такого вида:
{{
  "source_id": "{source_id}",
  "characters": {{
    "id": {{
      "name": "...",
      "aliases": [],
      "location": "...",
      "knowledge": [],
      "beliefs": [],
      "goals": [],
      "status": "active"
    }}
  }},
  "locations": [
    {{
      "id": "...",
      "name": "...",
      "evidence": "точная короткая цитата из исходного текста"
    }}
  ],
  "events": [
    {{
      "event_id": "...",
      "summary": "...",
      "participants": [],
      "location": "...",
      "causes": [],
      "consequences": [],
      "evidence": "точная короткая цитата из исходного текста"
    }}
  ],
  "facts": [
    {{
      "fact_id": "...",
      "statement": "...",
      "status": "CONFIRMED",
      "evidence": "точная короткая цитата из исходного текста"
    }}
  ],
  "secrets": [],
  "plot_threads": [],
  "unresolved_questions": []
}}

Правила:
- не придумывай факты, которых нет в тексте;
- знание персонажа отделяй от объективного факта;
- если неизвестно — оставляй пусто;
- evidence должен быть привязан к исходному тексту;
- идентификаторы делай короткими и стабильными;
- не возвращай markdown.
""".strip()

        raw = ollama_generate(self.model, prompt)
        data = self._parse_json(raw)
        return self._normalize(data, source_id)

    def ingest_file(self, path: str | Path) -> Dict[str, Any]:
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        return self.ingest_text(text, source_id=p.name)

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except Exception:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            raise ValueError("ALINA Analyst did not return valid JSON")

    @staticmethod
    def _normalize(data: Dict[str, Any], source_id: str) -> Dict[str, Any]:
        state = {
            "version": 1,
            "source_id": source_id,
            "characters": data.get("characters", {}),
            "locations": data.get("locations", []),
            "events": data.get("events", []),
            "facts": data.get("facts", []),
            "secrets": data.get("secrets", []),
            "plot_threads": data.get("plot_threads", []),
            "unresolved_questions": data.get("unresolved_questions", []),
            "relations": [],
            "objects": {},
            "continuity_flags": [],
        }
        return state


class IngestValidator:
    def validate(self, state: Dict[str, Any], source_text: str) -> Dict[str, Any]:
        issues = []

        if not state.get("characters"):
            issues.append("NO_CHARACTERS")
        if not state.get("events"):
            issues.append("NO_EVENTS")

        evidence_items = []
        for item in state.get("locations", []):
            evidence_items.append(item.get("evidence", ""))
        for item in state.get("events", []):
            evidence_items.append(item.get("evidence", ""))
        for item in state.get("facts", []):
            evidence_items.append(item.get("evidence", ""))

        unsupported = []
        for evidence in evidence_items:
            e = (evidence or "").strip()
            if e and e not in source_text:
                unsupported.append(e)

        if unsupported:
            issues.append("EVIDENCE_NOT_IN_SOURCE")

        return {
            "ok": not issues,
            "issues": issues,
            "unsupported_evidence": unsupported,
            "counts": {
                "characters": len(state.get("characters", {})),
                "events": len(state.get("events", [])),
                "locations": len(state.get("locations", [])),
                "facts": len(state.get("facts", [])),
            },
        }
