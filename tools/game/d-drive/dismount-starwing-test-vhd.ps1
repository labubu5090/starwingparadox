# dismount-starwing-test-vhd.ps1 — Safely dismounts the test VHDX
# Safety: $ErrorActionPreference = "Stop", confirms D: disappears
$ErrorActionPreference = "Stop"

$VhdPath = "C:\Users\KAHO\Pictures\Starwing\data\starwing-test-d.vhdx"

# Stop any game processes using D:
$gameProcs = Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue
if ($gameProcs) {
    Write-Host "Stopping game processes..."
    $gameProcs | ForEach-Object { try { $_.Kill() } catch {} }
    Start-Sleep -Seconds 2
}

# Stop NesysService if running
$nesysProcs = Get-Process -Name "NesysService*" -ErrorAction SilentlyContinue
if ($nesysProcs) {
    Write-Host "Stopping NesysService processes..."
    $nesysProcs | ForEach-Object { try { $_.Kill() } catch {} }
    Start-Sleep -Seconds 2
}

# Dismount VHDX
if (Test-Path "D:\") {
    Write-Host "Dismounting VHDX..."
    Dismount-VHD -Path $VhdPath -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Verify D: is gone
if (Test-Path "D:\") {
    Write-Warning "D: still exists after dismount"
} else {
    Write-Host "D: drive successfully dismounted"
}

# Show VHDX status
if (Test-Path $VhdPath) {
    Write-Host "`nVHDX file still exists at: $VhdPath"
    Get-VHD -Path $VhdPath -ErrorAction SilentlyContinue | Select-Object VhdType, Attached, FileSize, Size | Format-Table -AutoSize
}
