from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict


class ComfyUIProvider:
    name = "comfyui"

    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: int = 600):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> Dict[str, Any]:
        for path in ("/prompt", "/api/prompt"):
            try:
                with urllib.request.urlopen(self.base_url + path, timeout=5) as resp:
                    return {"ok": True, "path": path, "status": resp.status}
            except Exception:
                continue
        return {"ok": False, "path": None}

    def generate(self, job: Dict[str, Any], output_dir: str | Path) -> Dict[str, Any]:
        workflow_path = job.get("workflow_path")
        if not workflow_path:
            raise ValueError("ComfyUI job requires workflow_path")

        workflow = json.loads(Path(workflow_path).read_text(encoding="utf-8"))
        workflow = self._replace_tokens(
            workflow,
            {
                "{{PROMPT}}": job.get("prompt", ""),
                "{{NEGATIVE_PROMPT}}": job.get("negative_prompt", ""),
            },
        )

        client_id = str(uuid.uuid4())
        payload = {
            "prompt": workflow,
            "client_id": client_id,
        }

        response = self._post_json("/prompt", payload)
        prompt_id = response.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI did not return prompt_id: {response}")

        history = self._wait_history(prompt_id)
        image_refs = self._extract_images(history, prompt_id)
        if not image_refs:
            raise RuntimeError("ComfyUI completed without image outputs")

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        saved = []
        for index, image_ref in enumerate(image_refs, start=1):
            data = self._download_image(image_ref)
            suffix = Path(image_ref["filename"]).suffix or ".png"
            target = output / f"{job['shot_id']}-{index:02d}{suffix}"
            target.write_bytes(data)
            saved.append(str(target))

        return {
            "provider": self.name,
            "status": "GENERATED",
            "prompt_id": prompt_id,
            "images": saved,
            "history": history,
        }

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _wait_history(self, prompt_id: str) -> Dict[str, Any]:
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            for path in (f"/history/{prompt_id}", f"/api/history_v2/{prompt_id}"):
                try:
                    with urllib.request.urlopen(self.base_url + path, timeout=10) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    if data:
                        return data
                except Exception:
                    continue
            time.sleep(1.0)
        raise TimeoutError(f"ComfyUI generation timed out: {prompt_id}")

    @staticmethod
    def _extract_images(history: Dict[str, Any], prompt_id: str) -> list[Dict[str, Any]]:
        entry = history.get(prompt_id, history)
        outputs = entry.get("outputs", {}) if isinstance(entry, dict) else {}
        images = []
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            for image in node_output.get("images", []):
                if isinstance(image, dict) and image.get("filename"):
                    images.append(image)
        return images

    def _download_image(self, ref: Dict[str, Any]) -> bytes:
        query = urllib.parse.urlencode({
            "filename": ref["filename"],
            "subfolder": ref.get("subfolder", ""),
            "type": ref.get("type", "output"),
        })
        with urllib.request.urlopen(self.base_url + "/view?" + query, timeout=30) as resp:
            return resp.read()

    @classmethod
    def _replace_tokens(cls, value: Any, replacements: Dict[str, str]) -> Any:
        if isinstance(value, dict):
            return {k: cls._replace_tokens(v, replacements) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._replace_tokens(v, replacements) for v in value]
        if isinstance(value, str):
            result = value
            for token, replacement in replacements.items():
                result = result.replace(token, replacement)
            return result
        return value
