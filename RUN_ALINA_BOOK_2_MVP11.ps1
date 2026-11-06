$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 REAL VISUAL WORKFLOW MVP-11 ===" -ForegroundColor Cyan

python -m unittest .\test_visual_workflow_mvp11.py
if ($LASTEXITCODE -ne 0) {
    throw "Visual Workflow MVP-11 failed"
}

$models = ollama list
if (-not ($models -match "qwen3-vl:8b")) {
    throw "Required visual critic model qwen3-vl:8b is not installed"
}

Write-Host "PASS visual_workflow_prepare"
Write-Host "PASS qwen3-vl_visual_critic_available"
Write-Host "=== ALINA BOOK 2 REAL VISUAL WORKFLOW MVP-11: PASS ===" -ForegroundColor Green
