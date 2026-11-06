import shutil
import tempfile
import unittest
from pathlib import Path

from alina_book2.project_manager import AnalysisProjectManager


class AnalysisProjectManagerTests(unittest.TestCase):
    def test_create_and_list_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = AnalysisProjectManager(Path(tmp) / "projects")
            p = manager.create_project(
                "war-and-peace",
                "Война и мир",
                "MULTI_VOLUME_BOOK",
            )

            self.assertTrue((p / "project.json").exists())
            self.assertTrue((p / "sources").is_dir())
            self.assertTrue((p / "state").is_dir())
            self.assertTrue((p / "graph").is_dir())
            self.assertTrue((p / "evidence").is_dir())

            projects = manager.list_projects()
            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["project_id"], "war-and-peace")
            self.assertEqual(projects[0]["project_type"], "MULTI_VOLUME_BOOK")


if __name__ == "__main__":
    unittest.main()
