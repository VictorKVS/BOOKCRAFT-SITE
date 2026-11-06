from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

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
- evidence копируй ДОСЛОВНО из исходного текста;
- не заменяй местоимения именами и не исправляй формулировки внутри evidence;
- если для события нужно несколько фрагментов, выбери один наиболее прямой короткий фрагмент;
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
    @staticmethod
    def _norm(text: str) -> str:
        return " ".join((text or "").split())

    @staticmethod
    def _source_sentences(source_text: str) -> List[str]:
        parts = re.split(r"(?<=[.!?])\s+", IngestValidator._norm(source_text))
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _ground_evidence(evidence: str, source_text: str) -> Tuple[str | None, float]:
        e = IngestValidator._norm(evidence)
        source_norm = IngestValidator._norm(source_text)

        if not e:
            return None, 0.0

        if e in source_norm:
            return e, 1.0

        sentences = IngestValidator._source_sentences(source_text)
        if not sentences:
            return None, 0.0

        best = None
        best_score = 0.0
        for sentence in sentences:
            score = SequenceMatcher(None, e.lower(), sentence.lower()).ratio()
            if score > best_score:
                best = sentence
                best_score = score

        return (best, best_score) if best_score >= 0.72 else (None, best_score)

    def repair_evidence(self, state: Dict[str, Any], source_text: str) -> Dict[str, Any]:
        repaired = json.loads(json.dumps(state, ensure_ascii=False))
        repairs = []

        for bucket in ("locations", "events", "facts"):
            for item in repaired.get(bucket, []):
                evidence = (item.get("evidence") or "").strip()
                if not evidence:
                    continue

                grounded, score = self._ground_evidence(evidence, source_text)
                if grounded and self._norm(evidence) != grounded:
                    item["evidence_original"] = evidence
                    item["evidence"] = grounded
                    item["evidence_grounding"] = {
                        "method": "source_sentence_alignment",
                        "similarity": round(score, 3),
                    }
                    repairs.append({
                        "bucket": bucket,
                        "id": item.get("id") or item.get("event_id") or item.get("fact_id"),
                        "from": evidence,
                        "to": grounded,
                        "similarity": round(score, 3),
                    })

        repaired["evidence_repairs"] = repairs
        return repaired

    def validate(self, state: Dict[str, Any], source_text: str) -> Dict[str, Any]:
        issues = []

        if not state.get("characters"):
            issues.append("NO_CHARACTERS")
        if not state.get("events"):
            issues.append("NO_EVENTS")

        source_norm = self._norm(source_text)
        source_norm_lower = source_norm.lower()
        evidence_items = []
        for item in state.get("locations", []):
            evidence_items.append(item.get("evidence", ""))
        for item in state.get("events", []):
            evidence_items.append(item.get("evidence", ""))
        for item in state.get("facts", []):
            evidence_items.append(item.get("evidence", ""))

        unsupported = []
        for evidence in evidence_items:
            e = self._norm(evidence)
            if e and e.lower() not in source_norm_lower:
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
