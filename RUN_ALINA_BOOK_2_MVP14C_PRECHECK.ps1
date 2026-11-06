$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14C CANON PRECHECK ===" -ForegroundColor Cyan

python .\alina_book2_canon_precheck_mvp14c.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14C precheck failed"
}

$report = ".\projects\sto_let_tomu_vpered\reports\MVP14C_PRECHECK.md"
$run = ".\projects\sto_let_tomu_vpered\runs\mvp14c_precheck.json"

if (-not (Test-Path $report)) { throw "Missing MVP-14C precheck report" }
if (-not (Test-Path $run)) { throw "Missing MVP-14C precheck run evidence" }

Write-Host "PASS mvp14c_precheck_artifacts_exist"
Write-Host "=== ALINA BOOK 2 MVP-14C PRECHECK: DONE ===" -ForegroundColor Green
