<#
.SYNOPSIS
    Complete Procmon investigation: auto-elevates, control test, NesysService capture.
.DESCRIPTION
    Single entry point. Triggers one UAC prompt if not admin.
    After elevation: runs Notepad control test, then NesysService Run 4.
    No manual Procmon filtering required.
.EXAMPLE
    .\run-complete-procmon-investigation.ps1
#>

$ErrorActionPreference = "Stop"

# ── Auto-elevate if not admin ────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Relaunching as Administrator..." -ForegroundColor Yellow
    $scriptPath = $MyInvocation.MyCommand.Definition
    $scriptDir = Split-Path $scriptPath -Parent
    Start-Process PowerShell.exe -Verb RunAs -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", "cd '$scriptDir'; & '$scriptPath'"
    )
    exit
}

# ── Paths ────────────────────────────────────────────────
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$Procmon     = "$ProjectRoot\tools\external\ProcessMonitor\Procmon64.exe"
$NesysExe    = "X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe"
$Python      = "$ProjectRoot\server\.venv\Scripts\python.exe"
$Extractor   = "$ProjectRoot\tools\game\procmon\extract_procmon_pid.py"
$RuntimeDir  = "$ProjectRoot\runtime\procmon"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PROCMON INVESTIGATION - FULL AUTOMATION" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Running as: $([Security.Principal.WindowsIdentity]::GetCurrent().Name)" -ForegroundColor Gray
Write-Host ""

# ── Verify tools ─────────────────────────────────────────
Write-Host "[0] Verifying tools..." -ForegroundColor Yellow

$requiredPaths = @(
    @{ Path = $Procmon; Name = "Procmon64.exe" },
    @{ Path = $NesysExe; Name = "NesysService.exe" },
    @{ Path = $Python; Name = "Python" },
    @{ Path = $Extractor; Name = "extract_procmon_pid.py" }
)
foreach ($req in $requiredPaths) {
    if (-not (Test-Path $req.Path)) {
        Write-Host "  FATAL: $($req.Name) not found at $($req.Path)" -ForegroundColor Red
        exit 1
    }
    Write-Host "  $($req.Name): OK" -ForegroundColor Green
}

# Verify Procmon signature
$sig = Get-AuthenticodeSignature $Procmon -ErrorAction SilentlyContinue
if ($sig.Status -eq "Valid") {
    Write-Host "  Procmon signature: VALID (Microsoft)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Procmon signature status: $($sig.Status)" -ForegroundColor Yellow
}

# Kill stale Procmon
Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  Killing stale Procmon PID=$($_.Id)" -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

Write-Host ""

# ═══════════════════════════════════════════════════════════
# STAGE 1: NOTEPAD CONTROL TEST
# ═══════════════════════════════════════════════════════════

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STAGE 1: NOTEPAD CONTROL TEST" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$controlTs = Get-Date -Format "yyyyMMdd_HHmmss"
$controlDir = "$RuntimeDir\control_$controlTs"
$controlPml = "$controlDir\control.pml"
$controlCsv = "$controlDir\control_full.csv"
$controlCsvPid = "$controlDir\control_pid.csv"

New-Item -ItemType Directory -Path $controlDir -Force | Out-Null

# Start Procmon
Write-Host "`n  Starting Procmon..." -ForegroundColor Yellow
$pm1 = Start-Process -FilePath $Procmon `
    -ArgumentList "/AcceptEula /BackingFile `"$controlPml`" /OnConnection 1" `
    -PassThru
Start-Sleep -Seconds 3

$pmCheck = Get-Process -Id $pm1.Id -ErrorAction SilentlyContinue
if (-not $pmCheck) {
    Write-Host "  FATAL: Procmon exited immediately" -ForegroundColor Red
    exit 1
}
Write-Host "  Procmon PID: $($pm1.Id)" -ForegroundColor Green

# Launch Notepad
Write-Host "  Launching notepad.exe..." -ForegroundColor Yellow
$noteProc = Start-Process -FilePath "notepad.exe" -PassThru
$notePid = $noteProc.Id
Write-Host "  Notepad PID: $notePid" -ForegroundColor Green

# Wait
Start-Sleep -Seconds 2

# Close Notepad
Write-Host "  Closing Notepad..." -ForegroundColor Yellow
Stop-Process -Id $notePid -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Stop Procmon
Write-Host "  Stopping Procmon..." -ForegroundColor Yellow
Stop-Process -Id $pm1.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

# Verify PML
if (-not (Test-Path $controlPml)) {
    Write-Host "  FATAL: Control PML not created" -ForegroundColor Red; exit 1
}
$pmlSize = (Get-Item $controlPml).Length
Write-Host "  PML: $pmlSize bytes" -ForegroundColor Green

# Export CSV
Write-Host "  Exporting CSV..." -ForegroundColor Yellow
$csvExported = $false
try {
    $ep = Start-Process -FilePath $Procmon `
        -ArgumentList "/OpenLog `"$controlPml`" /SaveAs `"$controlCsv`"" `
        -PassThru
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Seconds 5
        if (Test-Path $controlCsv) {
            $csvSize = (Get-Item $controlCsv).Length
            if ($csvSize -gt 100) { $csvExported = $true; break }
        }
    }
    Get-Process -Id $ep.Id -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {}

if (-not $csvExported) {
    # Open GUI for manual save
    Write-Host "  Auto-export failed. Opening Procmon GUI..." -ForegroundColor Yellow
    Start-Process -FilePath $Procmon -ArgumentList "/OpenLog `"$controlPml`""
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Yellow
    Write-Host "  Please save the CSV:" -ForegroundColor Yellow
    Write-Host "  File -> Save As -> Type: CSV" -ForegroundColor White
    Write-Host "  Path: $controlCsv" -ForegroundColor White
    Write-Host "  ========================================" -ForegroundColor Yellow
    Write-Host "  Press Enter after saving..." -ForegroundColor Cyan
    Read-Host
    if (-not (Test-Path $controlCsv)) {
        Write-Host "  FATAL: CSV not found after manual save" -ForegroundColor Red; exit 1
    }
    Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

$controlCsvSha = (Get-FileHash -Path $controlCsv -Algorithm SHA256).Hash
Write-Host "  CSV: $((Get-Item $controlCsv).Length) bytes SHA=$controlCsvSha" -ForegroundColor Green

# Extract Notepad PID
Write-Host "  Extracting Notepad PID $notePid..." -ForegroundColor Yellow
& $Python $Extractor --input $controlCsv --pid $notePid --output $controlCsvPid 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

if (-not (Test-Path $controlCsvPid)) {
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Red
    Write-Host "  CONTROL TEST FAILED" -ForegroundColor Red
    Write-Host "  Notepad PID $notePid was not captured." -ForegroundColor Red
    Write-Host "  PROCMON_CAPTURE_PIPELINE_FAILED" -ForegroundColor Red
    Write-Host "  ============================================" -ForegroundColor Red
    exit 1
}

$controlRows = (Get-Content $controlCsvPid | Measure-Object).Count - 1
Write-Host "  CONTROL TEST PASSED: $controlRows rows for Notepad PID $notePid" -ForegroundColor Green

# Cleanup Procmon
Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host ""

# ═══════════════════════════════════════════════════════════
# STAGE 2: NESYSSERVICE RUN 4 CAPTURE
# ═══════════════════════════════════════════════════════════

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STAGE 2: NESYSSERVICE RUN 4 CAPTURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$run4Ts = Get-Date -Format "yyyyMMdd_HHmmss"
$run4Dir = "$RuntimeDir\run4_$run4Ts"
$run4Pml = "$run4Dir\nesys_run4.pml"
$run4Csv = "$run4Dir\nesys_run4_full.csv"
$run4CsvPid = "$run4Dir\nesys_run4_pid.csv"
$run4Summary = "$run4Dir\nesys_run4_summary.json"
$run4Meta = "$run4Dir\nesys_run4_metadata.json"

New-Item -ItemType Directory -Path $run4Dir -Force | Out-Null

# Record metadata
$gitHead = (git -C $ProjectRoot rev-parse HEAD 2>&1).Trim()
$procmonSha = (Get-FileHash -Path $Procmon -Algorithm SHA256).Hash
$nesysSha = (Get-FileHash -Path $NesysExe -Algorithm SHA256).Hash

@{
    timestamp = $run4Ts
    git_head = $gitHead
    procmon_sha256 = $procmonSha
    nesys_sha256 = $nesysSha
    nesys_path = $NesysExe
    control_test_passed = $true
    control_test_rows = $controlRows
} | ConvertTo-Json -Depth 5 | Out-File -FilePath $run4Meta -Encoding utf8

# Start Procmon
Write-Host "`n  Starting Procmon (no filters)..." -ForegroundColor Yellow
$pm2 = Start-Process -FilePath $Procmon `
    -ArgumentList "/AcceptEula /BackingFile `"$run4Pml`" /OnConnection 1" `
    -PassThru
Start-Sleep -Seconds 3

$pmCheck2 = Get-Process -Id $pm2.Id -ErrorAction SilentlyContinue
if (-not $pmCheck2) {
    Write-Host "  FATAL: Procmon exited immediately" -ForegroundColor Red; exit 1
}
Write-Host "  Procmon PID: $($pm2.Id)" -ForegroundColor Green

# Launch NesysService
Write-Host "  Launching NesysService.exe..." -ForegroundColor Yellow
$nesysDir = [System.IO.Path]::GetDirectoryName($NesysExe)
$nesysProc = Start-Process -FilePath $NesysExe -WorkingDirectory $nesysDir -PassThru
$nesysPid = $nesysProc.Id
Write-Host "  NesysService PID: $nesysPid" -ForegroundColor Green

# Wait for exit
Write-Host "  Waiting for NesysService to exit..." -ForegroundColor Yellow
try {
    $nesysProc.WaitForExit(15000)
    $exitCode = $nesysProc.ExitCode
    Write-Host "  NesysService exited: code $exitCode" -ForegroundColor Yellow
} catch {
    Write-Host "  Timeout. Forcing..." -ForegroundColor Yellow
    Stop-Process -Id $nesysPid -Force -ErrorAction SilentlyContinue
    $exitCode = -999
}

# Post-exit buffer
Write-Host "  Post-exit buffer (3s)..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Stop Procmon
Write-Host "  Stopping Procmon..." -ForegroundColor Yellow
Stop-Process -Id $pm2.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

# Verify PML
if (-not (Test-Path $run4Pml)) {
    Write-Host "  FATAL: Run 4 PML not created" -ForegroundColor Red; exit 1
}
$run4PmlSize = (Get-Item $run4Pml).Length
$run4PmlSha = (Get-FileHash -Path $run4Pml -Algorithm SHA256).Hash
Write-Host "  PML: $run4PmlSize bytes SHA=$run4PmlSha" -ForegroundColor Green

# Export CSV
Write-Host "  Exporting CSV..." -ForegroundColor Yellow
$csvExported2 = $false
try {
    $ep2 = Start-Process -FilePath $Procmon `
        -ArgumentList "/OpenLog `"$run4Pml`" /SaveAs `"$run4Csv`"" `
        -PassThru
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Seconds 5
        if (Test-Path $run4Csv) {
            $csvSize2 = (Get-Item $run4Csv).Length
            if ($csvSize2 -gt 100) { $csvExported2 = $true; break }
        }
    }
    Get-Process -Id $ep2.Id -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {}

if (-not $csvExported2) {
    Write-Host "  Auto-export failed. Opening Procmon GUI..." -ForegroundColor Yellow
    Start-Process -FilePath $Procmon -ArgumentList "/OpenLog `"$run4Pml`""
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Yellow
    Write-Host "  Please save the CSV:" -ForegroundColor Yellow
    Write-Host "  File -> Save As -> Type: CSV" -ForegroundColor White
    Write-Host "  Path: $run4Csv" -ForegroundColor White
    Write-Host "  ========================================" -ForegroundColor Yellow
    Write-Host "  Press Enter after saving..." -ForegroundColor Cyan
    Read-Host
    if (-not (Test-Path $run4Csv)) {
        Write-Host "  FATAL: CSV not found after manual save" -ForegroundColor Red; exit 1
    }
    Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

$run4CsvSha = (Get-FileHash -Path $run4Csv -Algorithm SHA256).Hash
Write-Host "  CSV: $((Get-Item $run4Csv).Length) bytes SHA=$run4CsvSha" -ForegroundColor Green

# Extract NesysService PID
Write-Host "  Extracting NesysService PID $nesysPid..." -ForegroundColor Yellow
$extractResult = & $Python $Extractor --input $run4Csv --pid $nesysPid --output $run4CsvPid --summary $run4Summary 2>&1
Write-Host "  $extractResult" -ForegroundColor Gray

if (-not (Test-Path $run4CsvPid)) {
    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Red
    Write-Host "  NESYSSERVICE NOT CAPTURED" -ForegroundColor Red
    Write-Host "  PID $nesysPid was not found in the capture." -ForegroundColor Red
    Write-Host "  PML: $run4Pml" -ForegroundColor White
    Write-Host "  CSV: $run4Csv" -ForegroundColor White
    Write-Host "  ============================================" -ForegroundColor Red
    exit 1
}

$pidCsvSize = (Get-Item $run4CsvPid).Length
Write-Host "  PID CSV: $pidCsvSize bytes" -ForegroundColor Green

# Verify it's actually NesysService.exe
$firstLine = Get-Content $run4CsvPid -Head 2 | Select-Object -Last 1
if ($firstLine -notmatch "NesysService.exe") {
    Write-Host "  WARNING: First data row does not contain NesysService.exe" -ForegroundColor Yellow
    Write-Host "  $firstLine" -ForegroundColor Gray
}

# ── Final report ─────────────────────────────────────────
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  RUN 4 CAPTURE COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NesysService PID:  $nesysPid" -ForegroundColor White
Write-Host "  Exit code:         $exitCode" -ForegroundColor $(if ($exitCode -ne 0) {'Yellow'} else {'Green'})
Write-Host "  PML:               $run4Pml ($run4PmlSize bytes)" -ForegroundColor White
Write-Host "  PML SHA-256:       $run4PmlSha" -ForegroundColor Gray
Write-Host "  Full CSV:          $run4Csv ($((Get-Item $run4Csv).Length) bytes)" -ForegroundColor White
Write-Host "  Full CSV SHA-256:  $run4CsvSha" -ForegroundColor Gray
Write-Host "  PID CSV:           $run4CsvPid ($pidCsvSize bytes)" -ForegroundColor White
Write-Host "  Summary:           $run4Summary" -ForegroundColor White
Write-Host "  Metadata:          $run4Meta" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Analyse the PID CSV to determine the terminal failure." -ForegroundColor Cyan

# Cleanup
Get-Process -Name "Procmon*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

exit 0
