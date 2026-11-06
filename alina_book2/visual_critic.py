from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path
from typing import Any, Dict


def ollama_vision_chat(model: str, prompt: str, image_path: str | Path, timeout: int = 240) -> str:
    image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
    payload = json.dumps({
        "model": model,
        "stream": False,
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [image_b64],
        }],
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return (body.get("message", {}).get("content") or body.get("response") or "").strip()


class VisualCritic:
    def __init__(self, model: str = "qwen3-vl:8b"):
        self.model = model

    def review(self, image_path: str | Path, contract: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Ты ALINA VISUAL CRITIC.

Сравни изображение с Visual Scene Contract.

CONTRACT:
{json.dumps(contract, ensure_ascii=False, indent=2)}

Проверь персонажей, локацию, крупные объекты, действие, запрещённые изменения и continuity.

Верни только JSON:
{{
  "decision": "PASS" или "REGENERATE",
  "score": 0.0,
  "issues": [
    {{
      "code": "VISUAL_MISMATCH",
      "severity": "MINOR | MAJOR | CRITICAL",
      "description": "..."
    }}
  ],
  "observed": {{
    "characters": [],
    "location": "",
    "objects": [],
    "actions": []
  }}
}}
""".strip()

        raw = ollama_vision_chat(self.model, prompt, image_path)
        data = self._parse_json(raw)
        data["raw"] = raw
        data["model"] = self.model
        return data

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        text = raw.strip()
        if text.startswith("~~~"):
            lines = text.splitlines()
            lines = lines[1:-1]
            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
        except Exception:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    data = json.loads(text[start:end + 1])
                except Exception:
                    data = {}
            else:
                data = {}

        decision = str(data.get("decision", "REGENERATE")).upper()
        if decision not in {"PASS", "REGENERATE"}:
            decision = "REGENERATE"

        issues = data.get("issues", [])
        if not isinstance(issues, list):
            issues = [{
                "code": "VISUAL_CRITIC_FORMAT_ERROR",
                "severity": "MAJOR",
                "description": "issues must be a list",
            }]
            decision = "REGENERATE"

        try:
            score = float(data.get("score", 0.0))
        except Exception:
            score = 0.0

        return {
            "decision": decision,
            "score": score,
            "issues": issues,
            "observed": data.get("observed", {}),
        }
