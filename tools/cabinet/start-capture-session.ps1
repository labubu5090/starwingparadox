#Requires -Version 5.1
<#
.SYNOPSIS
    Start a controlled capture session for Phase 2A cabinet traffic.
.PARAMETER SessionName
    Required session name. Must be a valid filename component.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SessionName
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$CaptureDir = "$ProjectRoot\data\captures"

# Validate session name
if ($SessionName -match '[\\/:*?"<>|]') {
    Write-Error "Invalid session name: contains invalid filename characters"
    exit 1
}

if ($SessionName.Length -gt 64) {
    Write-Error "Session name too long (max 64 characters)"
    exit 1
}

# Create capture directory
New-Item -ItemType Directory -Force -Path $CaptureDir | Out-Null

# Create session directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sessionDir = "$CaptureDir\${SessionName}_${timestamp}"

if (Test-Path $sessionDir) {
    Write-Error "Session directory already exists: $sessionDir"
    exit 1
}

New-Item -ItemType Directory -Force -Path $sessionDir | Out-Null

# Get Git commit
$gitCommit = git -C $ProjectRoot rev-parse HEAD 2>$null
if (-not $gitCommit) { $gitCommit = "unknown" }

# Get Alembic revision
$dbPath = "$ProjectRoot\data\starwing.db"
$alembicRev = "unknown"
if (Test-Path $dbPath) {
    $alembicRev = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); r=c.execute('SELECT version_num FROM alembic_version').fetchone(); c.close(); print(r[0] if r else 'unknown')" 2>$null
}

# Get database SHA-256
$dbSha = "unknown"
if (Test-Path $dbPath) {
    $dbSha = python -c "import hashlib; h=hashlib.sha256(); f=open(r'$dbPath','rb'); [h.update(d) for d in iter(lambda:f.read(8192),b'')]; print(h.hexdigest())" 2>$null
}

# Write session metadata
$metadata = @{
    session_name = $SessionName
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    git_commit = $gitCommit
    alembic_revision = $alembicRev
    database_sha256 = $dbSha
    capture_enabled_before = ($env:CAPTURE_ENABLED -eq "true")
    matching_enabled = ($env:MATCHER_ENABLED -eq "true")
    battle_enabled = ($env:BATTLE_ENABLED -eq "true")
}

$metadata | ConvertTo-Json | Out-File "$sessionDir\session_metadata.json" -Encoding UTF8

# Create subdirectories
New-Item -ItemType Directory -Force -Path "$sessionDir\http" | Out-Null
New-Item -ItemType Directory -Force -Path "$sessionDir\tcp" | Out-Null
New-Item -ItemType Directory -Force -Path "$sessionDir\raw" | Out-Null

Write-Host "Capture session started: $SessionName" -ForegroundColor Green
Write-Host "Session directory: $sessionDir" -ForegroundColor Cyan
Write-Host "Metadata: $sessionDir\session_metadata.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: Set CAPTURE_ENABLED=true in your .env to activate capture" -ForegroundColor Yellow
Write-Host "      Matching and battle remain disabled." -ForegroundColor Yellow
