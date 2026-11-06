import unittest

from alina_book2.local_image_profile import LocalImageProfile


class LocalImageProfileTests(unittest.TestCase):
    def test_default_quality_profile(self):
        p = LocalImageProfile.load()
        self.assertEqual(p.name, "sdxl_quality")
        self.assertEqual(p.model_family, "SDXL")
        self.assertEqual(p.generation["width"], 1024)
        self.assertEqual(p.generation["height"], 1024)
        self.assertEqual(p.generation["batch_size"], 1)
        self.assertEqual(p.validate(), [])

    def test_profile_applies_to_generation_job(self):
        p = LocalImageProfile.load()
        job = {
            "scene_id": "S-001",
            "shot_id": "S-001-shot-01",
            "prompt": "Анна стоит в коридоре."
        }
        result = p.apply_to_job(job)
        self.assertEqual(result["local_model_profile"], "sdxl_quality")
        self.assertEqual(result["checkpoint_filename"], "sd_xl_base_1.0.safetensors")
        self.assertEqual(result["requested_output"]["width"], 1024)


if __name__ == "__main__":
    unittest.main()
