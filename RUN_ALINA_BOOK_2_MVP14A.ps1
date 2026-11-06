$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14A SOURCE INGEST ===" -ForegroundColor Cyan

python .\alina_book2_ingest_mvp14a.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14A source ingest failed"
}

$manifest = ".\projects\sto_let_tomu_vpered\source_manifest.json"
$chapters = ".\projects\sto_let_tomu_vpered\structure\chapters.json"
$chunks = ".\projects\sto_let_tomu_vpered\structure\chunk_index.json"

if (-not (Test-Path $manifest)) { throw "Missing source manifest" }
if (-not (Test-Path $chapters)) { throw "Missing chapter structure" }
if (-not (Test-Path $chunks)) { throw "Missing chunk index" }

Write-Host "PASS ingest_artifacts_exist"
Write-Host "=== ALINA BOOK 2 MVP-14A SOURCE INGEST: PASS ===" -ForegroundColor Green
