import json
import tempfile
import unittest
from pathlib import Path

from alina_book2.scene_assets import ImageGenerationJobBuilder, SceneAssetRegistry


class SceneAssetTests(unittest.TestCase):
    def test_register_accept_and_continuity(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            registry = SceneAssetRegistry(project)

            contract = {
                "scene_id": "S-001",
                "shot_id": "S-001-shot-01",
                "mode": "ILLUSTRATION",
            }
            prompt = "Test visual prompt"

            reg = registry.register_contract(contract, prompt)
            self.assertEqual(reg["status"], "READY_FOR_GENERATION")

            job = ImageGenerationJobBuilder().build_job(contract, prompt)
            self.assertEqual(job["scene_id"], "S-001")
            self.assertEqual(job["status"], "READY")

            fake = project / "visual" / "generated" / "S-001-shot-01.png"
            fake.parent.mkdir(parents=True, exist_ok=True)
            fake.write_bytes(b"PNG-PLACEHOLDER")

            accepted = registry.accept_image(
                "S-001",
                "S-001-shot-01",
                fake,
                {"provider": "test"},
            )
            self.assertEqual(accepted["status"], "ACCEPTED")

            latest = registry.latest_visual_reference()
            self.assertEqual(latest["shot_id"], "S-001-shot-01")


if __name__ == "__main__":
    unittest.main()
