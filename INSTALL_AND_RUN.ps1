\
cd "G:\1"

# ============================================================
# BOOK-CRAFT
# SKELETON V1.2
# ЭТАП: маршруты + отдельная Аналитика + interaction states
# ============================================================

$ErrorActionPreference = "Stop"
$Target = "G:\1\BOOKCRAFT-SITE"
$Package = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Test-Path $Target) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Rename-Item -LiteralPath $Target -NewName "BOOKCRAFT-SITE_backup_$Stamp"
}

New-Item -ItemType Directory -Path $Target -Force | Out-Null

Get-ChildItem -LiteralPath $Package -Force |
    Where-Object { $_.Name -ne "INSTALL_AND_RUN.ps1" } |
    Copy-Item -Destination $Target -Recurse -Force

Copy-Item -LiteralPath "$Package\INSTALL_AND_RUN.ps1" -Destination "$Target\INSTALL_AND_RUN.ps1" -Force

Set-Location $Target

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

Write-Host ""
Write-Host "Checking production build..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "BOOK-CRAFT SKELETON V1.2 — BUILD OK" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

$Cmd = "Set-Location -LiteralPath '$Target'; npm run dev -- --host 127.0.0.1 --port 5180"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $Cmd
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5180"
