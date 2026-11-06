from __future__ import annotations

import json
from typing import Any, Dict, List

from alina_book2.llm_runtime import ollama_generate


class SemanticCritic:
    """LLM-backed semantic consistency critic.

    It checks whether prose introduces meaningful state changes that are absent
    from the declared state_delta or contradict the scene entry state.
    """

    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model

    def review(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any],
        draft: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = f"""
Ты ALINA SEMANTIC CRITIC.

Проверь согласованность художественной сцены с входным состоянием и state_delta.

ВХОДНОЕ СОСТОЯНИЕ:
{json.dumps(state, ensure_ascii=False, indent=2)}

КОНТРАКТ СЦЕНЫ:
{json.dumps(scene, ensure_ascii=False, indent=2)}

STATE DELTA:
{json.dumps(draft.get("state_delta", {}), ensure_ascii=False, indent=2)}

ПРОЗА:
{draft.get("prose", "")}

Ищи только существенные изменения состояния, которые появились в прозе, но отсутствуют в state_delta
или противоречат входному состоянию/контракту. Например:
- персонаж нашёл важный объект;
- дверь открылась;
- персонаж переместился;
- персонаж получил новое знание;
- возникла травма;
- изменились отношения;
- возник новый факт мира;
- произошло событие с последствиями.

Верни ТОЛЬКО JSON:
{{
  "decision": "PASS" или "REPAIR",
  "issues": [
    {{
      "code": "PROSE_STATE_MISMATCH",
      "claim": "кратко что произошло",
      "reason": "почему это не подтверждено state_delta/каноном"
    }}
  ]
}}

Если существенных несогласованностей нет, issues должен быть пустым.
""".strip()

        raw = ollama_generate(self.model, prompt)
        data = self._parse_json(raw)
        decision = str(data.get("decision", "REPAIR")).upper()
        issues = data.get("issues", [])
        if decision not in {"PASS", "REPAIR"}:
            decision = "REPAIR"
        if not isinstance(issues, list):
            issues = [{"code": "CRITIC_FORMAT_ERROR", "claim": "", "reason": "issues must be a list"}]
            decision = "REPAIR"
        return {
            "decision": decision,
            "issues": issues,
            "raw": raw,
            "model": self.model,
        }

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
                try:
                    return json.loads(text[start:end + 1])
                except Exception:
                    pass
        return {
            "decision": "REPAIR",
            "issues": [{
                "code": "CRITIC_FORMAT_ERROR",
                "claim": "",
                "reason": "Semantic critic did not return valid JSON"
            }]
        }


class SemanticRepair:
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model

    def repair(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any],
        draft: Dict[str, Any],
        semantic_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = f"""
Ты ALINA SEMANTIC REPAIR.

Исправь сцену так, чтобы все существенные изменения в прозе соответствовали входному состоянию,
контракту сцены и уже объявленному state_delta. Не добавляй новые события в state_delta:
нужно минимально исправить сам текст.

ВХОДНОЕ СОСТОЯНИЕ:
{json.dumps(state, ensure_ascii=False, indent=2)}

КОНТРАКТ:
{json.dumps(scene, ensure_ascii=False, indent=2)}

STATE DELTA:
{json.dumps(draft.get("state_delta", {}), ensure_ascii=False, indent=2)}

ПРОБЛЕМЫ:
{json.dumps(semantic_report.get("issues", []), ensure_ascii=False, indent=2)}

ИСХОДНАЯ ПРОЗА:
{draft.get("prose", "")}

Требования:
- не создавай фактов, которых нет во входном состоянии или state_delta;
- не позволяй персонажу получать знания без события приобретения знания;
- не меняй местоположение/объекты/отношения/состояние без delta;
- сохрани POV и цель сцены;
- 80–180 слов;
- верни только исправленную прозу.
""".strip()

        repaired = dict(draft)
        repaired["prose"] = ollama_generate(self.model, prompt)
        repaired["runtime"] = {
            "provider": "ollama",
            "model": self.model,
            "mode": "semantic_repair",
        }
        return repaired
