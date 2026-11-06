from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Protocol


class ImageProvider(Protocol):
    name: str

    def generate(self, job: Dict[str, Any], output_dir: str | Path) -> Dict[str, Any]:
        ...


class ManualImportProvider:
    name = "manual-import"

    def generate(self, job: Dict[str, Any], output_dir: str | Path) -> Dict[str, Any]:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        shot_id = job["shot_id"]
        request_path = output / f"{shot_id}.generation-request.json"
        request_path.write_text(
            json.dumps(job, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "provider": self.name,
            "status": "AWAITING_IMAGE",
            "shot_id": shot_id,
            "request_path": str(request_path),
            "expected_image_path": str(output / f"{shot_id}.png"),
        }


class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, ImageProvider] = {}
        self.register(ManualImportProvider())

    def register(self, provider: ImageProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> ImageProvider:
        if name not in self._providers:
            raise KeyError(f"Unknown image provider: {name}")
        return self._providers[name]

    def names(self) -> list[str]:
        return sorted(self._providers.keys())
