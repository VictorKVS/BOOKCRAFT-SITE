import json
from pathlib import Path

from alina_book2.story_ingest import IngestValidator, StoryIngestor


def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)


def main():
    source_path = Path("examples/story_mvp04.txt")
    source_text = source_path.read_text(encoding="utf-8")

    ingestor = StoryIngestor(model="qwen2.5:7b")
    state = ingestor.ingest_file(source_path)

    print("=== NARRATIVE STATE ===")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print("=== END STATE ===")

    validator = IngestValidator()
    state = validator.repair_evidence(state, source_text)
    report = validator.validate(state, source_text)

    print("=== GROUNDED EVIDENCE REPAIRS ===")
    print(json.dumps(state.get("evidence_repairs", []), ensure_ascii=False, indent=2))

    ok = True
    ok &= check("real_story_has_characters", report["counts"]["characters"] >= 2, report["counts"])
    ok &= check("real_story_has_events", report["counts"]["events"] >= 1, report["counts"])
    ok &= check("real_story_has_locations", report["counts"]["locations"] >= 1, report["counts"])
    ok &= check("evidence_is_grounded_in_source", report["ok"], report)

    names = [
        str(v.get("name", "")).lower()
        for v in state.get("characters", {}).values()
        if isinstance(v, dict)
    ]
    ok &= check(
        "anna_and_mikhail_are_recognized",
        any("анна" in x for x in names) and any("михаил" in x for x in names),
        {"names": names}
    )

    print("=== ALINA BOOK 2 REAL STORY INGEST MVP-04 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
