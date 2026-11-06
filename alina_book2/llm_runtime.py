from __future__ import annotations

import json
import urllib.request
from copy import deepcopy
from typing import Any, Dict

from alina_book2.production_loop import Analyst, CriticLayer, NarrativeStateStore, Producer


def ollama_generate(model: str, prompt: str, timeout: int = 180) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return (body.get("response") or "").strip()


class LLMWriter:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model

    def draft(self, scene: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        pov = scene["pov"]
        known = state.get("characters", {}).get(pov, {}).get("knowledge", [])
        restricted_fact = state.get("secrets", {}).get("locked_secret")

        prompt = f"""
Ты ALINA WRITER. Напиши короткую художественную сцену на русском языке.

POV: {pov}
Цель сцены: {scene['objective']}
Известные персонажу факты: {known}
Факт, которого персонаж не знает: {restricted_fact}

Требования:
- 80–180 слов;
- не используй неизвестный персонажу факт;
- сохрани POV;
- продвинь цель сцены;
- не меняй канон;
- верни только художественный текст.
""".strip()

        prose = ollama_generate(self.model, prompt)
        used_restricted = restricted_fact if restricted_fact and restricted_fact.lower() in prose.lower() else None

        return {
            "scene_id": scene["scene_id"],
            "prose": prose,
            "used_secret": used_restricted,
            "state_delta": {
                "new_events": [{
                    "event_id": f"E-{scene['scene_id']}",
                    "type": "scene_progress",
                    "summary": scene["objective"],
                }],
                "character_changes": {},
                "new_threads": [],
            },
            "runtime": {"provider": "ollama", "model": self.model},
        }


class RealLLMProductionLoop:
    def __init__(self, state: Dict[str, Any], model: str = "qwen2.5:7b"):
        self.store = NarrativeStateStore(state)
        self.producer = Producer()
        self.writer = LLMWriter(model)
        self.critics = CriticLayer()
        self.analyst = Analyst()

    def run_scene(self, objective: str) -> Dict[str, Any]:
        state = deepcopy(self.store.state)
        scene = self.producer.plan_scene(state, objective)
        draft = self.writer.draft(scene, state)
        findings = self.critics.review(draft, scene, state)

        if any(x.decision != "PASS" for x in findings):
            return {
                "ok": False,
                "status": "CRITIC_BLOCKED",
                "scene": scene,
                "draft": draft,
                "findings": [x.__dict__ for x in findings],
            }

        validation = self.analyst.validate_delta(draft["state_delta"], state)
        if not validation["ok"]:
            return {"ok": False, "status": "STATE_DELTA_INVALID", "validation": validation}

        new_state = self.store.apply_delta(draft["state_delta"])
        return {
            "ok": True,
            "status": "ACCEPTED",
            "scene": scene,
            "draft": draft,
            "findings": [x.__dict__ for x in findings],
            "state": new_state,
        }
