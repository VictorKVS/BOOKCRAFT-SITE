$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 VISUAL PROVIDER + CRITIC MVP-10 ===" -ForegroundColor Cyan

python -m unittest .\test_image_provider_mvp10.py
if ($LASTEXITCODE -ne 0) {
    throw "Image Provider MVP-10 failed"
}

$models = ollama list
if ($models -notmatch "qwen3-vl:8b") {
    throw "Required visual critic model qwen3-vl:8b is not installed"
}

Write-Host "PASS provider_registry"
Write-Host "PASS qwen3-vl_visual_critic_available"
Write-Host "=== ALINA BOOK 2 VISUAL PROVIDER + CRITIC MVP-10: PASS ===" -ForegroundColor Green
