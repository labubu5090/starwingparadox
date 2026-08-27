#Requires -Version 5.1
<#
.SYNOPSIS
    Stop the current capture session.
.PARAMETER SessionDir
    Path to the session directory to stop.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionDir
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$dbPath = "$ProjectRoot\data\starwing.db"

if (-not (Test-Path $SessionDir)) {
    Write-Error "Session directory not found: $SessionDir"
    exit 1
}

# Count captured files
$httpFiles = (Get-ChildItem "$SessionDir\http" -File -ErrorAction SilentlyContinue).Count
$tcpFiles = (Get-ChildItem "$SessionDir\tcp" -File -ErrorAction SilentlyContinue).Count
$rawFiles = (Get-ChildItem "$SessionDir\raw" -File -ErrorAction SilentlyContinue).Count

# Get database SHA-256 after session
$dbSha = "unknown"
if (Test-Path $dbPath) {
    $dbSha = python -c "import hashlib; h=hashlib.sha256(); f=open(r'$dbPath','rb'); [h.update(d) for d in iter(lambda:f.read(8192),b'')]; print(h.hexdigest())" 2>$null
}

# Update metadata
$metadataPath = "$SessionDir\session_metadata.json"
if (Test-Path $metadataPath) {
    $metadata = Get-Content $metadataPath | ConvertFrom-Json
    $metadata | Add-Member -NotePropertyName "stopped_at" -NotePropertyValue (Get-Date).ToUniversalTime().ToString("o") -Force
    $metadata | Add-Member -NotePropertyName "database_sha256_after" -NotePropertyValue $dbSha -Force
    $metadata | Add-Member -NotePropertyName "http_captures" -NotePropertyValue $httpFiles -Force
    $metadata | Add-Member -NotePropertyName "tcp_captures" -NotePropertyValue $tcpFiles -Force
    $metadata | Add-Member -NotePropertyName "raw_captures" -NotePropertyValue $rawFiles -Force
    $metadata | ConvertTo-Json | Out-File $metadataPath -Encoding UTF8
}

Write-Host "Capture session stopped" -ForegroundColor Green
Write-Host "Session: $SessionDir" -ForegroundColor Cyan
Write-Host "HTTP captures: $httpFiles" -ForegroundColor Cyan
Write-Host "TCP captures: $tcpFiles" -ForegroundColor Cyan
Write-Host "Raw captures: $rawFiles" -ForegroundColor Cyan
Write-Host "Database SHA-256 (after): $dbSha" -ForegroundColor Cyan
