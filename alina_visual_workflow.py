import argparse
import json

from alina_book2.visual_workflow import VisualWorkflow, load_contract


def main():
    parser = argparse.ArgumentParser(description="ALINA BOOK 2 visual workflow")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--project", required=True)
    prepare.add_argument("--contract", required=True)

    review = sub.add_parser("review")
    review.add_argument("--project", required=True)
    review.add_argument("--contract", required=True)
    review.add_argument("--image", required=True)

    args = parser.parse_args()
    workflow = VisualWorkflow(args.project)
    contract = load_contract(args.contract)

    if args.command == "prepare":
        result = workflow.prepare(contract)
    else:
        result = workflow.review_and_accept(contract, args.image)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
