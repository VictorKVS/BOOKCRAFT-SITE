$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-12 REAL IMAGE BACKEND ACCEPTANCE ===" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8188/prompt" -TimeoutSec 5
    Write-Host "PASS comfyui_api_available"
}
catch {
    throw "ComfyUI is not running at http://127.0.0.1:8188"
}

$workflow = "config\comfyui_workflow_api.json"
if (-not (Test-Path $workflow)) {
    throw "Workflow not found: $workflow"
}

$raw = Get-Content $workflow -Raw -Encoding UTF8
if ($raw -match '"_status"\s*:\s*"TEMPLATE_PLACEHOLDER"') {
    throw "ComfyUI workflow is still a placeholder. Export a real workflow in API format first."
}

if ($raw -notmatch '\{\{PROMPT\}\}') {
    throw "Workflow does not contain {{PROMPT}} token"
}

$models = ollama list
if (-not ($models -match "qwen3-vl:8b")) {
    throw "Required qwen3-vl:8b visual critic is not installed"
}

Write-Host "PASS workflow_is_real"
Write-Host "PASS prompt_token_present"
Write-Host "PASS qwen3-vl_visual_critic_available"
Write-Host "=== READY FOR FIRST REAL SCENE GENERATION ===" -ForegroundColor Green
