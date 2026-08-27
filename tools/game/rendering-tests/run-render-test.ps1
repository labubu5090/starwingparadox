param(
    [Parameter(Mandatory=$true)]
    [string]$TestName,
    [int]$TimeoutSec = 420,
    [switch]$WhatIf,
    [switch]$AuditOnly
)

$ErrorActionPreference = "Stop"
$GameExe = "X:\StarwingParadox\WindowsNoEditor\AcrGame.exe"
$ConfigDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor"
$BackupDir = "$env:LOCALAPPDATA\AcrGame\Saved\Config\WindowsNoEditor\G5_Backup"
$TestProfileDir = "C:\Users\KAHO\Pictures\Starwing\config\rendering-tests"
$LogDir = "C:\Users\KAHO\Pictures\Starwing\docs\generated"
$GameDataDir = "X:\StarwingParadox\WindowsNoEditor"

Write-Host "=== G5 Rendering Test Runner ==="
Write-Host "Test: $TestName"
Write-Host "Timeout: ${TimeoutSec}s"

# Verify game executable hash
$expectedHash = "97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C"
$actualHash = (Get-FileHash $GameExe -Algorithm SHA256).Hash
if ($actualHash -ne $expectedHash) {
    Write-Host "FATAL: Game executable hash mismatch! Expected $expectedHash, got $actualHash"
    exit 1
}
Write-Host "Game hash verified: OK"

# Check no game processes running
$running = Get-Process -Name "AcrGame*","NesysService*" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "FATAL: Game processes already running!"
    exit 1
}

# Backup current config
if (Test-Path $BackupDir) { Remove-Item $BackupDir -Recurse -Force }
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
$engineIni = Join-Path $ConfigDir "Engine.ini"
$gameSettingsIni = Join-Path $ConfigDir "GameUserSettings.ini"
$scalabilityIni = Join-Path $ConfigDir "Scalability.ini"
Copy-Item $engineIni "$BackupDir\Engine.ini.bak" -ErrorAction SilentlyContinue
Copy-Item $gameSettingsIni "$BackupDir\GameUserSettings.ini.bak" -ErrorAction SilentlyContinue
Copy-Item $scalabilityIni "$BackupDir\Scalability.ini.bak" -ErrorAction SilentlyContinue
Write-Host "Config backed up to $BackupDir"

# Load test profile
$profileFile = Join-Path $TestProfileDir "$TestName.ini"
if (-not (Test-Path $profileFile)) {
    Write-Host "FATAL: Profile not found: $profileFile"
    exit 1
}
$profileContent = Get-Content $profileFile -Raw
Write-Host "Profile loaded: $TestName"

if ($WhatIf) {
    Write-Host "[WhatIf] Would apply profile and launch game"
    Write-Host "[WhatIf] Profile content:"
    Write-Host $profileContent
    exit 0
}

if ($AuditOnly) {
    Write-Host "[AuditOnly] Profile content:"
    Write-Host $profileContent
    Write-Host "[AuditOnly] Would apply and launch"
    exit 0
}

# Apply profile - write to Engine.ini
$profileLines = Get-Content $profileFile
$finalContent = @()
$finalContent += "[ConsoleVariables]"
foreach ($line in $profileLines) {
    $trimmed = $line.Trim()
    if ($trimmed -ne "" -and -not $trimmed.StartsWith(";") -and -not $trimmed.StartsWith("[")) {
        $finalContent += $trimmed
    }
}

# Also keep existing Engine.ini content that isn't console variables
$existingEngine = Get-Content $engineIni -ErrorAction SilentlyContinue
if ($existingEngine) {
    $inConsoleSection = $false
    foreach ($line in $existingEngine) {
        if ($line -match "^\[ConsoleVariables\]") { $inConsoleSection = $true; continue }
        if ($line -match "^\[") { $inConsoleSection = $false }
        if (-not $inConsoleSection -and $line.Trim() -ne "") {
            $finalContent = @($line) + $finalContent
        }
    }
}

Set-Content -Path $engineIni -Value ($finalContent -join "`r`n") -Encoding UTF8
Write-Host "Profile applied to $engineIni"

# Record hashes
$iniHash = (Get-FileHash $engineIni -Algorithm SHA256).Hash
Write-Host "Engine.ini hash: $iniHash"

# Clear old log
$logPath = "$env:LOCALAPPDATA\AcrGame\Saved\Logs\AcrGame.log"
if (Test-Path $logPath) {
    $backupLog = "$logPath.pre_g5_$TestName"
    Copy-Item $logPath $backupLog -ErrorAction SilentlyContinue
    Remove-Item $logPath -Force -ErrorAction SilentlyContinue
}

# Launch game
Write-Host "Launching AcrGame.exe..."
$startTime = Get-Date
$proc = Start-Process -FilePath $GameExe -PassThru -WorkingDirectory $GameDataDir
$bootstrapPid = $proc.Id
Write-Host "Bootstrap PID: $bootstrapPid"

# Monitor
$crashDetected = $false
$crashFunction = ""
$titleReached = $false
$stableSec = 0
$preloaded = $false

try {
    while ((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSec {
        Start-Sleep -Seconds 5
        $elapsed = [int]((Get-Date) - $startTime).TotalSeconds

        # Check if game processes are running
        $gameProcs = Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue
        if (-not $gameProcs) {
            Write-Host "  t=${elapsed}s: Game processes exited"
            break
        }

        # Check log for key events
        if (Test-Path $logPath) {
            $logLines = Get-Content $logPath -Tail 200 -ErrorAction SilentlyContinue
            
            # Check for crash
            $crashLine = $logLines | Select-String "EXCEPTION_ACCESS_VIOLATION" | Select-Object -Last 1
            if ($crashLine) {
                $crashDetected = $true
                $crashFunction = ($logLines | Select-String "FRCPassPostProcessAA" | Select-Object -Last 1).Line
                Write-Host "  t=${elapsed}s: CRASH DETECTED - $crashFunction"
                break
            }

            # Check for title screen
            $titleLine = $logLines | Select-String "ActivateLevel.*SL_Title" | Select-Object -Last 1
            if ($titleLine -and -not $titleReached) {
                $titleReached = $true
                Write-Host "  t=${elapsed}s: TITLE SCREEN REACHED"
            }

            # Check for asset preload
            $assetLine = $logLines | Select-String "AssetLoad.*Completed|preload.*done" -CaseSensitive:$false | Select-Object -Last 1
            if ($assetLine -and -not $preloaded) {
                $preloaded = $true
                Write-Host "  t=${elapsed}s: ASSETS PRELOADED"
            }

            # Check for fatal error
            $fatalLine = $logLines | Select-String "Fatal error|Critical error" | Select-Object -Last 1
            if ($fatalLine) {
                Write-Host "  t=${elapsed}s: FATAL ERROR - $($fatalLine.Line)"
                $crashDetected = $true
                break
            }

            # Stable duration tracking
            if ($titleReached -and -not $crashDetected) {
                $stableSec += 5
                if ($stableSec % 30 -eq 0) {
                    Write-Host "  t=${elapsed}s: Stable at title for ${stableSec}s"
                }
            }
        }

        if ($elapsed % 30 -eq 0) {
            $procNames = $gameProcs | ForEach-Object { $_.Name }
            Write-Host "  t=${elapsed}s: processes=[$($procNames -join ', ')]"
        }
    }
} finally {
    # Stop all game processes
    Write-Host "Stopping game processes..."
    Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_.Stop(); Write-Host "  Stopped: $($_.Name) (PID $($_.Id))" } catch {}
    }
    Start-Sleep -Seconds 2
    Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue | ForEach-Object {
        try { $_.Kill() } catch {}
    }

    # Restore config
    Write-Host "Restoring config..."
    if (Test-Path "$BackupDir\Engine.ini.bak") {
        Copy-Item "$BackupDir\Engine.ini.bak" $engineIni -Force
    }
    if (Test-Path "$BackupDir\GameUserSettings.ini.bak") {
        Copy-Item "$BackupDir\GameUserSettings.ini.bak" $gameSettingsIni -Force
    }
    if (Test-Path "$BackupDir\Scalability.ini.bak") {
        Copy-Item "$BackupDir\Scalability.ini.bak" $scalabilityIni -Force
    }
    Write-Host "Config restored"

    # Verify restoration
    $restoredHash = (Get-FileHash $engineIni -Algorithm SHA256).Hash
    $backupHash = if (Test-Path "$BackupDir\Engine.ini.bak") { (Get-FileHash "$BackupDir\Engine.ini.bak" -Algorithm SHA256).Hash } else { "N/A" }
    Write-Host "Restored hash: $restoredHash, Backup hash: $backupHash"
}

# Save results
$result = @{
    test_name = $TestName
    start_time = $startTime.ToString("o")
    end_time = (Get-Date).ToString("o")
    timeout_sec = $TimeoutSec
    bootstrap_pid = $bootstrapPid
    title_reached = $titleReached
    crash_detected = $crashDetected
    crash_function = $crashFunction
    stable_duration_sec = $stableSec
    preloaded = $preloaded
    profile = $profileContent
    ini_hash = $iniHash
    config_restored = $true
}

$resultFile = Join-Path $LogDir "g5_test_${TestName}.json"
$result | ConvertTo-Json -Depth 5 | Set-Content $resultFile -Encoding UTF8
Write-Host "`nResult saved: $resultFile"

# Summary
Write-Host "`n=== RESULT ==="
Write-Host "Title reached: $titleReached"
Write-Host "Crash detected: $crashDetected"
Write-Host "Stable duration: ${stableSec}s"
if ($crashDetected) { Write-Host "Classification: CRASHED" }
elseif ($titleReached -and $stableSec -ge 120) { Write-Host "Classification: STABLE_AT_TITLE" }
elseif ($titleReached) { Write-Host "Classification: UNSTABLE_AT_TITLE" }
else { Write-Host "Classification: DID_NOT_REACH_TITLE" }
