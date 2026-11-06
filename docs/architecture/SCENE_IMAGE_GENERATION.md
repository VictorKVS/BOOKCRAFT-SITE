# ALINA BOOK 2 — Scene Image Generation Architecture

## Goal

Allow any accepted narrative scene to be selected and rendered as an image without losing canon, character identity, scene continuity or visual state.

## Pipeline

```text
SELECTED SCENE
→ NARRATIVE STATE
→ VISUAL SCENE CONTRACT
→ CHARACTER VISUAL STATE
→ CAMERA / COMPOSITION
→ LIGHT / ENVIRONMENT
→ IMAGE PROMPT
→ IMAGE GENERATOR
→ VISUAL CRITIC
→ ACCEPT / REGENERATE
→ SCENE ASSET
```

## Source of truth

The image generator never receives only free-form prose.

It receives:
- accepted scene prose;
- scene state;
- character state;
- canon;
- location;
- objects;
- time;
- weather/environment;
- visual continuity;
- allowed / forbidden visual changes.

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
- interaction with other characters.

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

A later image may inherit visual state from the previous accepted image.

```text
IMAGE N
→ VISUAL STATE DELTA
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
- character identity consistency;
- object consistency;
- location consistency;
- continuity check;
- no forbidden visual change.

## Storage

```text
projects/<project_id>/visual/
├── contracts/
├── prompts/
├── generated/
├── accepted/
├── rejected/
└── continuity/
```
