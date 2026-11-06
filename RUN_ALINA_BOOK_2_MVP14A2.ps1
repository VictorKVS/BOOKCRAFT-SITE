$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14A2 WORK BOUNDARY RESOLVER ===" -ForegroundColor Cyan

python .\alina_book2_work_boundary_mvp14a2.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14A2 work boundary resolver failed"
}

$works = ".\projects\sto_let_tomu_vpered\structure\work_boundaries.json"
$index = ".\projects\sto_let_tomu_vpered\structure\primary_work_chunk_index.json"
$run = ".\projects\sto_let_tomu_vpered\runs\mvp14a2_work_boundary.json"

if (-not (Test-Path $works)) { throw "Missing work boundaries" }
if (-not (Test-Path $index)) { throw "Missing primary work chunk index" }
if (-not (Test-Path $run)) { throw "Missing boundary run evidence" }

Write-Host "PASS work_boundary_artifacts_exist"
Write-Host "=== ALINA BOOK 2 MVP-14A2 WORK BOUNDARY: DONE ===" -ForegroundColor Green
