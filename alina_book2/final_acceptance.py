from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from alina_book2.full_story_pipeline import FullStoryContinuationPipeline


class StatefulBookRunner:
    """Final MVP acceptance runner.

    Proves that accepted scenes become the input state for subsequent scenes.
    """

    def __init__(self, model: str = "qwen2.5:7b"):
        self.pipeline = FullStoryContinuationPipeline(model=model)

    @staticmethod
    def apply_delta(state: Dict[str, Any], draft: Dict[str, Any]) -> Dict[str, Any]:
        next_state = deepcopy(state)
        next_state["version"] = int(next_state.get("version", 1)) + 1

        delta = draft.get("state_delta", {})
        next_state.setdefault("events", []).extend(delta.get("new_events", []))

        for cid, changes in delta.get("character_changes", {}).items():
            next_state.setdefault("characters", {}).setdefault(cid, {}).update(changes)

        next_state.setdefault("plot_threads", []).extend(delta.get("new_threads", []))
        next_state["last_accepted_scene"] = draft.get("scene_id")
        return next_state

    def run_two_scenes(
        self,
        source_path: str | Path,
        objectives: List[str],
    ) -> Dict[str, Any]:
        if len(objectives) != 2:
            raise ValueError("MVP-06 requires exactly two scene objectives")

        first = self.pipeline.run(source_path, objectives[0])
        if not first.get("ok"):
            return {"ok": False, "stage": "scene_1", "result": first}

        state_v1 = first["state"]
        state_v2 = self.apply_delta(state_v1, first["draft"])

        # Continue from the accepted state without re-ingesting the story.
        scene2 = self.pipeline.producer.plan_scene(state_v2, objectives[1])
        draft2 = self.pipeline.writer.draft(scene2, state_v2)

        report1 = self.pipeline.semantic.review(scene2, state_v2, draft2)
        repaired = False
        if report1.get("decision") == "REPAIR":
            draft2 = self.pipeline.semantic_repair.repair(scene2, state_v2, draft2, report1)
            repaired = True

        report2 = self.pipeline.semantic.review(scene2, state_v2, draft2)
        if report2.get("decision") != "PASS":
            return {
                "ok": False,
                "stage": "scene_2_semantic",
                "state_v2": state_v2,
                "scene_2": scene2,
                "draft_2": draft2,
                "report": report2,
            }

        state_v3 = self.apply_delta(state_v2, draft2)

        return {
            "ok": True,
            "status": "FINAL_ACCEPTANCE_PASS",
            "scene_1": first["draft"],
            "scene_2": draft2,
            "scene_2_repaired": repaired,
            "state_versions": [
                state_v1.get("version"),
                state_v2.get("version"),
                state_v3.get("version"),
            ],
            "state_v3": state_v3,
            "scene_2_semantic_report": report2,
        }


def write_evidence(result: Dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
