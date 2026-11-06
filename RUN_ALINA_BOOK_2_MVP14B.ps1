$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B SEMANTIC CANON ANALYZER ===" -ForegroundColor Cyan

python .\alina_book2_canon_mvp14b.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B semantic canon analyzer failed"
}

$state = ".\projects\sto_let_tomu_vpered\state\literary_canon_raw.json"
$run = ".\projects\sto_let_tomu_vpered\runs\mvp14b_semantic_canon.json"

if (-not (Test-Path $state)) { throw "Missing literary canon raw state" }
if (-not (Test-Path $run)) { throw "Missing MVP-14B run evidence" }

Write-Host "PASS semantic_canon_artifacts_exist"
Write-Host "=== ALINA BOOK 2 MVP-14B SEMANTIC CANON ANALYZER: PASS ===" -ForegroundColor Green
