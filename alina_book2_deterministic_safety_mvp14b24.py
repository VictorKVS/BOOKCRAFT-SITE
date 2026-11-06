from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "projects" / "sto_let_tomu_vpered"
EVIDENCE = PROJECT / "evidence" / "chunk_claims_v2"
SOURCES = PROJECT / "sources" / "work_chunks" / "sto_let_tomu_vpered"
STRUCTURE = PROJECT / "structure"
REPORTS = PROJECT / "reports"
RUNS = PROJECT / "runs"

RELATION_WORDS = {
    "друг": ("друг", "друж"),
    "подруга": ("подруг", "друж"),
    "брат": ("брат",),
    "сестра": ("сестр",),
    "муж": ("муж",),
    "жена": ("жен",),
}

IDENTITY_WORDS = {
    "уборщик": ("уборщик",),
    "врач": ("врач", "доктор"),
    "полицейский": ("полицейск", "милиционер"),
    "учитель": ("учител",),
    "пират": ("пират",),
    "робот": ("робот",),
}

HYPOTHETICAL_CUES = (
    "придумал",
    "представил",
    "представила",
    "вообразил",
    "вообразила",
    "а что если",
    "что если",
    "может быть",
    "а может быть",
    "если бы",
)

def norm(s: str) -> str:
    s=(s or "").casefold().replace("ё","е")
    s=re.sub(r"[^a-zа-я0-9\s-]"," ",s)
    return re.sub(r"\s+"," ",s).strip()

def iter_claims(validated: dict[str,Any]):
    for mention in validated.get("mentions",[]):
        for claim in mention.get("claims",[]):
            yield "mention",mention.get("surface",""),claim
    for event in validated.get("events",[]):
        for claim in event.get("claims",[]):
            yield "event",event.get("event",""),claim
    for term in validated.get("terms",[]):
        claim=term.get("definition_claim")
        if isinstance(claim,dict):
            yield "term",term.get("term",""),claim

def context_for(chunk_id: str, claim: dict[str,Any], meta: dict[str,Any], radius: int=5) -> str:
    path=SOURCES/f"{chunk_id}.txt"
    if not path.exists():
        return ""
    paragraphs=[p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    evs=claim.get("evidence",[])
    if not evs:
        return ""
    ps=evs[0].get("paragraph_start")
    pe=evs[0].get("paragraph_end")
    if ps is None or pe is None:
        return ""
    rs=max(0,int(ps)-int(meta["start_paragraph"])-radius)
    re_=min(len(paragraphs)-1,int(pe)-int(meta["start_paragraph"])+radius)
    return "\n\n".join(paragraphs[rs:re_+1])

def contains_any(text: str, stems: tuple[str,...]) -> bool:
    t=norm(text)
    return any(stem in t for stem in stems)

def deterministic_verdict(subject: str, claim: dict[str,Any], context: str) -> tuple[str,str,str]:
    predicate=norm(str(claim.get("predicate","")))
    value=norm(str(claim.get("value","")))
    combined=f"{predicate} {value}"
    ctx=norm(context)
    evs=claim.get("evidence",[])
    quote=norm(str(evs[0].get("quote",""))) if evs else ""

    # 1. Relationship overreach: the relationship itself must be explicit in evidence.
    for relation,stems in RELATION_WORDS.items():
        if contains_any(combined, stems):
            if not contains_any(quote, stems):
                return (
                    "REJECT",
                    "RELATIONSHIP_OVERREACH",
                    f"Claim вводит отношение '{relation}', которого нет в доказательной цитате."
                )

    # 2. Identity overreach: a precise identity label must occur in the evidence itself.
    for identity,stems in IDENTITY_WORDS.items():
        if contains_any(combined, stems):
            if not contains_any(quote, stems):
                return (
                    "REJECT",
                    "IDENTITY_OVERREACH",
                    f"Claim вводит идентичность '{identity}', не установленную доказательной цитатой."
                )

    # 3. Explicit imagined/hypothetical scenario leakage.
    # Apply only to temporal/world-state assertions, not to unrelated facts in a wide context window.
    temporal_markers=("лет назад","через ","сейчас он ","выйдет ","скажет ","ответят ","пропал")
    is_temporal_world_claim=any(x in combined for x in temporal_markers)
    if is_temporal_world_claim:
        cue=next((x for x in HYPOTHETICAL_CUES if x in ctx),None)
        if cue:
            return (
                "REJECT",
                "NARRATIVE_MODE",
                f"Контекст временного/world-state claim содержит маркер воображаемого сценария: '{cue}'."
            )

    # 4. Ownership overreach.
    if predicate in {"имеет","владеет","принадлежит"}:
        possession_stems=("имеет","владе","принадлеж","его ","ее ","свой ")
        if not contains_any(ctx,possession_stems):
            return (
                "REVIEW",
                "PREDICATE_OVERREACH",
                "Контекст показывает доступ/использование, но не доказывает владение."
            )

    return ("PASS","NONE","Детерминированных блокирующих признаков не найдено.")

def main() -> int:
    print("=== ALINA BOOK 2 / MVP-14B2.4 DETERMINISTIC CANON SAFETY FILTER ===")
    index=json.loads((STRUCTURE/"primary_work_chunk_index.json").read_text(encoding="utf-8"))
    meta_by_id={x["chunk_id"]:x for x in index}

    files=sorted(EVIDENCE.glob("primary-*.json"))
    if not files:
        print("FAIL no_claim_files")
        return 1

    checked=passed=review=rejected=0
    errors={}

    for i,path in enumerate(files,1):
        package=json.loads(path.read_text(encoding="utf-8"))
        validated=package["validated"]
        chunk_id=validated["chunk_id"]
        if chunk_id not in meta_by_id:
            continue
        print(f"[{i}/{len(files)}] SAFETY {chunk_id}")

        for scope,subject,claim in iter_claims(validated):
            if claim.get("acceptance") not in {"FINAL_CANON_CANDIDATE","FINAL_REVIEW"}:
                continue
            context=context_for(chunk_id,claim,meta_by_id[chunk_id],radius=5)
            verdict,error_type,reason=deterministic_verdict(subject,claim,context)
            claim["deterministic_safety"]={
                "verdict":verdict,
                "error_type":error_type,
                "reason":reason,
            }
            checked+=1
            errors[error_type]=errors.get(error_type,0)+1
            if verdict=="PASS":
                claim["acceptance"]="SAFE_CANON_CANDIDATE"
                passed+=1
            elif verdict=="REVIEW":
                claim["acceptance"]="SAFETY_REVIEW"
                review+=1
            else:
                claim["acceptance"]="REJECTED_BY_DETERMINISTIC_SAFETY"
                rejected+=1

        path.write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding="utf-8")

    if checked==0:
        print("FAIL zero_final_candidates_checked")
        return 1

    result={
        "stage":"MVP-14B2_4_DETERMINISTIC_CANON_SAFETY",
        "result":"PASS",
        "claims_checked":checked,
        "safe_canon_candidates":passed,
        "review":review,
        "rejected":rejected,
        "error_types":errors,
    }
    RUNS.mkdir(parents=True,exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)
    (RUNS/"mvp14b2_4_deterministic_canon_safety.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"
    )
    lines=[
        "# MVP-14B2.4 Deterministic Canon Safety Filter","",
        f"- Claims checked: {checked}",
        f"- SAFE_CANON_CANDIDATE: {passed}",
        f"- SAFETY_REVIEW: {review}",
        f"- REJECTED: {rejected}","",
        "## Error types"
    ]
    for k,v in sorted(errors.items()):
        lines.append(f"- {k}: {v}")
    (REPORTS/"MVP14B2_4_DETERMINISTIC_CANON_SAFETY_SUMMARY.md").write_text(
        "\n".join(lines),encoding="utf-8"
    )

    print(f"PASS claims_checked: {checked}")
    print(f"PASS safe_canon_candidates: {passed}")
    print(f"CHECK safety_review: {review}")
    print(f"CHECK rejected: {rejected}")
    print("=== ALINA BOOK 2 MVP-14B2.4 DETERMINISTIC CANON SAFETY: PASS ===")
    return 0

if __name__=="__main__":
    sys.exit(main())
