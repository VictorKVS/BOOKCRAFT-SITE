$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 FINAL ACCEPTANCE MVP-06 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 93% -> target 100%" -ForegroundColor Yellow

python .\run_final_acceptance_mvp06.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Final Acceptance MVP-06 failed"
}

Write-Host "=== ALINA BOOK 2 FINAL ACCEPTANCE MVP-06: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 100%" -ForegroundColor Green
Write-Host "ALINA BOOK 2 CORE: READY" -ForegroundColor Green
