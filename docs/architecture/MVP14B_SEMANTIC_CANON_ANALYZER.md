# MVP-14B — Semantic Literary Canon Analyzer

This stage reads the local chunks produced by MVP-14A and uses the local Ollama model to extract literary canon.

It intentionally does **not** merge film/TV/cultural canon into source canon.

Outputs:
- raw character registry;
- locations;
- objects;
- events;
- world rules;
- unresolved questions;
- per-chunk evidence JSON;
- summary/run evidence.

Pipeline:

```text
LOCAL CHUNKS
→ qwen2.5:7b
→ STRICT JSON EXTRACTION
→ PER-CHUNK EVIDENCE
→ RAW LITERARY CANON
→ MVP-14C RECONCILIATION
```

MVP-14C will perform:
- alias/entity resolution;
- contradiction resolution;
- timeline;
- knowledge/belief state;
- character bibles;
- merge of user-locked cultural visual canon;
- final canon acceptance.
