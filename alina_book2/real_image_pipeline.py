from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from alina_book2.comfyui_provider import ComfyUIProvider
from alina_book2.scene_assets import SceneAssetRegistry
from alina_book2.visual_critic import VisualCritic


class RealImagePipeline:
    def __init__(
        self,
        project_dir: str | Path,
        comfy_url: str = "http://127.0.0.1:8188",
        critic_model: str = "qwen3-vl:8b",
    ):
        self.project_dir = Path(project_dir)
        self.provider = ComfyUIProvider(comfy_url)
        self.critic = VisualCritic(critic_model)
        self.assets = SceneAssetRegistry(self.project_dir)

    def run(self, job: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        generation = self.provider.generate(
            job,
            self.project_dir / "visual" / "generated",
        )

        candidates = generation.get("images", [])
        reports = []

        for image_path in candidates:
            report = self.critic.review(image_path, contract)
            reports.append({
                "image_path": image_path,
                "report": report,
            })

            if report.get("decision") == "PASS":
                accepted = self.assets.accept_image(
                    contract["scene_id"],
                    contract["shot_id"],
                    image_path,
                    metadata={
                        "provider": "comfyui",
                        "prompt_id": generation.get("prompt_id"),
                        "visual_critic": report,
                    },
                )
                return {
                    "ok": True,
                    "status": "ACCEPTED",
                    "generation": generation,
                    "visual_reports": reports,
                    "asset": accepted,
                }

        return {
            "ok": False,
            "status": "REGENERATE",
            "generation": generation,
            "visual_reports": reports,
        }
