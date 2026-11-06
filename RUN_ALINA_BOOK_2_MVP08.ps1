$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 VISUAL SCENE CONTRACT MVP-08 ===" -ForegroundColor Cyan

python -m unittest .\test_visual_scene_mvp08.py
if ($LASTEXITCODE -ne 0) {
    throw "Visual Scene Contract MVP-08 failed"
}

Write-Host "=== ALINA BOOK 2 VISUAL SCENE CONTRACT MVP-08: PASS ===" -ForegroundColor Green
