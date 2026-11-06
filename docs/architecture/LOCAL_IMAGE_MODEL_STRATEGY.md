# ALINA BOOK 2 — Local Image Model Strategy

## Decision

ALINA BOOK 2 must support both:

1. external / replaceable image providers;
2. a fully local image-generation model running on the user's GPU.

The local model is not embedded into story logic. It is a replaceable image-generation brain behind the same provider contract.

## Hardware target

Current target workstation:
- NVIDIA GeForce RTX 3060;
- 12 GB VRAM;
- Windows 11;
- ComfyUI local backend.

## Default local profiles

### SDXL Quality

Purpose: final book illustration.

Defaults:
- 1024 x 1024;
- batch 1;
- 28 steps;
- CFG 6.5;
- DPM++ 2M;
- Karras scheduler;
- random seed.

This is the default active profile.

### SDXL Fast

Purpose: storyboard / preview / composition search.

Defaults:
- 768 x 768;
- batch 1;
- 6 steps;
- CFG 1.5;
- Euler;
- normal scheduler.

The fast profile remains disabled until an SDXL Turbo-compatible checkpoint is installed and validated.

## Model placement

Local checkpoint files live outside the ALINA repository:

```text
G:\1\ComfyUI_windows_portable\ComfyUI\models\checkpoints
```

ALINA stores only:
- model profile;
- filename;
- inference settings;
- workflow;
- evidence;
- quality results.

Large model weights are never committed to Git.

## Model lifecycle

```text
MODEL CANDIDATE
→ INSTALL
→ HARDWARE CHECK
→ GENERATION TEST
→ VISUAL CRITIC
→ QUALITY BENCHMARK
→ CHAMPION / CHALLENGER
```

Changing the image model must not alter:
- scene contract;
- canon;
- asset registry;
- visual critic;
- continuity memory.

## Local generation flow

```text
SELECTED SCENE
→ VISUAL SCENE CONTRACT
→ LOCAL IMAGE PROFILE
→ COMFYUI WORKFLOW
→ LOCAL MODEL
→ PNG
→ QWEN3-VL VISUAL CRITIC
→ ACCEPT / REGENERATE
→ CONTINUITY REFERENCE
```

## Future local adapters

The same configuration layer may later host:
- SDXL;
- SDXL Turbo;
- Flux quantized / memory-optimized variants;
- Qwen Image;
- other ComfyUI-supported local models.

No new model becomes active until it passes physical acceptance on the target workstation.
