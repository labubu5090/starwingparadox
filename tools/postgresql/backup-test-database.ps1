<#
.SYNOPSIS
    Backup the test database.
.DESCRIPTION
    Creates a timestamped backup of the test database before destructive operations.
.PARAMETER Host
    PostgreSQL host (default: localhost)
#>
param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$Superuser = "postgres"
)

$ErrorActionPreference = "Stop"

# Load environment if exists
$envFile = Join-Path $PSScriptRoot "environment.ps1"
if (Test-Path $envFile) {
    . $envFile
    if ($Host -eq "localhost" -and $PG_HOST) { $Host = $PG_HOST }
    if ($Port -eq "5432" -and $PG_PORT) { $Port = $PG_PORT }
    if ($Superuser -eq "postgres" -and $PG_SUPERUSER) { $Superuser = $PG_SUPERUSER }
}

$Database = "starwing_test"

# Safety: refuse non-test databases
if ($Database -notmatch "_test$") {
    Write-Error "Refusing to backup non-test database: $Database"
    exit 1
}

# Create backup directory
$backupDir = Join-Path $PSScriptRoot "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "${Database}_${timestamp}.sql"

Write-Host "Backing up '$Database'..." -ForegroundColor Cyan

# Check database exists
$dbExists = & psql -h $Host -p $Port -U $Superuser -d postgres -t -A -c "SELECT 1 FROM pg_database WHERE datname='$Database'" 2>&1
if ($dbExists -ne "1") {
    Write-Warning "Database '$Database' does not exist. Nothing to backup."
    exit 0
}

# Backup
& pg_dump -h $Host -p $Port -U $Superuser -d $Database -f $backupFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to backup '$Database'"
    exit 1
}

$size = (Get-Item $backupFile).Length
Write-Host "  [OK] Backup saved: $backupFile ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
exit 0
