<#
.SYNOPSIS
    Control test: verify Procmon can capture a simple process.
.DESCRIPTION
    Captures notepad.exe to prove the Procmon pipeline works before Run 4.
    Requires administrator privileges.
.EXAMPLE
    .\capture-control-test.ps1
#>

$ErrorActionPreference = "Stop"

# ── Require admin ────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "FATAL: This script requires administrator privileges." -ForegroundColor Red
    exit 1
}

$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$Procmon     = "$ProjectRoot\tools\external\ProcessMonitor\Procmon64.exe"
$Python      = "$ProjectRoot\server\.venv\Scripts\python.exe"
$Extractor   = "$ProjectRoot\tools\game\procmon\extract_procmon_pid.py"
$RuntimeDir  = "$ProjectRoot\runtime\procmon"

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$CaptureDir = "$RuntimeDir\control_$ts"
$PmlFile    = "$CaptureDir\control.pml"
$CsvFull    = "$CaptureDir\control_full.csv"
$CsvPid     = "$CaptureDir\control_pid.csv"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PROCMON CONTROL TEST (Notepad)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Pre-flight ───────────────────────────────────────────
if (-not (Test-Path $Procmon)) { Write-Host "FATAL: Procmon not found" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $Python)) { Write-Host "FATAL: Python not found" -ForegroundColor Red; exit 1 }

# Kill stale Procmon
Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

New-Item -ItemType Directory -Path $CaptureDir -Force | Out-Null

# ── Start Procmon ────────────────────────────────────────
Write-Host "`n[1/7] Starting Procmon capture..." -ForegroundColor Yellow
$pm = Start-Process -FilePath $Procmon `
    -ArgumentList "/AcceptEula /BackingFile `"$PmlFile`" /OnConnection 1" `
    -PassThru
Start-Sleep -Seconds 3

$pmCheck = Get-Process -Id $pm.Id -ErrorAction SilentlyContinue
if (-not $pmCheck) { Write-Host "FATAL: Procmon exited" -ForegroundColor Red; exit 1 }
Write-Host "  Procmon PID: $($pm.Id)" -ForegroundColor Green

# ── Launch Notepad ───────────────────────────────────────
Write-Host "`n[2/7] Launching notepad.exe..." -ForegroundColor Yellow
$noteProc = Start-Process -FilePath "notepad.exe" -PassThru
$notePid = $noteProc.Id
Write-Host "  Notepad PID: $notePid" -ForegroundColor Green

# ── Wait ─────────────────────────────────────────────────
Write-Host "`n[3/7] Waiting 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# ── Close Notepad ────────────────────────────────────────
Write-Host "`n[4/7] Closing Notepad..." -ForegroundColor Yellow
Stop-Process -Id $notePid -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# ── Stop Procmon ─────────────────────────────────────────
Write-Host "`n[5/7] Stopping Procmon..." -ForegroundColor Yellow
Stop-Process -Id $pm.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

# ── Verify PML ───────────────────────────────────────────
Write-Host "`n[6/7] Verifying PML..." -ForegroundColor Yellow
if (-not (Test-Path $PmlFile)) { Write-Host "FATAL: PML not created" -ForegroundColor Red; exit 1 }
$pmlSize = (Get-Item $PmlFile).Length
Write-Host "  PML: $pmlSize bytes" -ForegroundColor Green

# ── Export CSV ───────────────────────────────────────────
Write-Host "`n[7/7] Exporting CSV..." -ForegroundColor Yellow
$csvExported = $false
try {
    $ep = Start-Process -FilePath $Procmon `
        -ArgumentList "/OpenLog `"$PmlFile`" /SaveAs `"$CsvFull`"" `
        -PassThru
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Seconds 5
        if (Test-Path $CsvFull) {
            $csvSize = (Get-Item $CsvFull).Length
            if ($csvSize -gt 100) { $csvExported = $true; break }
        }
    }
    Get-Process -Id $ep.Id -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {}

if (-not $csvExported) {
    Write-Host "  Auto-export failed. Opening GUI for manual save." -ForegroundColor Yellow
    Start-Process -FilePath $Procmon -ArgumentList "/OpenLog `"$PmlFile`""
    Write-Host "  Save CSV to: $CsvFull" -ForegroundColor White
    Write-Host "  Press Enter after saving..." -ForegroundColor Cyan
    Read-Host
    if (-not (Test-Path $CsvFull)) { Write-Host "FATAL: CSV not found" -ForegroundColor Red; exit 1 }
}

$csvSha = (Get-FileHash -Path $CsvFull -Algorithm SHA256).Hash
Write-Host "  CSV: $((Get-Item $CsvFull).Length) bytes SHA=$csvSha" -ForegroundColor Green

# ── Extract Notepad PID ──────────────────────────────────
Write-Host "`n  Extracting Notepad PID $notePid..." -ForegroundColor Yellow
& $Python $Extractor --input $CsvFull --pid $notePid --output $CsvPid 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

if (-not (Test-Path $CsvPid)) {
    Write-Host "`n  FAILED: Notepad PID $notePid not found in capture." -ForegroundColor Red
    Write-Host "  PROCMON_CAPTURE_PIPELINE_FAILED" -ForegroundColor Red
    exit 1
}

$pidRows = (Get-Content $CsvPid | Measure-Object).Count - 1
Write-Host "  SUCCESS: Found $pidRows rows for Notepad PID $notePid" -ForegroundColor Green

# ── Result ───────────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  CONTROL TEST PASSED" -ForegroundColor Green
Write-Host "  Notepad PID: $notePid" -ForegroundColor White
Write-Host "  Matched rows: $pidRows" -ForegroundColor White
Write-Host "  PML: $PmlFile" -ForegroundColor White
Write-Host "  Full CSV: $CsvFull" -ForegroundColor White
Write-Host "  PID CSV: $CsvPid" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan

# Cleanup Procmon
Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

exit 0
