$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:ALINA_MAX_CHUNKS = "3"
try {
    Write-Host "=== ALINA BOOK 2 MVP-14B2.3 CANON PRECISION GATE / SMOKE ===" -ForegroundColor Cyan
    python .\alina_book2_precision_gate_mvp14b23.py
    if ($LASTEXITCODE -ne 0) { throw "MVP-14B2.3 precision gate failed" }
} finally {
    Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
}
Write-Host "=== ALINA BOOK 2 MVP-14B2.3 CANON PRECISION GATE: DONE ===" -ForegroundColor Green
