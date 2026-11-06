$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
Write-Host "=== ALINA BOOK 2 MVP-14B2 CLAIM-LEVEL CANON ANALYZER ===" -ForegroundColor Cyan
python .\alina_book2_claims_mvp14b2.py
if ($LASTEXITCODE -ne 0) { throw "MVP-14B2 claim-level analyzer failed" }

$state = ".\projects\sto_let_tomu_vpered\state\literary_claims_raw_v2.json"
$run = ".\projects\sto_let_tomu_vpered\runs\mvp14b2_claim_level_canon.json"
if (-not (Test-Path $state)) { throw "Missing literary_claims_raw_v2.json" }
if (-not (Test-Path $run)) { throw "Missing MVP-14B2 run evidence" }

Write-Host "PASS claim_level_canon_artifacts_exist"
Write-Host "=== ALINA BOOK 2 MVP-14B2 CLAIM-LEVEL CANON: DONE ===" -ForegroundColor Green
