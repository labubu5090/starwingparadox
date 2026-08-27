# remove-starwing-test-vhd.ps1 — Removes the test VHDX file
# Safety: $ErrorActionPreference = "Stop", requires explicit confirmation
$ErrorActionPreference = "Stop"

$VhdPath = "C:\Users\KAHO\Pictures\Starwing\data\starwing-test-d.vhdx"

# Refuse if D: is still mounted
if (Test-Path "D:\") {
    Write-Error "D: drive is still mounted. Run dismount-starwing-test-vhd.ps1 first."
    exit 1
}

# Refuse if VHDX doesn't exist
if (-not (Test-Path $VhdPath)) {
    Write-Host "VHDX not found at $VhdPath. Nothing to remove."
    exit 0
}

# Confirm removal
Write-Host "VHDX to remove: $VhdPath"
$size = (Get-Item $VhdPath).Length
Write-Host "Size: $([math]::Round($size/1MB,1)) MB"

Remove-Item -Path $VhdPath -Force
Write-Host "VHDX removed successfully"
