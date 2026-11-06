import argparse
import json

from alina_book2.project_manager import AnalysisProjectManager


def main():
    parser = argparse.ArgumentParser(description="ALINA BOOK 2 project manager")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create analysis project")
    create.add_argument("project_id")
    create.add_argument("--title", required=True)
    create.add_argument(
        "--type",
        default="SINGLE_BOOK",
        choices=[
            "SINGLE_BOOK",
            "MULTI_VOLUME_BOOK",
            "BOOK_SERIES",
            "UNIVERSE",
            "COMPARATIVE_STUDY",
        ],
    )
    create.add_argument("--language", default="ru")

    sub.add_parser("list", help="List projects")

    args = parser.parse_args()
    manager = AnalysisProjectManager()

    if args.command == "create":
        path = manager.create_project(
            args.project_id,
            args.title,
            args.type,
            args.language,
        )
        print(f"CREATED: {path}")
        print((path / "project.json").read_text(encoding="utf-8"))

    elif args.command == "list":
        print(json.dumps(manager.list_projects(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
