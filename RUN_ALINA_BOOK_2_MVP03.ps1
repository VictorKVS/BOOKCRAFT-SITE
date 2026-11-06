$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 SEMANTIC GUARD MVP-03 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 65% -> target 75%" -ForegroundColor Yellow

python .\run_semantic_guard_mvp03.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Semantic Guard MVP-03 failed"
}

Write-Host "=== ALINA BOOK 2 SEMANTIC GUARD MVP-03: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 75%" -ForegroundColor Green
