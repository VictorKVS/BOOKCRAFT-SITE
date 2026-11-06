import json
import urllib.request

from alina_book2.llm_runtime import LLMWriter, Producer
from alina_book2.semantic_guard import SemanticCritic, SemanticRepair


STATE = {
    "version": 1,
    "default_pov": "anna",
    "characters": {
        "anna": {
            "knowledge": ["дверь была заперта"],
            "location": "коридор"
        }
    },
    "objects": {},
    "events": [],
    "plot_threads": []
}


def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)


def installed_models():
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return [x.get("name") for x in payload.get("models", [])]


def main():
    model = "qwen2.5:7b"
    available = installed_models()
    ok = check("semantic_model_is_installed", model in available, {"required": model})
    if not ok:
        raise SystemExit(1)

    producer = Producer()
    scene = producer.plan_scene(STATE, "Анна исследует запертую дверь, не открывая её и не находя новых предметов.")

    # Deliberately inconsistent prose to prove that semantic guard catches it.
    draft = {
        "scene_id": scene["scene_id"],
        "prose": "Анна нашла ключ под ковром, открыла дверь и вошла в комнату.",
        "used_secret": None,
        "state_delta": {
            "new_events": [{
                "event_id": "E-test",
                "type": "scene_progress",
                "summary": "Анна исследует запертую дверь."
            }],
            "character_changes": {},
            "new_threads": []
        }
    }

    critic = SemanticCritic(model)
    report = critic.review(scene, STATE, draft)
    print("=== SEMANTIC REPORT ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    ok &= check(
        "prose_state_mismatch_is_detected",
        report.get("decision") == "REPAIR" and len(report.get("issues", [])) > 0,
        {"decision": report.get("decision"), "issue_count": len(report.get("issues", []))}
    )

    repair = SemanticRepair(model)
    fixed = repair.repair(scene, STATE, draft, report)
    second = critic.review(scene, STATE, fixed)

    print("=== REPAIRED DRAFT ===")
    print(fixed["prose"])
    print("=== SECOND SEMANTIC REPORT ===")
    print(json.dumps(second, ensure_ascii=False, indent=2))

    ok &= check(
        "semantic_repair_passes",
        second.get("decision") == "PASS",
        {"decision": second.get("decision"), "issues": second.get("issues", [])}
    )

    print("=== ALINA BOOK 2 SEMANTIC GUARD MVP-03 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
