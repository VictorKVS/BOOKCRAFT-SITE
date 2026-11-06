import json
import urllib.request

from alina_book2.llm_runtime import RealLLMProductionLoop

STATE = {
    "version": 1,
    "default_pov": "anna",
    "characters": {"anna": {"knowledge": ["дверь была заперта"], "location": "дом"}},
    "secrets": {"locked_secret": "служебный факт"},
    "events": [],
    "plot_threads": []
}

def check(name, condition, details=None):
    print(("PASS" if condition else "FAIL"), name, json.dumps(details or {}, ensure_ascii=False))
    return bool(condition)

def models():
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return [x.get("name") for x in payload.get("models", [])]

def main():
    ok = True
    available = models()
    ok &= check("ollama_is_available", bool(available), {"count": len(available)})

    model = "qwen2.5:7b"
    ok &= check("creative_model_is_installed", model in available, {"required": model})
    if model not in available:
        raise SystemExit(1)

    result = RealLLMProductionLoop(STATE, model=model).run_scene(
        "Анна начинает исследовать запертую комнату и действует только на основании известных ей фактов."
    )

    prose = result.get("draft", {}).get("prose", "")
    print("=== REAL DRAFT ===")
    print(prose)
    print("=== END DRAFT ===")

    ok &= check("real_llm_scene_is_accepted",
                result.get("ok") and result.get("status") == "ACCEPTED",
                {"status": result.get("status"), "chars": len(prose)})

    ok &= check("real_llm_scene_has_content", len(prose.strip()) >= 100, {"chars": len(prose)})

    ok &= check("real_llm_scene_updates_state",
                result.get("state", {}).get("version") == 2,
                {"version": result.get("state", {}).get("version")})

    print("=== ALINA BOOK 2 REAL LLM WRITER MVP-02 ===")
    print("RESULT:", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
