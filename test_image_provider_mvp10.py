import tempfile
import unittest
from pathlib import Path

from alina_book2.image_providers import ProviderRegistry


class ImageProviderTests(unittest.TestCase):
    def test_manual_provider_materializes_request(self):
        registry = ProviderRegistry()
        self.assertIn("manual-import", registry.names())

        job = {
            "job_type": "SCENE_IMAGE_GENERATION",
            "scene_id": "S-001",
            "shot_id": "S-001-shot-01",
            "prompt": "test",
        }

        with tempfile.TemporaryDirectory() as tmp:
            result = registry.get("manual-import").generate(job, tmp)
            self.assertEqual(result["status"], "AWAITING_IMAGE")
            self.assertTrue(Path(result["request_path"]).exists())
            self.assertTrue(result["expected_image_path"].endswith(".png"))


if __name__ == "__main__":
    unittest.main()
