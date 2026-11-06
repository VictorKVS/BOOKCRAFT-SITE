from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from alina_book2.llm_runtime import LLMWriter, Producer
from alina_book2.semantic_guard import SemanticCritic, SemanticRepair
from alina_book2.story_ingest import IngestValidator, StoryIngestor


class FullStoryContinuationPipeline:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.ingestor = StoryIngestor(model)
        self.validator = IngestValidator()
        self.producer = Producer()
        self.writer = LLMWriter(model)
        self.semantic = SemanticCritic(model)
        self.semantic_repair = SemanticRepair(model)

    def _prepare_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = deepcopy(state)

        if not state.get("default_pov"):
            characters = state.get("characters", {})
            if not characters:
                raise ValueError("No characters available for POV selection")
            state["default_pov"] = next(iter(characters.keys()))

        # llm_runtime currently expects a dict for secrets.
        # Preserve extracted secrets separately and keep runtime-compatible state.
        extracted_secrets = state.get("secrets", [])
        if isinstance(extracted_secrets, list):
            state["extracted_secrets"] = extracted_secrets
            state["secrets"] = {}

        state.setdefault("events", [])
        state.setdefault("plot_threads", [])
        state.setdefault("objects", {})
        return state

    def run(self, source_path: str | Path, objective: str) -> Dict[str, Any]:
        path = Path(source_path)
        source_text = path.read_text(encoding="utf-8")

        state = self.ingestor.ingest_file(path)
        state = self.validator.repair_evidence(state, source_text)
        validation = self.validator.validate(state, source_text)
        if not validation["ok"]:
            return {
                "ok": False,
                "status": "INGEST_INVALID",
                "validation": validation,
                "state": state,
            }

        state = self._prepare_state(state)
        scene = self.producer.plan_scene(state, objective)
        draft = self.writer.draft(scene, state)

        first = self.semantic.review(scene, state, draft)
        repaired = False

        if first.get("decision") == "REPAIR":
            draft = self.semantic_repair.repair(scene, state, draft, first)
            repaired = True

        second = self.semantic.review(scene, state, draft)

        if second.get("decision") != "PASS":
            return {
                "ok": False,
                "status": "SEMANTIC_BLOCKED",
                "state": state,
                "scene": scene,
                "draft": draft,
                "first_semantic_report": first,
                "final_semantic_report": second,
                "repaired": repaired,
            }

        return {
            "ok": True,
            "status": "ACCEPTED_CONTINUATION",
            "state": state,
            "scene": scene,
            "draft": draft,
            "first_semantic_report": first,
            "final_semantic_report": second,
            "repaired": repaired,
            "ingest_validation": validation,
        }
