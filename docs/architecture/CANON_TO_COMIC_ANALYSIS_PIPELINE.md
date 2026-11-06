# ALINA BOOK 2 — Canon → Story → Comic Analysis Pipeline

## Mandatory order

No story continuation or comic generation starts directly from raw prose.

```text
SOURCE BOOK / SERIES
↓
1. INGEST
↓
2. STRUCTURE
↓
3. LITERARY CANON
↓
4. CHARACTER BIBLE
↓
5. WORLD BIBLE
↓
6. KNOWLEDGE / BELIEF STATE
↓
7. BOOK GLOSSARY / CONCEPT DICTIONARY
↓
8. CULTURAL EMBODIMENTS REGISTRY
↓
9. CULTURAL / USER CANON LOCKS
↓
10. VISUAL BIBLE + IDENTITY LOCKS
↓
11. CONTRADICTION CHECK
↓
12. CANON ACCEPTANCE
↓
11. STORY HYPOTHESIS
↓
12. CANON VERIFY
↓
13. STORY / CONTINUATION
↓
14. COMIC ADAPTATION
↓
15. PAGE PLAN
↓
16. PANEL PLAN
↓
17. VISUAL SCENE CONTRACTS
↓
18. LOCAL / EXTERNAL IMAGE GENERATION
↓
19. VISUAL CRITIC
↓
20. COMIC PAGE COMPOSITION
```

## Canon layers

### Literary canon
Facts stated or strongly supported by the source.

### User-locked canon
Project decisions explicitly established by the user.

### Cultural visual canon
A culturally recognized screen/illustration image selected by the user for adaptation recognizability.

This layer must preserve provenance and must not overwrite the source.

### Derived canon
Safe conclusions derived from multiple source facts.

### Hypothesis
Unconfirmed interpretation. Never silently promoted to canon.

## Adaptation rule

The comic may compress narration, reorder presentation for page rhythm, or convert internal narration into visual action/captions, but it may not silently change:
- identity;
- age;
- relationships;
- knowledge state;
- causal history;
- world rules;
- locked visual identity.

## Character identity stability

Each recurring major character receives:
- CHARACTER_BIBLE;
- VISUAL_BIBLE;
- IDENTITY_LOCK;
- EXPRESSION_SET;
- OUTFIT_TIMELINE;
- CONTINUITY_STATE.

These are inherited by every generated comic panel.

## Acceptance statuses

```text
PASS        — safe for production
CONDITIONAL — usable with explicit uncertainty / unresolved locks
REJECT      — generation blocked
```


## Book glossary / concept dictionary

Every project builds a source-grounded dictionary of concepts used by the book.

Each entry stores:
- canonical term;
- aliases / grammatical variants;
- category;
- source-supported definition;
- short operational definition for agents;
- evidence snippets / chunk references;
- related characters, objects, locations and world rules;
- confidence;
- provenance;
- unresolved ambiguity.

Preferred categories:
- TECHNOLOGY
- DEVICE
- ORGANIZATION
- LOCATION
- PROFESSION
- SCIENCE
- CREATURE
- SPECIES
- TRANSPORT
- INSTITUTION
- TIME_TRAVEL
- SOCIAL_CONCEPT
- WORLD_RULE
- OTHER

The glossary is not a generic encyclopedia. A definition must first reflect what the source establishes. External knowledge may be added only in a separately marked layer.

## Cultural embodiments registry

A character may have multiple successful screen, illustration or cultural embodiments.

These are stored separately from literary canon.

Each embodiment records:
- work / adaptation;
- medium;
- year/version when known;
- character;
- visual traits;
- behavioural traits;
- recognizability;
- fidelity to literary canon;
- usefulness for adaptation;
- source/provenance;
- user decision: LOCKED / REFERENCE / REJECTED / UNREVIEWED.

No embodiment silently rewrites source canon.

The final visual identity may combine:
```text
LITERARY CANON
+ USER-SELECTED CULTURAL EMBODIMENT
+ PROJECT VISUAL DESIGN
= ADAPTATION VISUAL IDENTITY
```
