import unittest

from alina_book2.production_loop import ProductionLoop


STATE = {
    "version": 1,
    "default_pov": "anna",
    "characters": {"anna": {"knowledge": ["дверь была заперта"]}},
    "secrets": {"locked_secret": "ключ спрятан в часах"},
    "events": [],
    "plot_threads": [],
}


class ProductionLoopTests(unittest.TestCase):
    def test_clean_scene_accepts(self):
        result = ProductionLoop(STATE).run_scene("Продвинуть расследование.")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ACCEPTED")
        self.assertEqual(result["state"]["version"], 2)

    def test_unknown_secret_forces_repair(self):
        result = ProductionLoop(STATE).run_scene("Продвинуть расследование.", inject_flaw=True)
        self.assertTrue(result["ok"])
        self.assertTrue(result["repaired"])
        self.assertEqual(result["final_findings"][0]["decision"], "PASS")


if __name__ == "__main__":
    unittest.main()
