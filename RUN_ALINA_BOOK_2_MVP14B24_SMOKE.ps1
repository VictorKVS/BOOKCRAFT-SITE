$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== ALINA BOOK 2 MVP-14B2.4 DETERMINISTIC CANON SAFETY / SMOKE ===" -ForegroundColor Cyan
python .\alina_book2_deterministic_safety_mvp14b24.py
if ($LASTEXITCODE -ne 0) { throw "MVP-14B2.4 deterministic safety failed" }
Write-Host "=== ALINA BOOK 2 MVP-14B2.4 DETERMINISTIC CANON SAFETY: DONE ===" -ForegroundColor Green
