# mount-starwing-test-vhd.ps1 — Mounts the test VHDX as D:
# Safety: $ErrorActionPreference = "Stop", refuses if D: already exists
$ErrorActionPreference = "Stop"

$VhdPath = "C:\Users\KAHO\Pictures\Starwing\data\starwing-test-d.vhdx"

# Refuse if VHDX doesn't exist
if (-not (Test-Path $VhdPath)) {
    Write-Error "VHDX not found at $VhdPath. Run create-starwing-test-vhd.ps1 first."
    exit 1
}

# Refuse if D: already exists
if (Test-Path "D:\") {
    Write-Error "D: drive already exists. Cannot mount VHDX as D:."
    exit 1
}

Write-Host "Mounting VHDX as D:..."
$disk = Mount-VHD -Path $VhdPath -PassThru

# Initialize and format if needed
$diskNumber = $disk.Number
$partitions = Get-Partition -DiskNumber $diskNumber -ErrorAction SilentlyContinue
if (-not $partitions) {
    Write-Host "Initializing disk $diskNumber..."
    Initialize-Disk -Number $diskNumber -PartitionStyle MBR
    $partition = New-Partition -DiskNumber $diskNumber -UseMaximumSize -AssignDriveLetter -IsActive
    Format-Volume -Partition $partition -FileSystem NTFS -Force -Confirm:$false
} else {
    # Just assign drive letter D if not already assigned
    $part = $partitions | Select-Object -First 1
    if ($part.DriveLetter -ne 'D') {
        Set-Partition -DiskNumber $diskNumber -PartitionNumber $part.PartitionNumber -DriveLetter 'D'
    }
}

# Verify D: exists
if (Test-Path "D:\") {
    Write-Host "D: drive mounted successfully"
    Get-PSDrive -Name D | Select-Object Name,Root,Free,Used | Format-Table -AutoSize
} else {
    Write-Error "Failed to mount D: drive"
    exit 1
}
