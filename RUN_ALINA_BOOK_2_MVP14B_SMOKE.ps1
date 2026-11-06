$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B SMOKE / FIRST 3 CHUNKS ===" -ForegroundColor Cyan

$env:ALINA_MAX_CHUNKS = "3"
try {
    python .\alina_book2_canon_mvp14b.py
    if ($LASTEXITCODE -ne 0) { throw "MVP-14B smoke failed" }
}
finally {
    Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
}
