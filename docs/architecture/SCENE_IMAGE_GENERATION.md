# ALINA BOOK 2 — Scene Image Generation Architecture

## Goal

Allow any accepted narrative scene to be selected and rendered as an image without losing canon, character identity, scene continuity, cultural recognizability or visual state.

## Pipeline

```text
SELECTED SCENE
→ NARRATIVE STATE
→ LITERARY CANON
→ CHARACTER / WORLD BIBLE
→ USER-LOCKED CULTURAL VISUAL CANON
→ VISUAL SCENE CONTRACT
→ CHARACTER VISUAL STATE
→ CAMERA / COMPOSITION
→ LIGHT / ENVIRONMENT
→ IMAGE PROMPT
→ IMAGE GENERATOR
→ VISUAL CRITIC
→ CANON / IDENTITY CHECK
→ ACCEPT / REGENERATE
→ SCENE ASSET
```

## Source of truth

The image generator never receives only free-form prose.

It receives:
- accepted scene prose;
- scene state;
- character state;
- literary canon;
- user-locked cultural visual canon;
- location;
- objects;
- time;
- weather/environment;
- visual continuity;
- allowed / forbidden visual changes;
- identity-reference package.

Every visual rule carries provenance:
- SOURCE_CANON;
- USER_LOCKED_CANON;
- USER_LOCKED_CULTURAL_CANON;
- DERIVED;
- HYPOTHESIS.

## Identity Lock

For culturally recognizable characters, ALINA maintains a stable `visual_identity_lock`.

It may include:
- age band;
- facial geometry descriptors;
- hair colour / length / shape;
- eye colour;
- body proportions;
- habitual expression;
- default outfit;
- alternate canonical outfits;
- reference-image IDs where legally and operationally available;
- features that must not drift.

The identity lock is inherited by every panel and illustration.

## Visual Scene Contract

```json
{
  "scene_id": "S-014",
  "shot_id": "S-014-shot-01",
  "characters": [],
  "location": {},
  "objects": [],
  "actions": [],
  "interactions": [],
  "camera": {},
  "composition": {},
  "lighting": {},
  "mood": {},
  "continuity": {},
  "identity_locks": [],
  "forbidden_changes": [],
  "prompt": ""
}
```

## Character visual state

For each character:
- identity;
- age;
- body type;
- face;
- hair;
- clothing;
- injuries;
- carried objects;
- pose;
- gaze direction;
- expression;
- action;
- position in frame;
- interaction with other characters;
- identity-lock provenance.

## Scene visual state

- location;
- architecture;
- weather;
- time of day;
- light source;
- key objects;
- spatial relations;
- atmosphere;
- camera angle;
- lens/framing;
- foreground/background;
- continuity from previous image.

## Interaction layer

The visual system must explicitly encode:
- who looks at whom;
- who touches whom;
- who gives/takes an object;
- who stands/sits/lies;
- relative positions;
- distance;
- gestures;
- emotional interaction.

## Continuity rule

A later image inherits accepted visual state from prior assets.

```text
ACCEPTED IMAGE N
→ VISUAL STATE DELTA
→ IDENTITY LOCK
→ IMAGE N+1
```

## Multiple render modes

- ILLUSTRATION
- CINEMATIC
- COMIC_PANEL
- STORYBOARD
- CHARACTER_FOCUS
- ENVIRONMENT_FOCUS
- ACTION_SHOT

## Acceptance

An image is accepted only after:
- scene alignment;
- literary-canon alignment;
- cultural-visual-canon alignment where locked;
- character identity consistency;
- age consistency;
- object consistency;
- location consistency;
- continuity check;
- no forbidden visual change.

## Storage

```text
projects/<project_id>/visual/
├── bibles/
├── contracts/
├── prompts/
├── generated/
├── accepted/
├── rejected/
└── continuity/
```
