import json

from alina_book2.production_loop import ProductionLoop


INITIAL_STATE = {
    "version": 1,
    "default_pov": "anna",
    "characters": {
        "anna": {
            "knowledge": ["дверь была заперта"],
            "location": "дом",
        }
    },
    "secrets": {
        "locked_secret": "ключ спрятан в часах"
    },
    "events": [],
    "plot_threads": [],
}


def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)


def main():
    ok = True

    clean = ProductionLoop(INITIAL_STATE)
    r1 = clean.run_scene("Анна должна начать исследовать запертую комнату.")
    ok &= check(
        "clean_scene_is_accepted",
        r1.get("ok") and r1.get("status") == "ACCEPTED" and r1["state"]["version"] == 2,
        {"status": r1.get("status"), "version": r1.get("state", {}).get("version")},
    )

    repair = ProductionLoop(INITIAL_STATE)
    r2 = repair.run_scene("Анна должна начать исследовать запертую комнату.", inject_flaw=True)
    codes = [x["code"] for x in r2.get("initial_findings", [])]
    ok &= check(
        "knowledge_violation_is_detected_and_repaired",
        r2.get("ok") and r2.get("repaired") and "KNOWLEDGE_BEFORE_ACQUISITION" in codes,
        {"status": r2.get("status"), "repaired": r2.get("repaired"), "initial_codes": codes},
    )

    final_codes = [x["code"] for x in r2.get("final_findings", [])]
    ok &= check(
        "repaired_scene_passes_critic",
        r2.get("ok") and final_codes == ["OK"],
        {"final_codes": final_codes},
    )

    ok &= check(
        "accepted_scene_updates_narrative_state",
        r2.get("state", {}).get("version") == 2 and len(r2.get("state", {}).get("events", [])) == 1,
        {"state": r2.get("state")},
    )

    print("=== ALINA BOOK 2 PRODUCTION LOOP MVP-01 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
