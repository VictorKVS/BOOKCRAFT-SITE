$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 SCENE ASSET REGISTRY MVP-09 ===" -ForegroundColor Cyan

python -m unittest .\test_scene_assets_mvp09.py
if ($LASTEXITCODE -ne 0) {
    throw "Scene Asset Registry MVP-09 failed"
}

Write-Host "=== ALINA BOOK 2 SCENE ASSET REGISTRY MVP-09: PASS ===" -ForegroundColor Green
