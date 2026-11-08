$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA LOCAL FACTORY ===" -ForegroundColor Cyan

$portFrontend = 5180
$portBackend = 8191

function Stop-Port([int]$port) {
    $pids = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
    foreach ($p in $pids) {
        if ($p) {
            Write-Host "Stopping PID=$p on port $port"
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
}

Stop-Port $portFrontend
Stop-Port $portBackend

if (-not (Test-Path ".venv-alina")) {
    Write-Host "Creating Python venv..."
    python -m venv .venv-alina
}

$python = Join-Path $PSScriptRoot ".venv-alina\Scripts\python.exe"
$pip = Join-Path $PSScriptRoot ".venv-alina\Scripts\pip.exe"

Write-Host "Installing/checking backend dependencies..."
& $pip install -r requirements-alina.txt

Write-Host "Starting ALINA backend on http://127.0.0.1:$portBackend ..."
$backend = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","backend.alina_api:app","--host","127.0.0.1","--port","$portBackend","--reload" -WorkingDirectory $PSScriptRoot -PassThru

Start-Sleep -Seconds 2

Write-Host "Starting BOOKCRAFT frontend on http://127.0.0.1:$portFrontend ..."
npm run dev

if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
}
