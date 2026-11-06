import json
from pathlib import Path

from alina_book2.final_acceptance import StatefulBookRunner, write_evidence


def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)


def main():
    runner = StatefulBookRunner(model="qwen2.5:7b")

    objectives = [
        "Анна исследует коридор и источник металлического стука, не открывая дверь.",
        "Анна продолжает расследование, опираясь только на уже известные факты и результаты предыдущей принятой сцены."
    ]

    result = runner.run_two_scenes("examples/story_mvp04.txt", objectives)

    print("=== SCENE 1 ===")
    print(result.get("scene_1", {}).get("prose", ""))
    print("=== SCENE 2 ===")
    print(result.get("scene_2", {}).get("prose", ""))

    ok = True
    ok &= check(
        "two_scene_pipeline_completed",
        result.get("ok") is True and result.get("status") == "FINAL_ACCEPTANCE_PASS",
        {"status": result.get("status")}
    )

    versions = result.get("state_versions", [])
    ok &= check(
        "narrative_state_advances_between_scenes",
        len(versions) == 3 and versions[1] == versions[0] + 1 and versions[2] == versions[1] + 1,
        {"versions": versions}
    )

    events = result.get("state_v3", {}).get("events", [])
    ok &= check(
        "accepted_scenes_are_committed_to_state",
        len(events) >= 3,
        {"event_count": len(events)}
    )

    ok &= check(
        "second_scene_semantic_guard_passes",
        result.get("scene_2_semantic_report", {}).get("decision") == "PASS",
        result.get("scene_2_semantic_report", {})
    )

    evidence_path = write_evidence(
        result,
        "evidence/alina_book_2_final_acceptance_mvp06.json"
    )
    ok &= check(
        "final_evidence_written",
        evidence_path.exists() and evidence_path.stat().st_size > 0,
        {"path": str(evidence_path), "bytes": evidence_path.stat().st_size if evidence_path.exists() else 0}
    )

    print("=== ALINA BOOK 2 FINAL ACCEPTANCE MVP-06 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    print("EVIDENCE:", evidence_path)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
