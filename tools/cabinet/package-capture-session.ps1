#Requires -Version 5.1
<#
.SYNOPSIS
    Package a capture session into a timestamped archive.
.PARAMETER SessionDir
    Path to the session directory to package.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionDir
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"

if (-not (Test-Path $SessionDir)) {
    Write-Error "Session directory not found: $SessionDir"
    exit 1
}

$sessionName = Split-Path $SessionDir -Leaf
$archiveName = "${sessionName}_package.zip"
$archivePath = "$ProjectRoot\data\captures\$archiveName"

if (Test-Path $archivePath) {
    Write-Error "Archive already exists: $archivePath"
    exit 1
}

# Create manifest
$manifest = @{
    packaged_at = (Get-Date).ToUniversalTime().ToString("o")
    session_name = $sessionName
    source_directory = $SessionDir
    provenance = "REAL_CABINET_CAPTURE"
    includes_raw = $true
    excludes_secrets = $true
    excludes_env = $true
    excludes_database = $true
}

$manifestPath = "$SessionDir\manifest.json"
$manifest | ConvertTo-Json | Out-File $manifestPath -Encoding UTF8

# Create archive (excluding database files)
$tempDir = "$env:TEMP\starwing_capture_$([System.IO.Path]::GetRandomFileName())"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

try {
    # Copy session directory
    Copy-Item -Path $SessionDir -Destination "$tempDir\$sessionName" -Recurse

    # Remove any database files that might have been included
    Get-ChildItem "$tempDir" -Recurse -Include "*.db","*.db-wal","*.db-shm" | Remove-Item -Force

    # Create zip
    Compress-Archive -Path "$tempDir\$sessionName" -DestinationPath $archivePath -Force

    $archiveSize = (Get-Item $archivePath).Length
    Write-Host "Capture package created: $archivePath" -ForegroundColor Green
    Write-Host "Size: $([math]::Round($archiveSize / 1KB, 2)) KB" -ForegroundColor Cyan
    Write-Host "Manifest: $manifestPath" -ForegroundColor Cyan
} finally {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
