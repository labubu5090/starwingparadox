<#
.SYNOPSIS
    Automated Procmon capture of NesysService.exe (Run 4).
.DESCRIPTION
    Requires administrator privileges.
    Clears stale filters, captures NesysService lifecycle, exports CSV, extracts PID rows.
.EXAMPLE
    .\capture-nesysservice-run4.ps1
#>

$ErrorActionPreference = "Stop"

# ── Require admin ────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "FATAL: This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'." -ForegroundColor Yellow
    exit 1
}

# ── Paths ────────────────────────────────────────────────
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$Procmon     = "$ProjectRoot\tools\external\ProcessMonitor\Procmon64.exe"
$NesysExe    = "X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe"
$RuntimeDir  = "$ProjectRoot\runtime\procmon"
$Python      = "$ProjectRoot\server\.venv\Scripts\python.exe"
$Extractor   = "$ProjectRoot\tools\game\procmon\extract_procmon_pid.py"

# ── Timestamp ────────────────────────────────────────────
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$CaptureDir  = "$RuntimeDir\run4_$ts"
$PmlFile     = "$CaptureDir\nesys_run4.pml"
$CsvFull     = "$CaptureDir\nesys_run4_full.csv"
$CsvPid      = "$CaptureDir\nesys_run4_pid.csv"
$SummaryJson = "$CaptureDir\nesys_run4_summary.json"
$MetadataJson= "$CaptureDir\nesys_run4_metadata.json"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NESYSSERVICE RUN 4 AUTOMATED CAPTURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Capture dir: $CaptureDir" -ForegroundColor Gray

# ── Pre-flight checks ───────────────────────────────────
Write-Host "`n[1/10] Pre-flight checks..." -ForegroundColor Yellow

if (-not (Test-Path $Procmon)) {
    Write-Host "FATAL: Procmon not found at $Procmon" -ForegroundColor Red; exit 1
}
Write-Host "  Procmon: OK" -ForegroundColor Green

if (-not (Test-Path $NesysExe)) {
    Write-Host "FATAL: NesysService not found at $NesysExe" -ForegroundColor Red; exit 1
}
Write-Host "  NesysService: OK" -ForegroundColor Green

if (-not (Test-Path $Python)) {
    Write-Host "FATAL: Python not found at $Python" -ForegroundColor Red; exit 1
}
Write-Host "  Python: OK" -ForegroundColor Green

if (-not (Test-Path $Extractor)) {
    Write-Host "FATAL: Extractor not found at $Extractor" -ForegroundColor Red; exit 1
}
Write-Host "  Extractor: OK" -ForegroundColor Green

# ── Kill stale Procmon ──────────────────────────────────
Write-Host "`n[2/10] Cleaning stale Procmon..." -ForegroundColor Yellow
$stale = Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue
if ($stale) {
    foreach ($p in $stale) {
        Write-Host "  Killing stale Procmon PID=$($p.Id)" -ForegroundColor Yellow
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 3
}
# Verify clean
$still = Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue
if ($still) {
    Write-Host "WARNING: Could not kill all Procmon processes. Continuing." -ForegroundColor Yellow
} else {
    Write-Host "  Clean" -ForegroundColor Green
}

# ── Create capture directory ─────────────────────────────
Write-Host "`n[3/10] Creating capture directory..." -ForegroundColor Yellow
if (Test-Path $CaptureDir) {
    Write-Host "FATAL: Capture directory already exists: $CaptureDir" -ForegroundColor Red; exit 1
}
New-Item -ItemType Directory -Path $CaptureDir -Force | Out-Null
Write-Host "  Created: $CaptureDir" -ForegroundColor Green

# ── Record metadata ──────────────────────────────────────
Write-Host "`n[4/10] Recording metadata..." -ForegroundColor Yellow
$gitHead = (git -C $ProjectRoot rev-parse HEAD 2>&1).Trim()
$procmonSha = (Get-FileHash -Path $Procmon -Algorithm SHA256).Hash
$nesysSha = (Get-FileHash -Path $NesysExe -Algorithm SHA256).Hash
$procmonVersion = (Get-Item $Procmon).VersionInfo.FileVersion

$metadata = @{
    timestamp = $ts
    git_head = $gitHead
    procmon_path = $Procmon
    procmon_sha256 = $procmonSha
    procmon_version = $procmonVersion
    nesys_path = $NesysExe
    nesys_sha256 = $nesysSha
    pml_file = $PmlFile
    csv_full = $CsvFull
    csv_pid = $CsvPid
    d_drive_mapped = (Test-Path "D:\")
    admin_user = [Security.Principal.WindowsIdentity]::GetCurrent().Name
}
$metadata | ConvertTo-Json -Depth 5 | Out-File -FilePath $MetadataJson -Encoding utf8
Write-Host "  Metadata saved" -ForegroundColor Green

# ── Start Procmon capture (no filters) ──────────────────
Write-Host "`n[5/10] Starting Procmon capture (no filters)..." -ForegroundColor Yellow

# Use /BackingFile to start capture directly, /OnConnection 1 to begin immediately
# /AcceptEula to skip the EULA dialog
# This starts Procmon with ZERO filters - captures everything
$procmonArgs = "/AcceptEula /BackingFile `"$PmlFile`" /OnConnection 1"
Write-Host "  Args: $procmonArgs" -ForegroundColor Gray

$procmonProc = Start-Process -FilePath $Procmon -ArgumentList $procmonArgs -PassThru -ErrorAction Stop
Write-Host "  Procmon PID: $($procmonProc.Id)" -ForegroundColor Green

# Wait for Procmon to initialize
Start-Sleep -Seconds 3

# Verify Procmon is running
$pmCheck = Get-Process -Id $procmonProc.Id -ErrorAction SilentlyContinue
if (-not $pmCheck) {
    Write-Host "FATAL: Procmon exited immediately" -ForegroundColor Red; exit 1
}
Write-Host "  Procmon is running" -ForegroundColor Green

# ── Launch NesysService ─────────────────────────────────
Write-Host "`n[6/10] Launching NesysService.exe..." -ForegroundColor Yellow
$nesysDir = [System.IO.Path]::GetDirectoryName($NesysExe)

$nesysProc = Start-Process -FilePath $NesysExe `
    -WorkingDirectory $nesysDir `
    -PassThru -ErrorAction Stop

$nesysPid = $nesysProc.Id
Write-Host "  NesysService PID: $nesysPid" -ForegroundColor Green
Write-Host "  Working directory: $nesysDir" -ForegroundColor Gray

# ── Wait for NesysService to exit ────────────────────────
Write-Host "`n[7/10] Waiting for NesysService to exit..." -ForegroundColor Yellow
try {
    $nesysProc.WaitForExit(15000)  # 15 second timeout
    $exitCode = $nesysProc.ExitCode
    Write-Host "  NesysService exited with code: $exitCode" -ForegroundColor Yellow
} catch {
    Write-Host "  NesysService still running after 15s. Forcing..." -ForegroundColor Yellow
    Stop-Process -Id $nesysPid -Force -ErrorAction SilentlyContinue
    $exitCode = -999
}

# ── Post-exit buffer ─────────────────────────────────────
Write-Host "`n[8/10] Post-exit buffer (3 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# ── Stop Procmon ─────────────────────────────────────────
Write-Host "`n[9/10] Stopping Procmon capture..." -ForegroundColor Yellow

# Try to stop Procmon cleanly via its /Terminate command
# Procmon v4.1 responds to WM_CLOSE or can be killed
$pmStill = Get-Process -Id $procmonProc.Id -ErrorAction SilentlyContinue
if ($pmStill) {
    Write-Host "  Sending close to Procmon..." -ForegroundColor Gray
    Stop-Process -Id $procmonProc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
}

# Verify Procmon is gone
$pmFinal = Get-Process -Id $procmonProc.Id -ErrorAction SilentlyContinue
if ($pmFinal) {
    Write-Host "WARNING: Procmon still running" -ForegroundColor Yellow
} else {
    Write-Host "  Procmon stopped" -ForegroundColor Green
}

# ── Verify PML ───────────────────────────────────────────
Write-Host "`n[10/10] Verifying PML and exporting CSV..." -ForegroundColor Yellow

if (-not (Test-Path $PmlFile)) {
    Write-Host "FATAL: PML not created: $PmlFile" -ForegroundColor Red; exit 1
}
$pmlSize = (Get-Item $PmlFile).Length
Write-Host "  PML size: $pmlSize bytes" -ForegroundColor Green

if ($pmlSize -lt 1000) {
    Write-Host "WARNING: PML is very small ($pmlSize bytes). Capture may have failed." -ForegroundColor Yellow
}

$pmlSha = (Get-FileHash -Path $PmlFile -Algorithm SHA256).Hash
Write-Host "  PML SHA-256: $pmlSha" -ForegroundColor Gray

# ── Attempt CSV export ───────────────────────────────────
Write-Host "`n  Attempting CSV export..." -ForegroundColor Yellow

# Procmon v4.1 command-line CSV export is unreliable.
# Try it anyway - if it fails, we'll use the fallback.
$csvExported = $false

try {
    # Use /OpenLog + /SaveAs in a single command
    $exportProc = Start-Process -FilePath $Procmon `
        -ArgumentList "/OpenLog `"$PmlFile`" /SaveAs `"$CsvFull`"" `
        -PassThru -ErrorAction Stop

    # Wait for export (up to 60 seconds)
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Seconds 5
        if (Test-Path $CsvFull) {
            $csvSize = (Get-Item $CsvFull).Length
            if ($csvSize -gt 100) {
                $csvExported = $true
                Write-Host "  CSV exported: $csvSize bytes" -ForegroundColor Green
                break
            }
        }
        Write-Host "  Waiting... ($($i*5)s)" -ForegroundColor Gray
    }

    # Kill the export Procmon
    $exportStill = Get-Process -Id $exportProc.Id -ErrorAction SilentlyContinue
    if ($exportStill) {
        Stop-Process -Id $exportProc.Id -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "  CSV export attempt failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

if (-not $csvExported) {
    Write-Host "`n  ============================================" -ForegroundColor Yellow
    Write-Host "  CSV EXPORT FAILED AUTOMATICALLY" -ForegroundColor Yellow
    Write-Host "  ============================================" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "  AUTOMATED FALLBACK: Opening Procmon GUI with the PML." -ForegroundColor Yellow
    Write-Host "  Please do ONE thing:" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor White
    Write-Host "    File -> Save As -> Type: CSV" -ForegroundColor White
    Write-Host "    Path: $CsvFull" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "  Then press Enter in this window to continue." -ForegroundColor Yellow
    Write-Host "  ============================================" -ForegroundColor Yellow

    # Open Procmon GUI with the PML
    Start-Process -FilePath $Procmon -ArgumentList "/OpenLog `"$PmlFile`""

    # Wait for operator
    Write-Host "`nPress Enter after saving the CSV..." -ForegroundColor Cyan
    Read-Host

    if (-not (Test-Path $CsvFull)) {
        Write-Host "FATAL: CSV not found after operator export: $CsvFull" -ForegroundColor Red; exit 1
    }
    $csvSize = (Get-Item $CsvFull).Length
    if ($csvSize -lt 100) {
        Write-Host "FATAL: CSV is too small: $csvSize bytes" -ForegroundColor Red; exit 1
    }
    $csvExported = $true
    Write-Host "  CSV obtained from operator export: $csvSize bytes" -ForegroundColor Green

    # Kill Procmon GUI
    Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}

# ── Calculate CSV SHA ────────────────────────────────────
$csvSha = (Get-FileHash -Path $CsvFull -Algorithm SHA256).Hash
Write-Host "  CSV SHA-256: $csvSha" -ForegroundColor Gray

# ── Extract PID rows ─────────────────────────────────────
Write-Host "`n  Extracting PID $nesysPid rows..." -ForegroundColor Yellow

$extractArgs = "--input", "`"$CsvFull`"", "--pid", $nesysPid, "--output", "`"$CsvPid`"", "--summary", "`"$SummaryJson`""
$extractCmd = "& `"$Python`" `"$Extractor`" $extractArgs"
$extractResult = Invoke-Expression $extractCmd 2>&1
Write-Host "  $extractResult" -ForegroundColor Gray

if (-not (Test-Path $CsvPid)) {
    Write-Host "FATAL: PID-specific CSV not created" -ForegroundColor Red
    Write-Host "  NesysService PID $nesysPid was not found in the Procmon capture." -ForegroundColor Red
    Write-Host "  This means Procmon did not capture NesysService events." -ForegroundColor Red
    exit 1
}

$pidCsvSize = (Get-Item $CsvPid).Length
Write-Host "  PID CSV: $pidCsvSize bytes" -ForegroundColor Green

if ($pidCsvSize -lt 10) {
    Write-Host "FATAL: PID CSV is empty. NesysService was not captured." -ForegroundColor Red; exit 1
}

# ── Final summary ────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  RUN 4 CAPTURE COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NesysService PID: $nesysPid" -ForegroundColor White
Write-Host "  Exit code: $exitCode" -ForegroundColor $(if ($exitCode -ne 0) {'Yellow'} else {'Green'})
Write-Host "  PML: $PmlFile ($pmlSize bytes)" -ForegroundColor White
Write-Host "  PML SHA-256: $pmlSha" -ForegroundColor Gray
Write-Host "  Full CSV: $CsvFull ($csvSize bytes)" -ForegroundColor White
Write-Host "  Full CSV SHA-256: $csvSha" -ForegroundColor Gray
Write-Host "  PID CSV: $CsvPid ($pidCsvSize bytes)" -ForegroundColor White
Write-Host "  Summary: $SummaryJson" -ForegroundColor White
Write-Host "  Metadata: $MetadataJson" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan

# Return success
exit 0
