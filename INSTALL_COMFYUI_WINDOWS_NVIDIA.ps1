$ErrorActionPreference = "Stop"

$Root = "G:\1"
$Target = "G:\1\ComfyUI_windows_portable"
$DownloadDir = "G:\1\_downloads"
$Archive = Join-Path $DownloadDir "ComfyUI_windows_portable_nvidia.7z"

Write-Host "=== ALINA BOOK 2 / COMFYUI AUTO INSTALL ===" -ForegroundColor Cyan

function Stop-Install([string]$Message) {
    throw $Message
}

try {
    Write-Host ""
    Write-Host "[1/8] NVIDIA CHECK"
    $gpu = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null
    if (-not $gpu) { Stop-Install "NVIDIA GPU is not visible through nvidia-smi" }
    Write-Host "PASS NVIDIA: $gpu" -ForegroundColor Green

    Write-Host ""
    Write-Host "[2/8] DIRECTORIES"
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null
    Write-Host "PASS directories" -ForegroundColor Green

    $Launcher = Join-Path $Target "run_nvidia_gpu.bat"
    if (Test-Path $Launcher) {
        Write-Host "ComfyUI already installed: $Target" -ForegroundColor Yellow
        Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", "`"$Launcher`"") -WorkingDirectory $Target
        Write-Host "INSTALL RESULT: ALREADY_INSTALLED" -ForegroundColor Green
        exit 0
    }

    Write-Host ""
    Write-Host "[3/8] GITHUB RELEASE"
    $Headers = @{ "User-Agent" = "ALINA-BOOK-2"; "Accept" = "application/vnd.github+json" }
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/Comfy-Org/ComfyUI/releases/latest" -Headers $Headers
    $Asset = $Release.assets | Where-Object { $_.name -eq "ComfyUI_windows_portable_nvidia.7z" } | Select-Object -First 1
    if (-not $Asset) { Stop-Install "Official NVIDIA portable asset was not found" }
    Write-Host "Release : $($Release.tag_name)"
    Write-Host "Asset   : $($Asset.name)"
    Write-Host ("Size    : {0:N2} GB" -f ($Asset.size / 1GB))

    Write-Host ""
    Write-Host "[4/8] 7-ZIP"
    $SevenZipCandidates = @("C:\Program Files\7-Zip\7z.exe", "C:\Program Files (x86)\7-Zip\7z.exe")
    $SevenZip = $SevenZipCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $SevenZip) {
        Write-Host "Installing 7-Zip through winget..."
        & winget install --id 7zip.7zip -e --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { Stop-Install "winget failed to install 7-Zip" }
        $SevenZip = $SevenZipCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    }
    if (-not $SevenZip) { Stop-Install "7-Zip executable not found" }
    Write-Host "PASS 7-Zip: $SevenZip" -ForegroundColor Green

    Write-Host ""
    Write-Host "[5/8] DOWNLOAD"
    $NeedDownload = $true
    if (Test-Path $Archive) {
        $ExistingSize = (Get-Item $Archive).Length
        if ($ExistingSize -eq $Asset.size) {
            Write-Host "Existing archive has expected size; hash will be verified."
            $NeedDownload = $false
        } else {
            Write-Host "Removing incomplete archive: $ExistingSize bytes" -ForegroundColor Yellow
            Remove-Item $Archive -Force
        }
    }

    if ($NeedDownload) {
        $Part = "$Archive.part"
        if (Test-Path $Part) { Remove-Item $Part -Force }
        Write-Host ("Downloading {0:N2} GB..." -f ($Asset.size / 1GB))
        try {
            Start-BitsTransfer -Source $Asset.browser_download_url -Destination $Part -DisplayName "ComfyUI NVIDIA Portable" -Description "ALINA BOOK 2 image backend"
        } catch {
            Write-Host "BITS failed; using Invoke-WebRequest fallback..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $Part -UseBasicParsing
        }
        if (-not (Test-Path $Part)) { Stop-Install "Download did not create archive file" }
        $DownloadedSize = (Get-Item $Part).Length
        if ($DownloadedSize -ne $Asset.size) { Stop-Install "Downloaded file size mismatch. Expected $($Asset.size), got $DownloadedSize" }
        Move-Item $Part $Archive -Force
    }
    if (-not (Test-Path $Archive)) { Stop-Install "Archive does not exist after download stage" }
    Write-Host "PASS DOWNLOAD: $Archive" -ForegroundColor Green

    Write-Host ""
    Write-Host "[6/8] SHA256"
    $ActualHash = (Get-FileHash $Archive -Algorithm SHA256).Hash.ToLower()
    $ExpectedHash = $null
    if ($Asset.digest -and $Asset.digest.StartsWith("sha256:")) { $ExpectedHash = $Asset.digest.Substring(7).ToLower() }
    Write-Host "Actual   : $ActualHash"
    if ($ExpectedHash) {
        Write-Host "Expected : $ExpectedHash"
        if ($ActualHash -ne $ExpectedHash) { Stop-Install "SHA256 mismatch" }
        Write-Host "PASS SHA256" -ForegroundColor Green
    } else {
        Write-Host "WARNING: release metadata contains no SHA256 digest" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "[7/8] EXTRACT"
    if (Test-Path $Target) {
        $Existing = @(Get-ChildItem $Target -Force -ErrorAction SilentlyContinue)
        if ($Existing.Count -gt 0) { Stop-Install "Target directory already exists and is not empty: $Target" }
        Remove-Item $Target -Force -Recurse -ErrorAction SilentlyContinue
    }
    & $SevenZip x $Archive "-o$Root" -y
    if ($LASTEXITCODE -ne 0) { Stop-Install "7-Zip extraction failed with code $LASTEXITCODE" }
    if (-not (Test-Path $Launcher)) { Stop-Install "Launcher was not found after extraction: $Launcher" }
    Write-Host "PASS EXTRACT: $Target" -ForegroundColor Green

    Write-Host ""
    Write-Host "[8/8] START"
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", "`"$Launcher`"") -WorkingDirectory $Target

    Write-Host ""
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host "COMFYUI INSTALL: PASS" -ForegroundColor Green
    Write-Host "PATH: $Target"
    Write-Host "API:  http://127.0.0.1:8188"
    Write-Host "==============================================" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "COMFYUI INSTALL: FAIL" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}