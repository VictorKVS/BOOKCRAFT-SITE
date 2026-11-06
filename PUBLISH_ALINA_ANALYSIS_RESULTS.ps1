$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 - PUBLISH ANALYSIS RESULTS ===" -ForegroundColor Cyan

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
        if ($LASTEXITCODE -ne 0) {
            throw "git add failed for $p"
        }
    }
}

# Never stage local source materials.
if (Test-Path "$project\sources") {
    git reset -- "$project\sources" 2>$null
}

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "NO_CHANGES analysis results already published"
    exit 0
}

Write-Host "FILES TO COMMIT:"
$staged | ForEach-Object { Write-Host $_ }

$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
git commit -m "analysis: publish ALINA results $stamp"
if ($LASTEXITCODE -ne 0) {
    throw "git commit failed"
}

git push origin alina-book-2
if ($LASTEXITCODE -ne 0) {
    throw "git push failed"
}

Write-Host "PASS analysis_results_committed"
Write-Host "PASS analysis_results_pushed"
Write-Host "=== ALINA BOOK 2 ANALYSIS RESULTS: PUBLISHED ===" -ForegroundColor Green
