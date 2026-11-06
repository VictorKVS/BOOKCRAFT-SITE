$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 PROJECT FACTORY MVP-07 ===" -ForegroundColor Cyan

python -m unittest .\test_project_manager_mvp07.py
if ($LASTEXITCODE -ne 0) {
    throw "Project Factory unit tests failed"
}

$demoRoot = "projects\demo-war-and-peace"
if (Test-Path $demoRoot) {
    Remove-Item -Recurse -Force $demoRoot
}

python .\alina_projects.py create demo-war-and-peace --title "Война и мир" --type MULTI_VOLUME_BOOK
if ($LASTEXITCODE -ne 0) {
    throw "Project creation failed"
}

python .\alina_projects.py list
if ($LASTEXITCODE -ne 0) {
    throw "Project listing failed"
}

Write-Host "=== ALINA BOOK 2 PROJECT FACTORY MVP-07: PASS ===" -ForegroundColor Green
