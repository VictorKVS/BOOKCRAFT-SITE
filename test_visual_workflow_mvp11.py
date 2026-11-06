import json
import tempfile
import unittest
from pathlib import Path

from alina_book2.visual_workflow import VisualWorkflow


class VisualWorkflowTests(unittest.TestCase):
    def test_prepare_creates_generation_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            workflow = VisualWorkflow(project)

            contract = {
                "scene_id": "S-100",
                "shot_id": "S-100-shot-01",
                "mode": "ILLUSTRATION",
                "characters": [],
                "location": {"id": "corridor", "description": "коридор"},
                "objects": [],
                "actions": [],
                "interactions": [],
                "camera": {},
                "composition": {},
                "lighting": {},
                "mood": {},
                "continuity": {},
                "forbidden_changes": [],
                "source_prose": "Анна стоит в коридоре."
            }

            result = workflow.prepare(contract)
            self.assertEqual(result["status"], "AWAITING_IMAGE")
            self.assertTrue(Path(result["generation"]["request_path"]).exists())
            self.assertTrue(result["generation"]["expected_image_path"].endswith(".png"))


if __name__ == "__main__":
    unittest.main()
