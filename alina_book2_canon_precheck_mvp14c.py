from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
STRUCTURE = PROJECT / "structure"
STATE = PROJECT / "state"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def has_cyrillic(s: str) -> bool:
    return bool(re.search(r"[А-Яа-яЁё]", s or ""))


def has_latin(s: str) -> bool:
    return bool(re.search(r"[A-Za-z]", s or ""))


def mixed_script(s: str) -> bool:
    return has_cyrillic(s) and has_latin(s)


def normalize_surface(s: str) -> str:
    s = (s or "").strip().casefold()
    s = s.replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    return s


def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14C CANON PRECHECK ===")

    chapters_path = STRUCTURE / "chapters.json"
    canon_path = STATE / "literary_canon_raw.json"
    if not chapters_path.exists() or not canon_path.exists():
        print("FAIL required_artifacts_missing")
        return 1

    chapters = load_json(chapters_path)
    canon = load_json(canon_path)

    findings = []
    metrics = {}

    # 1. Structure anomaly detection
    sizes = [c.get("paragraph_count", 0) for c in chapters if c.get("paragraph_count", 0) > 0]
    median = sorted(sizes)[len(sizes)//2] if sizes else 0
    oversized = []
    threshold = max(250, median * 3 if median else 250)
    for c in chapters:
        if c.get("paragraph_count", 0) > threshold:
            oversized.append(c)
            findings.append({
                "severity": "BLOCKER",
                "type": "STRUCTURE_OVERSIZED_CHAPTER",
                "detail": f"chapter_index={c.get('chapter_index')} title={c.get('title')} paragraphs={c.get('paragraph_count')} threshold={threshold}"
            })
    metrics["chapter_median_paragraphs"] = median
    metrics["oversized_chapters"] = len(oversized)

    # 2. Duplicate / alias candidate detection
    chars = canon.get("characters", [])
    normalized_map = defaultdict(list)
    for i, ch in enumerate(chars):
        normalized_map[normalize_surface(ch.get("name", ""))].append((i, ch.get("name", "")))
    exact_dupes = {k:v for k,v in normalized_map.items() if k and len(v) > 1}
    for k, vals in exact_dupes.items():
        findings.append({
            "severity": "ERROR",
            "type": "DUPLICATE_SURFACE_NAME",
            "detail": f"{k}: {[name for _,name in vals]}"
        })
    metrics["exact_duplicate_name_groups"] = len(exact_dupes)

    # 3. Known transliteration / alias collision heuristics
    translit_pairs = [
        ("alice", "алиса"), ("alica", "алиса"),
        ("djavat", "джавад"), ("pavel", "павел"),
        ("nikolai nikolaevich", "николай николаевич"),
        ("fima", "фима"), ("kolya", "коля")
    ]
    names = [ch.get("name", "") for ch in chars]
    names_cf = {normalize_surface(n): n for n in names}
    alias_candidates = []
    for a,b in translit_pairs:
        if a in names_cf and b in names_cf:
            alias_candidates.append((names_cf[a], names_cf[b]))
            findings.append({
                "severity": "WARN",
                "type": "TRANSLITERATION_ALIAS_CANDIDATE",
                "detail": f"{names_cf[a]} <-> {names_cf[b]}"
            })
    metrics["transliteration_alias_candidates"] = len(alias_candidates)

    # 4. Mixed-script contamination
    mixed = []
    def scan_value(path, value):
        if isinstance(value, str) and mixed_script(value):
            mixed.append((path, value))
        elif isinstance(value, list):
            for idx, x in enumerate(value):
                scan_value(f"{path}[{idx}]", x)
        elif isinstance(value, dict):
            for k, v in value.items():
                scan_value(f"{path}.{k}", v)

    scan_value("canon", canon)
    for path, value in mixed[:100]:
        findings.append({
            "severity": "WARN",
            "type": "MIXED_SCRIPT_TEXT",
            "detail": f"{path}: {value[:160]}"
        })
    metrics["mixed_script_occurrences"] = len(mixed)

    # 5. Evidence quality heuristics
    unsupported_evidence = 0
    english_evidence = 0
    source_quote_count = 0

    for ch in chars:
        for ev in ch.get("evidence", []):
            if isinstance(ev, str):
                if has_cyrillic(ev):
                    source_quote_count += 1
                elif has_latin(ev):
                    english_evidence += 1

    for coll_name in ("locations", "objects", "events", "world_rules"):
        for item in canon.get(coll_name, []):
            for ev in item.get("evidence", []):
                if isinstance(ev, str):
                    if has_cyrillic(ev):
                        source_quote_count += 1
                    elif has_latin(ev):
                        english_evidence += 1

    if english_evidence:
        findings.append({
            "severity": "ERROR",
            "type": "NON_SOURCE_EVIDENCE_TEXT",
            "detail": f"{english_evidence} evidence entries appear to be English/model paraphrases rather than source quotations"
        })
    metrics["source_like_evidence_entries"] = source_quote_count
    metrics["english_evidence_entries"] = english_evidence

    # 6. Contradiction signals inside one merged entity
    contradiction_patterns = [
        (re.compile(r"\b14 years old\b", re.I), re.compile(r"\b12 years old\b", re.I)),
        (re.compile(r"from konotop", re.I), re.compile(r"from kostroma", re.I)),
    ]
    contradictions = []
    for ch in chars:
        facts = [str(x) for x in ch.get("facts", [])]
        joined = "\n".join(facts)
        for p1, p2 in contradiction_patterns:
            if p1.search(joined) and p2.search(joined):
                contradictions.append(ch.get("name", ""))
                findings.append({
                    "severity": "BLOCKER",
                    "type": "ENTITY_CONTRADICTION",
                    "detail": f"{ch.get('name')}: conflicting facts matched"
                })
    metrics["entities_with_detected_contradictions"] = len(set(contradictions))

    # Decision
    blockers = sum(1 for f in findings if f["severity"] == "BLOCKER")
    errors = sum(1 for f in findings if f["severity"] == "ERROR")
    warns = sum(1 for f in findings if f["severity"] == "WARN")

    status = "PASS" if blockers == 0 and errors == 0 else "CONDITIONAL"

    report = {
        "stage": "MVP-14C_PRECHECK",
        "status": status,
        "metrics": metrics,
        "counts": {
            "blockers": blockers,
            "errors": errors,
            "warnings": warns,
            "findings": len(findings)
        },
        "findings": findings
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    (RUNS / "mvp14c_precheck.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# MVP-14C Canon Precheck",
        "",
        f"Status: {status}",
        f"Blockers: {blockers}",
        f"Errors: {errors}",
        f"Warnings: {warns}",
        "",
        "## Metrics",
    ]
    for k, v in metrics.items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Findings"]
    for f in findings[:200]:
        lines.append(f"- [{f['severity']}] {f['type']}: {f['detail']}")

    (REPORTS / "MVP14C_PRECHECK.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"STATUS: {status}")
    print(f"BLOCKERS: {blockers}")
    print(f"ERRORS: {errors}")
    print(f"WARNINGS: {warns}")
    print(f"PASS report_written: {REPORTS / 'MVP14C_PRECHECK.md'}")
    print(f"PASS run_written: {RUNS / 'mvp14c_precheck.json'}")
    print("=== ALINA BOOK 2 MVP-14C CANON PRECHECK: COMPLETE ===")

    return 0 if status in ("PASS", "CONDITIONAL") else 1


if __name__ == "__main__":
    sys.exit(main())
