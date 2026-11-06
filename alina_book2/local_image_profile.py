from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class LocalImageProfile:
    name: str
    provider: str
    model_family: str
    role: str
    checkpoint_filename: str
    checkpoint_path: str
    generation: Dict[str, Any]
    negative_prompt: str
    resource_policy: Dict[str, Any]

    @classmethod
    def load(
        cls,
        config_path: str | Path = "config/local_image_models.json",
        profile_name: str | None = None,
    ) -> "LocalImageProfile":
        data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        name = profile_name or data["active_profile"]
        p = data["profiles"][name]

        return cls(
            name=name,
            provider=p["provider"],
            model_family=p["model_family"],
            role=p["role"],
            checkpoint_filename=p["checkpoint"]["filename"],
            checkpoint_path=p["checkpoint"]["path"],
            generation=p["generation"],
            negative_prompt=p.get("negative_prompt", ""),
            resource_policy=p.get("resource_policy", {}),
        )

    def apply_to_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(job)
        result["local_model_profile"] = self.name
        result["model_family"] = self.model_family
        result["checkpoint_filename"] = self.checkpoint_filename
        result["negative_prompt"] = self.negative_prompt
        result["requested_output"] = {
            **result.get("requested_output", {}),
            "width": self.generation["width"],
            "height": self.generation["height"],
            "count": self.generation.get("batch_size", 1),
        }
        result["generation_settings"] = dict(self.generation)
        result["resource_policy"] = dict(self.resource_policy)
        return result

    def checkpoint_full_path(self, comfy_root: str | Path) -> Path:
        root = Path(comfy_root)
        relative = Path(self.checkpoint_path)
        parts = list(relative.parts)
        if parts and parts[0].lower() == "comfyui":
            relative = Path(*parts[1:])
        return root / "ComfyUI" / relative.relative_to("models") / self.checkpoint_filename

    def validate(self) -> list[str]:
        issues = []
        if not self.checkpoint_filename:
            issues.append("checkpoint_filename_is_empty")
        if self.generation.get("batch_size", 1) > self.resource_policy.get("max_batch_size", 1):
            issues.append("batch_size_exceeds_resource_policy")
        if self.generation.get("width", 0) <= 0 or self.generation.get("height", 0) <= 0:
            issues.append("invalid_resolution")
        return issues
