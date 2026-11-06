from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from alina_book2.image_providers import ProviderRegistry
from alina_book2.scene_assets import ImageGenerationJobBuilder, SceneAssetRegistry
from alina_book2.visual_critic import VisualCritic
from alina_book2.visual_scene import VisualPromptBuilder


class VisualWorkflow:
    def __init__(self, project_dir: str | Path, provider: str = "manual-import", critic_model: str = "qwen3-vl:8b"):
        self.project_dir = Path(project_dir)
        self.assets = SceneAssetRegistry(self.project_dir)
        self.providers = ProviderRegistry()
        self.provider = self.providers.get(provider)
        self.critic = VisualCritic(critic_model)

    def prepare(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        prompt = VisualPromptBuilder().build_prompt(contract)
        self.assets.register_contract(contract, prompt)

        job = ImageGenerationJobBuilder().build_job(
            contract,
            prompt,
            continuity_reference=self.assets.latest_visual_reference(),
        )

        generation = self.provider.generate(
            job,
            self.project_dir / "visual" / "generated",
        )

        return {
            "status": "AWAITING_IMAGE",
            "job": job,
            "generation": generation,
        }

    def review_and_accept(self, contract: Dict[str, Any], image_path: str | Path) -> Dict[str, Any]:
        image_path = Path(image_path)
        if not image_path.exists():
            return {
                "ok": False,
                "status": "IMAGE_NOT_FOUND",
                "image_path": str(image_path),
            }

        report = self.critic.review(image_path, contract)

        if report.get("decision") != "PASS":
            return {
                "ok": False,
                "status": "REGENERATE",
                "visual_report": report,
                "image_path": str(image_path),
            }

        record = self.assets.accept_image(
            contract["scene_id"],
            contract["shot_id"],
            image_path,
            metadata={
                "visual_critic": report,
            },
        )

        return {
            "ok": True,
            "status": "ACCEPTED",
            "visual_report": report,
            "asset": record,
        }


def load_contract(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
