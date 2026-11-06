from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class SceneAssetRegistry:
    def __init__(self, project_dir: str | Path):
        self.project_dir = Path(project_dir)
        self.visual_dir = self.project_dir / "visual"
        for name in ("contracts", "prompts", "generated", "accepted", "rejected", "continuity"):
            (self.visual_dir / name).mkdir(parents=True, exist_ok=True)

    def register_contract(self, contract: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        scene_id = contract["scene_id"]
        shot_id = contract["shot_id"]

        contract_path = self.visual_dir / "contracts" / f"{shot_id}.json"
        prompt_path = self.visual_dir / "prompts" / f"{shot_id}.txt"

        contract_path.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        prompt_path.write_text(prompt, encoding="utf-8")

        return {
            "scene_id": scene_id,
            "shot_id": shot_id,
            "contract_path": str(contract_path),
            "prompt_path": str(prompt_path),
            "status": "READY_FOR_GENERATION",
        }

    def accept_image(
        self,
        scene_id: str,
        shot_id: str,
        image_path: str | Path,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        record = {
            "scene_id": scene_id,
            "shot_id": shot_id,
            "image_path": str(image_path),
            "status": "ACCEPTED",
            "metadata": metadata or {},
        }

        record_path = self.visual_dir / "accepted" / f"{shot_id}.json"
        record_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        continuity_path = self.visual_dir / "continuity" / "latest.json"
        continuity_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return record

    def latest_visual_reference(self) -> Dict[str, Any] | None:
        p = self.visual_dir / "continuity" / "latest.json"
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))


class ImageGenerationJobBuilder:
    """Provider-neutral generation request.

    The actual image provider can be local or external. This contract keeps
    ALINA BOOK 2 independent from a specific image model.
    """

    def build_job(
        self,
        contract: Dict[str, Any],
        prompt: str,
        continuity_reference: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "job_type": "SCENE_IMAGE_GENERATION",
            "scene_id": contract["scene_id"],
            "shot_id": contract["shot_id"],
            "mode": contract.get("mode", "ILLUSTRATION"),
            "prompt": prompt,
            "visual_contract": contract,
            "continuity_reference": continuity_reference,
            "requested_output": {
                "format": "png",
                "aspect_ratio": "16:9",
                "count": 1,
            },
            "status": "READY",
        }
