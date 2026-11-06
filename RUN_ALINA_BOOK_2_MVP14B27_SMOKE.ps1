$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B2.7 ENTITY REGISTRY / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_entity_registry_mvp14b27.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B2.7 entity registry failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B2.7 ENTITY REGISTRY: DONE ===" -ForegroundColor Green
