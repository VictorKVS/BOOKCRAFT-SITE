from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CriticFinding:
    critic: str
    decision: str
    code: str
    message: str


class NarrativeStateStore:
    def __init__(self, initial_state: Dict[str, Any]):
        self.state = deepcopy(initial_state)

    def apply_delta(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        next_state = deepcopy(self.state)
        next_state["version"] = int(next_state.get("version", 0)) + 1
        next_state.setdefault("events", []).extend(delta.get("new_events", []))
        next_state.setdefault("plot_threads", []).extend(delta.get("new_threads", []))
        for cid, changes in delta.get("character_changes", {}).items():
            next_state.setdefault("characters", {}).setdefault(cid, {}).update(changes)
        self.state = next_state
        return deepcopy(self.state)


class Producer:
    def plan_scene(self, state: Dict[str, Any], objective: str) -> Dict[str, Any]:
        pov = state.get("default_pov") or next(iter(state.get("characters", {"unknown": {}})))
        return {
            "scene_id": f"S-{int(state.get('version', 0)) + 1:03d}",
            "objective": objective,
            "pov": pov,
            "required_events": ["advance_objective"],
            "forbidden_events": ["break_locked_canon"],
            "entry_state_version": state.get("version", 0),
        }


class Writer:
    """Deterministic MVP writer.

    This deliberately does not call an LLM yet. It proves the production
    contract and state handoff before model integration.
    """

    def draft(self, scene: Dict[str, Any], state: Dict[str, Any], flawed: bool = False) -> Dict[str, Any]:
        pov = scene["pov"]
        known = state.get("characters", {}).get(pov, {}).get("knowledge", [])
        forbidden_secret = state.get("secrets", {}).get("locked_secret")

        if flawed and forbidden_secret:
            prose = (
                f"{pov} вошёл в комнату и сразу понял тайну: {forbidden_secret}. "
                f"Он решил действовать."
            )
            used_secret = forbidden_secret
        else:
            prose = (
                f"{pov} вошёл в комнату. Он опирался только на известные ему факты: "
                f"{', '.join(known) if known else 'ничего достоверного'}. "
                f"Сцена продвинула цель: {scene['objective']}."
            )
            used_secret = None

        return {
            "scene_id": scene["scene_id"],
            "prose": prose,
            "used_secret": used_secret,
            "state_delta": {
                "new_events": [
                    {
                        "event_id": f"E-{scene['scene_id']}",
                        "type": "scene_progress",
                        "summary": scene["objective"],
                    }
                ],
                "character_changes": {},
                "new_threads": [],
            },
        }


class CriticLayer:
    def review(self, draft: Dict[str, Any], scene: Dict[str, Any], state: Dict[str, Any]) -> List[CriticFinding]:
        findings: List[CriticFinding] = []

        used_secret = draft.get("used_secret")
        pov = scene["pov"]
        known = set(state.get("characters", {}).get(pov, {}).get("knowledge", []))
        if used_secret and used_secret not in known:
            findings.append(
                CriticFinding(
                    critic="continuity",
                    decision="REPAIR",
                    code="KNOWLEDGE_BEFORE_ACQUISITION",
                    message=f"{pov} использует секрет, которого ещё не знает.",
                )
            )

        if "break_locked_canon" in draft.get("prose", ""):
            findings.append(
                CriticFinding(
                    critic="canon",
                    decision="REJECT",
                    code="LOCKED_CANON_VIOLATION",
                    message="Черновик нарушает locked canon.",
                )
            )

        if not findings:
            findings.append(
                CriticFinding(
                    critic="aggregate",
                    decision="PASS",
                    code="OK",
                    message="Blocking defects not found.",
                )
            )
        return findings


class RepairAgent:
    def repair(
        self,
        draft: Dict[str, Any],
        scene: Dict[str, Any],
        state: Dict[str, Any],
        findings: List[CriticFinding],
        writer: Writer,
    ) -> Dict[str, Any]:
        repairable = any(x.code == "KNOWLEDGE_BEFORE_ACQUISITION" for x in findings)
        if not repairable:
            return draft
        return writer.draft(scene, state, flawed=False)


class Analyst:
    def validate_delta(self, delta: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(delta.get("new_events", []), list):
            return {"ok": False, "reason": "new_events_must_be_list"}
        return {"ok": True, "reason": "validated"}


class ProductionLoop:
    def __init__(self, state: Dict[str, Any]):
        self.store = NarrativeStateStore(state)
        self.producer = Producer()
        self.writer = Writer()
        self.critics = CriticLayer()
        self.repair = RepairAgent()
        self.analyst = Analyst()

    def run_scene(self, objective: str, inject_flaw: bool = False) -> Dict[str, Any]:
        state = deepcopy(self.store.state)
        scene = self.producer.plan_scene(state, objective)
        first_draft = self.writer.draft(scene, state, flawed=inject_flaw)
        first_findings = self.critics.review(first_draft, scene, state)

        final_draft = first_draft
        repaired = False

        if any(x.decision == "REJECT" for x in first_findings):
            return {
                "ok": False,
                "status": "REJECTED",
                "scene": scene,
                "findings": [x.__dict__ for x in first_findings],
            }

        if any(x.decision == "REPAIR" for x in first_findings):
            final_draft = self.repair.repair(first_draft, scene, state, first_findings, self.writer)
            repaired = final_draft != first_draft

        final_findings = self.critics.review(final_draft, scene, state)
        if any(x.decision != "PASS" for x in final_findings):
            return {
                "ok": False,
                "status": "REPAIR_EXHAUSTED",
                "scene": scene,
                "findings": [x.__dict__ for x in final_findings],
            }

        validation = self.analyst.validate_delta(final_draft["state_delta"], state)
        if not validation["ok"]:
            return {
                "ok": False,
                "status": "STATE_DELTA_INVALID",
                "scene": scene,
                "validation": validation,
            }

        new_state = self.store.apply_delta(final_draft["state_delta"])
        return {
            "ok": True,
            "status": "ACCEPTED",
            "scene": scene,
            "draft": final_draft,
            "repaired": repaired,
            "initial_findings": [x.__dict__ for x in first_findings],
            "final_findings": [x.__dict__ for x in final_findings],
            "state": new_state,
        }
