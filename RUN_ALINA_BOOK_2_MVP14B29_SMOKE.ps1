$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B2.9 KNOWLEDGE GRAPH / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_knowledge_graph_mvp14b29.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B2.9 knowledge graph failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B2.9 KNOWLEDGE GRAPH: DONE ===" -ForegroundColor Green
