$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B2.8 RELATION & EVENT STORE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_relation_event_store_mvp14b28.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B2.8 relation/event store failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B2.8 RELATION & EVENT STORE: DONE ===" -ForegroundColor Green
