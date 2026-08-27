<#
.SYNOPSIS
    Pre-flight checks for game launch.
.DESCRIPTION
    Verifies all prerequisites before launching the game.
.EXAMPLE
    .\preflight-game.ps1
#>

$ErrorActionPreference = "Continue"
$GameRoot = "X:\StarwingParadox"
$ServerRoot = "C:\Users\KAHO\Pictures\Starwing\server"
$checksPassed = 0
$checksFailed = 0
$checksTotal = 0

function Check {
    param([string]$Name, [scriptblock]$Test)
    $script:checksTotal++
    try {
        $result = & $Test
        if ($result) {
            Write-Host "  PASS: $Name" -ForegroundColor Green
            $script:checksPassed++
        } else {
            Write-Host "  FAIL: $Name" -ForegroundColor Red
            $script:checksFailed++
        }
    } catch {
        Write-Host "  FAIL: $Name ($($_.Exception.Message))" -ForegroundColor Red
        $script:checksFailed++
    }
}

Write-Host "=== Game Pre-flight Checks ===" -ForegroundColor Cyan

# Game files
Write-Host "`nGame Files:" -ForegroundColor Yellow
Check "AcrGame.exe exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame.exe" }
Check "AcrGame-Win64-Shipping.exe exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe" }
Check "NesysService.exe exists" { Test-Path "$GameRoot\WindowsNoEditor\NesysService.exe" }
Check "NoHDDUnload.dll exists" { Test-Path "$GameRoot\NoHDDUnload.dll" }
Check "NesysNet.dll exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Binaries\Win64\NesysNet.dll" }

# Config files
Write-Host "`nConfig Files:" -ForegroundColor Yellow
Check "DefaultInput.ini exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Config\DefaultInput.ini" }
Check "GameUserSettings.ini exists" { Test-Path "$GameRoot\D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\GameUserSettings.ini" }
Check "test_mode_setting.json exists" { Test-Path "$GameRoot\D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json" }

# Test mode configs
Write-Host "`nTest Mode:" -ForegroundColor Yellow
Check "tm_main.json exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\tm_main.json" }
Check "tm_network.json exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\tm_network.json" }
Check "tm_device.json exists" { Test-Path "$GameRoot\WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\tm_device.json" }

# Server
Write-Host "`nServer:" -ForegroundColor Yellow
Check "Server directory exists" { Test-Path $ServerRoot }
Check "app/main.py exists" { Test-Path "$ServerRoot\app\main.py" }
Check "app/tcp_server.py exists" { Test-Path "$ServerRoot\app\tcp_server.py" }

# Network
Write-Host "`nNetwork:" -ForegroundColor Yellow
Check "Port 4001 available" { -not (Get-NetTCPConnection -LocalPort 4001 -ErrorAction SilentlyContinue) }
Check "Port 6666 available" { -not (Get-NetTCPConnection -LocalPort 6666 -ErrorAction SilentlyContinue) }

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $checksPassed / $checksTotal" -ForegroundColor $(if ($checksFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host "Failed: $checksFailed / $checksTotal" -ForegroundColor $(if ($checksFailed -eq 0) { "Green" } else { "Red" })

if ($checksFailed -eq 0) {
    Write-Host "`nAll checks passed. Ready to launch." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome checks failed. Review before launching." -ForegroundColor Yellow
    exit 1
}
