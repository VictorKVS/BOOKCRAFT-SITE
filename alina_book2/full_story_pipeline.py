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

    def _semantic_gate(self, scene: Dict[str, Any], state: Dict[str, Any], draft: Dict[str, Any], max_repairs: int = 3) -> Dict[str, Any]:
        history = []
        current = draft
        repaired = False

        for attempt in range(max_repairs + 1):
            report = self.semantic.review(scene, state, current)
            history.append(report)

            if report.get("decision") == "PASS":
                return {
                    "ok": True,
                    "draft": current,
                    "repaired": repaired,
                    "attempts": attempt,
                    "history": history,
                    "final_report": report,
                }

            if attempt >= max_repairs:
                break

            current = self.semantic_repair.repair(scene, state, current, report)
            repaired = True

        return {
            "ok": False,
            "draft": current,
            "repaired": repaired,
            "attempts": max_repairs,
            "history": history,
            "final_report": history[-1] if history else {},
        }

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

        gate = self._semantic_gate(scene, state, draft, max_repairs=3)

        if not gate["ok"]:
            return {
                "ok": False,
                "status": "SEMANTIC_BLOCKED",
                "state": state,
                "scene": scene,
                "draft": gate["draft"],
                "semantic_history": gate["history"],
                "final_semantic_report": gate["final_report"],
                "repaired": gate["repaired"],
                "repair_attempts": gate["attempts"],
                "ingest_validation": validation,
            }

        return {
            "ok": True,
            "status": "ACCEPTED_CONTINUATION",
            "state": state,
            "scene": scene,
            "draft": gate["draft"],
            "semantic_history": gate["history"],
            "final_semantic_report": gate["final_report"],
            "repaired": gate["repaired"],
            "repair_attempts": gate["attempts"],
            "ingest_validation": validation,
        }
