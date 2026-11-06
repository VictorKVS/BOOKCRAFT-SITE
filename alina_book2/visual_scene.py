from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class VisualSceneBuilder:
    def build_contract(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any],
        mode: str = "ILLUSTRATION",
    ) -> Dict[str, Any]:
        scene_id = scene.get("scene_id", "scene")
        prose = scene.get("prose", "")
        pov = state.get("default_pov")

        characters = []
        for cid, data in state.get("characters", {}).items():
            if not isinstance(data, dict):
                continue
            characters.append({
                "character_id": cid,
                "name": data.get("name", cid),
                "location": data.get("location"),
                "physical_state": data.get("physical_state"),
                "emotional_state": data.get("emotional_state"),
                "clothing": data.get("clothing"),
                "appearance": data.get("appearance"),
                "knowledge": data.get("knowledge", []),
            })

        return {
            "scene_id": scene_id,
            "shot_id": f"{scene_id}-shot-01",
            "mode": mode,
            "source_prose": prose,
            "pov": pov,
            "characters": characters,
            "location": self._resolve_location(state, pov),
            "objects": deepcopy(state.get("objects", {})),
            "actions": [],
            "interactions": [],
            "camera": {
                "shot_size": "medium",
                "angle": "eye-level",
                "viewpoint": pov or "",
                "lens": "",
            },
            "composition": {
                "foreground": [],
                "midground": [],
                "background": [],
                "positions": {},
            },
            "lighting": {
                "time_of_day": "",
                "sources": [],
                "contrast": "",
                "atmosphere": "",
            },
            "mood": {
                "emotion": "",
                "tone": "",
            },
            "continuity": {
                "previous_shot_id": None,
                "inherit_character_appearance": True,
                "inherit_clothing": True,
                "inherit_injuries": True,
                "inherit_objects": True,
            },
            "forbidden_changes": [
                "change_character_identity",
                "invent_major_object",
                "change_location_without_scene_event",
                "remove_canon_injury",
            ],
        }

    @staticmethod
    def _resolve_location(state: Dict[str, Any], pov: str | None) -> Dict[str, Any]:
        if pov:
            character = state.get("characters", {}).get(pov, {})
            if isinstance(character, dict) and character.get("location"):
                return {
                    "id": str(character.get("location")),
                    "description": str(character.get("location")),
                }

        locations = state.get("locations", [])
        if locations and isinstance(locations[0], dict):
            first = locations[0]
            return {
                "id": first.get("id", ""),
                "description": first.get("name", ""),
            }

        return {"id": "", "description": ""}


class VisualPromptBuilder:
    def build_prompt(self, contract: Dict[str, Any]) -> str:
        characters = []
        for ch in contract.get("characters", []):
            characters.append(
                f"{ch.get('name')}: appearance={ch.get('appearance')}; "
                f"clothing={ch.get('clothing')}; state={ch.get('physical_state')}; "
                f"emotion={ch.get('emotional_state')}"
            )

        forbidden = ", ".join(contract.get("forbidden_changes", []))

        return (
            f"Scene ID: {contract.get('scene_id')}\n"
            f"Mode: {contract.get('mode')}\n"
            f"Location: {contract.get('location', {}).get('description', '')}\n"
            f"Characters: {' | '.join(characters)}\n"
            f"Camera: {contract.get('camera')}\n"
            f"Composition: {contract.get('composition')}\n"
            f"Lighting: {contract.get('lighting')}\n"
            f"Mood: {contract.get('mood')}\n"
            f"Source scene: {contract.get('source_prose', '')}\n"
            f"Do not violate: {forbidden}\n"
            "Preserve character identity, clothing, injuries, objects, location and scene continuity."
        )
