$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 — PUBLISH ANALYSIS RESULTS ===" -ForegroundColor Cyan

$project = ".\projects\sto_let_tomu_vpered"

$paths = @(
    "$project\source_manifest.json",
    "$project\structure",
    "$project\state",
    "$project\reports",
    "$project\runs",
    "$project\evidence\chunk_analysis"
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        git add -- $p
    }
}

# Explicitly exclude local source material even if ignore rules change later.
git reset -- "$project\sources" 2>$null

$pending = git status --short
if (-not $pending) {
    Write-Host "NO_CHANGES analysis results already published"
    exit 0
}

Write-Host "FILES TO COMMIT:"
$pending | ForEach-Object { Write-Host $_ }

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "analysis: publish ALINA results $stamp"

git push origin alina-book-2

Write-Host "PASS analysis_results_committed"
Write-Host "PASS analysis_results_pushed"
Write-Host "=== ALINA BOOK 2 ANALYSIS RESULTS: PUBLISHED ===" -ForegroundColor Green
