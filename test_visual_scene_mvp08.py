import unittest

from alina_book2.visual_scene import VisualPromptBuilder, VisualSceneBuilder


class VisualSceneTests(unittest.TestCase):
    def test_build_contract_and_prompt(self):
        scene = {
            "scene_id": "S-014",
            "prose": "Анна стоит перед запертой дверью и прислушивается."
        }
        state = {
            "default_pov": "anna",
            "characters": {
                "anna": {
                    "name": "Анна",
                    "location": "коридор",
                    "appearance": "тёмные волосы",
                    "clothing": "серый свитер",
                    "physical_state": "без травм",
                    "emotional_state": "насторожена",
                    "knowledge": ["дверь заперта"]
                }
            },
            "objects": {},
            "locations": [{"id": "corridor", "name": "коридор"}]
        }

        contract = VisualSceneBuilder().build_contract(scene, state)
        prompt = VisualPromptBuilder().build_prompt(contract)

        self.assertEqual(contract["scene_id"], "S-014")
        self.assertEqual(contract["location"]["description"], "коридор")
        self.assertEqual(contract["characters"][0]["name"], "Анна")
        self.assertIn("Анна", prompt)
        self.assertIn("коридор", prompt)
        self.assertIn("Preserve character identity", prompt)


if __name__ == "__main__":
    unittest.main()
