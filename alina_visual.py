import argparse
import json
from pathlib import Path

from alina_book2.scene_assets import ImageGenerationJobBuilder, SceneAssetRegistry
from alina_book2.visual_scene import VisualPromptBuilder


def main():
    parser = argparse.ArgumentParser(description="ALINA BOOK 2 visual asset manager")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-job")
    build.add_argument("--project", required=True)
    build.add_argument("--contract", required=True)

    accept = sub.add_parser("accept-image")
    accept.add_argument("--project", required=True)
    accept.add_argument("--scene-id", required=True)
    accept.add_argument("--shot-id", required=True)
    accept.add_argument("--image", required=True)

    args = parser.parse_args()
    registry = SceneAssetRegistry(args.project)

    if args.command == "build-job":
        contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        prompt = VisualPromptBuilder().build_prompt(contract)
        registry.register_contract(contract, prompt)
        job = ImageGenerationJobBuilder().build_job(
            contract,
            prompt,
            continuity_reference=registry.latest_visual_reference(),
        )
        print(json.dumps(job, ensure_ascii=False, indent=2))

    elif args.command == "accept-image":
        record = registry.accept_image(
            args.scene_id,
            args.shot_id,
            args.image,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
