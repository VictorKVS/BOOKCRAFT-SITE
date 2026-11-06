$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 LOCAL IMAGE MODEL PROFILE MVP-13 ===" -ForegroundColor Cyan

python -m unittest .\test_local_image_profile_mvp13.py
if ($LASTEXITCODE -ne 0) {
    throw "Local Image Model Profile MVP-13 failed"
}

Write-Host "PASS local_model_profile"
Write-Host "PASS sdxl_quality_profile"
Write-Host "=== ALINA BOOK 2 LOCAL IMAGE MODEL PROFILE MVP-13: PASS ===" -ForegroundColor Green
