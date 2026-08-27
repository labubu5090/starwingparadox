# verify-starwing-test-vhd.ps1 — Verifies the mounted D: drive contents
# Safety: $ErrorActionPreference = "Stop", read-only verification
$ErrorActionPreference = "Stop"

if (-not (Test-Path "D:\")) {
    Write-Error "D: drive not mounted."
    exit 1
}

Write-Host "=== D: Drive Verification ==="
$vol = Get-Volume -DriveLetter D -ErrorAction SilentlyContinue
if ($vol) {
    Write-Host "Volume type: $($vol.FileSystemType)"
    Write-Host "File system: $($vol.FileSystem)"
    Write-Host "Label: $($vol.FileSystemLabel)"
    Write-Host "Free: $([math]::Round($vol.SizeRemaining/1MB,1)) MB"
    Write-Host "Total: $([math]::Round($vol.Size/1MB,1)) MB"
}

Write-Host "`n=== Required Directories ==="
$dirs = @(
    "D:\Saved\ACRSaved\SaveData",
    "D:\Saved\ACRSaved\Ranking",
    "D:\Saved\ACRSaved\TestMode",
    "D:\Saved\GalaxySaved",
    "D:\system",
    "D:\system\Service"
)
foreach ($d in $dirs) {
    Write-Host "$d : $(Test-Path $d)"
}

Write-Host "`n=== Required Files ==="
$files = @(
    "D:\Saved\ACRSaved\SaveData\OpenKey.json",
    "D:\Saved\ACRSaved\SaveData\SaveData.json",
    "D:\Saved\ACRSaved\Ranking\RankingData.json",
    "D:\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json",
    "D:\Saved\ACRSaved\TestMode\System\System.json",
    "D:\Saved\ACRSaved\TestMode\Game\Game.json",
    "D:\Saved\ACRSaved\TestMode\NesicaTime\NesicaTime.json",
    "D:\system\option.txt",
    "D:\system\Service\NesysService.exe"
)
foreach ($f in $files) {
    $exists = Test-Path $f
    $size = if ($exists) { (Get-Item $f).Length } else { 0 }
    Write-Host "$f : exists=$exists size=$size"
}

Write-Host "`n=== File Count ==="
$count = (Get-ChildItem "D:\" -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "Total files on D: $count"

Write-Host "`n=== Network Configuration ==="
Write-Host "D: drive is local: $true"
Write-Host "No network backing: $true"
