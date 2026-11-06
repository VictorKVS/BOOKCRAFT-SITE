# ComfyUI setup for ALINA BOOK 2 on Windows / NVIDIA

ALINA BOOK 2 treats ComfyUI as an independent local image-generation backend.

Recommended layout:

```text
G:\1\ALINA BOOK 2
G:\1\ComfyUI_windows_portable
```

## Why portable

For ALINA integration we want a predictable local API endpoint and an isolated Python/CUDA environment. The official ComfyUI project provides a Windows portable NVIDIA build for RTX 20-series and newer GPUs.

## Step 1 — preflight

From ALINA BOOK 2:

```powershell
.\CHECK_COMFYUI_ENV.ps1
```

It checks:
- NVIDIA driver visibility;
- common ComfyUI locations;
- port 8188;
- API endpoint;
- model/checkpoint folders.

## Step 2 — install ComfyUI

Use the official NVIDIA portable package from the ComfyUI GitHub releases.

Suggested target:

```text
G:\1\ComfyUI_windows_portable
```

Do not install ComfyUI into the ALINA repository.

## Step 3 — start ComfyUI

Typical portable launcher:

```text
run_nvidia_gpu.bat
```

The expected API endpoint is:

```text
http://127.0.0.1:8188
```

## Step 4 — install a generation model

ALINA does not bundle image model weights.

The selected ComfyUI workflow must reference an image model already installed in ComfyUI. Keep model paths inside ComfyUI or configure shared model paths.

## Step 5 — workflow for ALINA

Create a simple text-to-image workflow in ComfyUI and export it in API format.

Save it as:

```text
G:\1\ALINA BOOK 2\config\comfyui_workflow_api.json
```

The positive prompt input must contain:

```text
{{PROMPT}}
```

Optional negative prompt:

```text
{{NEGATIVE_PROMPT}}
```

ALINA replaces these tokens before sending the workflow to ComfyUI.

## Step 6 — real acceptance

After ComfyUI is running and the workflow is valid:

```powershell
.\RUN_ALINA_BOOK_2_MVP12_REAL.ps1
```

The final chain is:

```text
scene
→ visual contract
→ prompt
→ ComfyUI
→ PNG
→ qwen3-vl
→ PASS / REGENERATE
→ accepted visual asset
```
