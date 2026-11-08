from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

SCHEMA_KEYS = ["characters","events","relations","locations","technologies","organizations","time_anchors","claims","open_threads"]


def json_request(url: str, payload: dict[str, Any] | None = None, timeout: int = 600) -> Any:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"}, method="GET" if body is None else "POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def detect_local_model() -> dict[str, Any]:
    explicit = os.getenv("ALINA_LLM_BASE_URL", "").rstrip("/")
    explicit_model = os.getenv("ALINA_LLM_MODEL", "").strip()
    if explicit:
        try:
            json_request(explicit + "/models", timeout=3)
            return {"available":True,"provider":"OPENAI_COMPAT_LOCAL","base_url":explicit,"model":explicit_model or "local-model"}
        except Exception as exc:
            return {"available":False,"provider":"OPENAI_COMPAT_LOCAL","error":str(exc)}
    ollama = os.getenv("ALINA_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    try:
        tags = json_request(ollama + "/api/tags", timeout=3)
        models = [x.get("name") for x in tags.get("models",[]) if x.get("name")]
        preferred = os.getenv("ALINA_OLLAMA_MODEL","").strip()
        model = preferred if preferred in models else (models[0] if models else None)
        if model:
            return {"available":True,"provider":"OLLAMA","base_url":ollama,"model":model,"models":models}
        return {"available":False,"provider":"OLLAMA","models":[]}
    except Exception as exc:
        return {"available":False,"provider":"NONE","error":str(exc)}


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = re.sub(r"^.{3}(?:json)?\s*", "", text)
        text = re.sub(r"\s*.{3}$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise
        data = json.loads(text[start:end+1])
    if not isinstance(data, dict):
        raise ValueError("LLM result is not object")
    for key in SCHEMA_KEYS:
        if not isinstance(data.get(key), list):
            data[key] = []
    return data


def analyze_chunk(model_info: dict[str, Any], chunk: dict[str, Any]) -> dict[str, Any]:
    schema = {
      "characters":[{"name":"","aliases":[],"roles":[],"observed_traits":[],"knowledge":[],"goals":[],"emotions":[],"actions":[],"evidence":""}],
      "events":[{"event":"","participants":[],"location":"","time_expression":"","causes":[],"consequences":[],"evidence":""}],
      "relations":[{"source":"","target":"","relation_type":"","state_change":"","evidence":""}],
      "locations":[{"name":"","facts":[],"evidence":""}],
      "technologies":[{"name":"","facts":[],"limitations":[],"evidence":""}],
      "organizations":[{"name":"","facts":[],"evidence":""}],
      "time_anchors":[{"expression":"","normalized_guess":"","confidence":0.0,"evidence":""}],
      "claims":[{"statement":"","type":"","confidence":0.0,"evidence":""}],
      "open_threads":[{"thread":"","status":"","evidence":""}]
    }
    prompt = (
        "Ты ALINA Evidence Extractor. Анализируй ТОЛЬКО данный фрагмент художественного текста. "
        "Не додумывай. Каждый вывод должен иметь evidence из фрагмента. Верни ТОЛЬКО JSON по схеме:\n"
        + json.dumps(schema, ensure_ascii=False)
        + "\nИсточник: " + chunk["source_name"]
        + "\nРаздел: " + (chunk.get("section_title") or "без заголовка")
        + "\nChunk: " + chunk["chunk_id"]
        + "\nТЕКСТ:\n" + chunk["text"]
    )
    if model_info["provider"] == "OLLAMA":
        payload = {
            "model":model_info["model"],"stream":False,"format":"json",
            "options":{"temperature":0.1},
            "messages":[
                {"role":"system","content":"Ты точный аналитик доказательств. Не выдумывай факты."},
                {"role":"user","content":prompt},
            ],
        }
        result = json_request(model_info["base_url"] + "/api/chat", payload)
        return extract_json(result.get("message",{}).get("content","{}"))
    payload = {
        "model":model_info["model"],"temperature":0.1,
        "response_format":{"type":"json_object"},
        "messages":[
            {"role":"system","content":"Ты точный аналитик доказательств. Не выдумывай факты."},
            {"role":"user","content":prompt},
        ],
    }
    result = json_request(model_info["base_url"] + "/chat/completions", payload)
    return extract_json(result["choices"][0]["message"]["content"])


def fb2_units(path: Path) -> list[dict[str,Any]]:
    tree = ET.parse(path); root = tree.getroot()
    def lname(tag: str) -> str: return tag.split("}")[-1]
    units=[]; ordinal=0
    for elem in root.iter():
        if lname(elem.tag)!="section": continue
        title=""; paragraphs=[]
        for child in elem:
            if lname(child.tag)=="title":
                title=" ".join("".join(x.itertext()).strip() for x in child).strip() or "".join(child.itertext()).strip()
            elif lname(child.tag)=="p":
                txt="".join(child.itertext()).strip()
                if txt: paragraphs.append(txt)
        if paragraphs:
            ordinal+=1; units.append({"ordinal":ordinal,"section_title":title,"text":"\n".join(paragraphs)})
    return units


def pdf_units(path: Path) -> list[dict[str,Any]]:
    from pypdf import PdfReader
    reader=PdfReader(str(path)); units=[]
    for i,page in enumerate(reader.pages):
        text=page.extract_text() or ""
        if text.strip(): units.append({"ordinal":i+1,"section_title":f"Страница {i+1}","text":text})
    return units


def docx_units(path: Path) -> list[dict[str,Any]]:
    from docx import Document
    doc=Document(str(path)); units=[]; current=[]; title=""; ordinal=0
    for p in doc.paragraphs:
        text=p.text.strip()
        if not text: continue
        if p.style.name.lower().startswith("heading"):
            if current:
                ordinal+=1; units.append({"ordinal":ordinal,"section_title":title,"text":"\n".join(current)}); current=[]
            title=text
        else: current.append(text)
    if current:
        ordinal+=1; units.append({"ordinal":ordinal,"section_title":title,"text":"\n".join(current)})
    return units


def txt_units(path: Path) -> list[dict[str,Any]]:
    raw=path.read_bytes(); text=None
    for enc in ("utf-8","utf-8-sig","cp1251"):
        try: text=raw.decode(enc); break
        except UnicodeDecodeError: pass
    text=text if text is not None else raw.decode("utf-8",errors="replace")
    blocks=[x.strip() for x in re.split(r"\n\s*\n",text) if x.strip()]
    return [{"ordinal":i+1,"section_title":"","text":block} for i,block in enumerate(blocks)]


def epub_units(path: Path) -> list[dict[str,Any]]:
    units=[]; ordinal=0
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.lower().endswith((".xhtml",".html",".htm")): continue
            raw=zf.read(name).decode("utf-8",errors="ignore")
            title_match=re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>",raw,flags=re.I|re.S)
            title=re.sub(r"<[^>]+>"," ",title_match.group(1)).strip() if title_match else name
            text=re.sub(r"<[^>]+>","\n",raw); text=re.sub(r"\n\s*\n+","\n\n",text)
            if text.strip():
                ordinal+=1; units.append({"ordinal":ordinal,"section_title":title,"text":text.strip()})
    return units


def extract_units(path: Path) -> list[dict[str,Any]]:
    return {".fb2":fb2_units,".pdf":pdf_units,".docx":docx_units,".txt":txt_units,".epub":epub_units}.get(path.suffix.lower(),lambda _:[])(path)


def chunk_units(source_id: str, source_name: str, units: list[dict[str,Any]], max_chars: int=14000) -> list[dict[str,Any]]:
    chunks=[]; seq=0
    for unit in units:
        paragraphs=[p.strip() for p in re.split(r"\n+",unit["text"]) if p.strip()]
        buffer=[]; size=0
        def emit(text: str):
            nonlocal seq
            seq+=1
            chunks.append({
                "chunk_id":f"{source_id}-CHK-{seq:06d}","source_id":source_id,"source_name":source_name,
                "section_ordinal":unit.get("ordinal"),"section_title":unit.get("section_title",""),
                "text":text,"char_count":len(text),"text_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
            })
        for paragraph in paragraphs:
            if size+len(paragraph)+1>max_chars and buffer:
                emit("\n".join(buffer)); buffer=[]; size=0
            if len(paragraph)>max_chars:
                if buffer: emit("\n".join(buffer)); buffer=[]; size=0
                for pos in range(0,len(paragraph),max_chars): emit(paragraph[pos:pos+max_chars])
                continue
            buffer.append(paragraph); size+=len(paragraph)+1
        if buffer: emit("\n".join(buffer))
    return chunks


def normalize_name(name: str) -> str:
    name=name.casefold().replace("ё","е"); name=re.sub(r"[^a-zа-я0-9 ]+"," ",name)
    return re.sub(r"\s+"," ",name).strip()


def merge_extractions(extractions: list[dict[str,Any]]) -> dict[str,Any]:
    merged={key:[] for key in SCHEMA_KEYS}; char_index={}
    for ext in extractions:
        chunk_id=ext["_chunk"]["chunk_id"]
        for char in ext.get("characters",[]):
            name=str(char.get("name","")).strip(); key=normalize_name(name)
            if not key: continue
            item=char_index.setdefault(key,{
                "name":name,"aliases":set(),"roles":set(),"observed_traits":set(),"knowledge":set(),
                "goals":set(),"emotions":set(),"actions":[],"evidence":[],"chunks":set()
            })
            for field in ("aliases","roles","observed_traits","knowledge","goals","emotions"):
                for value in char.get(field,[]) or []:
                    if str(value).strip(): item[field].add(str(value).strip())
            for value in char.get("actions",[]) or []:
                if str(value).strip(): item["actions"].append(str(value).strip())
            if char.get("evidence"): item["evidence"].append({"chunk_id":chunk_id,"text":str(char["evidence"])})
            item["chunks"].add(chunk_id)
        for key in ("events","relations","locations","technologies","organizations","time_anchors","claims","open_threads"):
            for obj in ext.get(key,[]):
                if isinstance(obj,dict): merged[key].append({**obj,"chunk_id":chunk_id})
    chars=[]
    for item in char_index.values():
        chars.append({k:(sorted(v) if isinstance(v,set) else v) for k,v in item.items()})
    merged["characters"]=chars
    return merged
