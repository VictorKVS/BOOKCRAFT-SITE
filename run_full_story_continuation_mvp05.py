import json

from alina_book2.full_story_pipeline import FullStoryContinuationPipeline


def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)


def main():
    pipeline = FullStoryContinuationPipeline(model="qwen2.5:7b")

    objective = (
        "Продолжить историю: Анна осматривает коридор и пытается понять источник "
        "металлического стука, не открывая дверь и не получая знаний, которых у неё ещё нет."
    )

    result = pipeline.run("examples/story_mvp04.txt", objective)

    print("=== ACCEPTED CONTINUATION CANDIDATE ===")
    print(result.get("draft", {}).get("prose", ""))
    print("=== END CONTINUATION ===")

    print("=== FINAL SEMANTIC REPORT ===")
    print(json.dumps(result.get("final_semantic_report", {}), ensure_ascii=False, indent=2))

    ok = True
    ok &= check(
        "real_story_ingest_is_valid",
        result.get("ingest_validation", {}).get("ok") is True,
        result.get("ingest_validation", {}),
    )

    ok &= check(
        "continuation_is_accepted",
        result.get("ok") is True and result.get("status") == "ACCEPTED_CONTINUATION",
        {"status": result.get("status"), "repaired": result.get("repaired")},
    )

    prose = result.get("draft", {}).get("prose", "")
    ok &= check("continuation_has_content", len(prose.strip()) >= 100, {"chars": len(prose)})

    ok &= check(
        "semantic_guard_final_pass",
        result.get("final_semantic_report", {}).get("decision") == "PASS",
        result.get("final_semantic_report", {}),
    )

    state = result.get("state", {})
    ok &= check(
        "narrative_state_contains_real_characters",
        len(state.get("characters", {})) >= 2,
        {"characters": list(state.get("characters", {}).keys())},
    )

    print("=== ALINA BOOK 2 FULL STORY CONTINUATION MVP-05 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
