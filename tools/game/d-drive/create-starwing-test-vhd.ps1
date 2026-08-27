# create-starwing-test-vhd.ps1 — Creates a test VHDX for D: drive reconstruction
# Safety: $ErrorActionPreference = "Stop", no physical disk operations
$ErrorActionPreference = "Stop"

$VhdPath = "C:\Users\KAHO\Pictures\Starwing\data\starwing-test-d.vhdx"
$SizeBytes = 50MB

# Refuse if VHDX already exists
if (Test-Path $VhdPath) {
    Write-Error "VHDX already exists at $VhdPath. Remove it first or use a different path."
    exit 1
}

# Ensure data directory exists
$dataDir = Split-Path $VhdPath -Parent
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

Write-Host "Creating VHDX: $VhdPath ($SizeBytes bytes)"
New-VHD -Path $VhdPath -SizeBytes $SizeBytes -Dynamic
Write-Host "VHDX created successfully"
Get-Item $VhdPath | Select-Object FullName,Length,LastWriteTime
