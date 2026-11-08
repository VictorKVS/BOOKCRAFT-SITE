# ALICE CYCLE CORPUS

## Goal

Collect the Alice Selezneva cycle as separate works and ingest each work independently.

The registry currently contains **52 works** from the FantLab cycle catalog.

Important: catalog order is NOT treated as authoritative chronology.

We maintain three independent orders:

1. PUBLICATION_ORDER
2. EXTERNAL_PROPOSED_CHRONOLOGY
3. ALINA_RECONSTRUCTED_CHRONOLOGY

## Per-work target structure

Each work will eventually have:

- metadata
- source document reference
- chapter/segment index
- evidence claims
- entities
- events
- locations
- technologies
- timeline anchors
- character states
- relationships
- contradictions
- cross-work links

Target conceptual layout:

ALICE-001/
  metadata.json
  source/
  chunks/
  evidence/
  entities/
  events/
  timeline/
  contradictions/

...

ALICE-052/

## Ingestion rule

Catalog metadata may come from bibliographic/web sources.

Full copyrighted text is ingested only from user-provided or otherwise legally accessible copies.

## Cross-cycle validation

After works are individually ingested:

WORK LEVEL
-> CROSS-WORK ENTITY RESOLUTION
-> CROSS-WORK TIMELINE
-> TECHNOLOGY CONSISTENCY
-> AGE / BIOGRAPHY CONSISTENCY
-> LOCATION / TRAVEL CONSISTENCY
-> CANON CONTRADICTION MAP
-> RECONSTRUCTED WORLD MODEL
