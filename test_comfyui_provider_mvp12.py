import tempfile
import unittest
from pathlib import Path

from alina_book2.comfyui_provider import ComfyUIProvider


class ComfyUITests(unittest.TestCase):
    def test_prompt_tokens_are_replaced_recursively(self):
        workflow = {
            "1": {"inputs": {"text": "{{PROMPT}}"}},
            "2": {"inputs": {"text": "avoid {{NEGATIVE_PROMPT}}"}},
            "3": ["{{PROMPT}}"],
        }
        result = ComfyUIProvider._replace_tokens(
            workflow,
            {
                "{{PROMPT}}": "Анна в коридоре",
                "{{NEGATIVE_PROMPT}}": "искажённые руки",
            },
        )
        self.assertEqual(result["1"]["inputs"]["text"], "Анна в коридоре")
        self.assertIn("искажённые руки", result["2"]["inputs"]["text"])
        self.assertEqual(result["3"][0], "Анна в коридоре")


if __name__ == "__main__":
    unittest.main()
