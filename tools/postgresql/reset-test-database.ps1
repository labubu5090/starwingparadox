<#
.SYNOPSIS
    Destructive reset of the test database.
.DESCRIPTION
    Drops and recreates the test database, then re-imports the legacy schema.
    REQUIRES the -Confirm switch to proceed.
    Creates a backup before destructive operations.
.PARAMETER Host
    PostgreSQL host (default: localhost)
.PARAMETER Confirm
    Must be passed to confirm destructive operation.
#>
param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$Superuser = "postgres",
    [switch]$Confirm
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
    Write-Error "Refusing to reset non-test database: $Database"
    exit 1
}

# Safety: require -Confirm switch
if (-not $Confirm) {
    Write-Error "DESTRUCTIVE OPERATION: Must pass -Confirm switch to reset the test database. Example: .\reset-test-database.ps1 -Confirm"
    exit 1
}

# Safety: refuse forbidden database names
$forbiddenNames = @("postgres", "template0", "template1")
if ($Database -in $forbiddenNames) {
    Write-Error "Refusing to drop forbidden database: $Database"
    exit 1
}

Write-Host "DESTRUCTIVE RESET of '$Database'" -ForegroundColor Red
Write-Host "  This will drop ALL data in the test database." -ForegroundColor Red

# Step 1: Backup
Write-Host "`nStep 1: Creating backup..." -ForegroundColor Cyan
$backupDir = Join-Path $PSScriptRoot "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
}
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "${Database}_reset_${timestamp}.sql"

& pg_dump -h $Host -p $Port -U $Superuser -d $Database -f $backupFile 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Backup saved: $backupFile" -ForegroundColor Green
} else {
    Write-Warning "Backup failed or database is empty. Continuing with reset..."
}

# Step 2: Terminate connections
Write-Host "`nStep 2: Terminating active connections..." -ForegroundColor Cyan
$terminateQuery = @"
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$Database' AND pid <> pg_backend_pid();
"@
& psql -h $Host -p $Port -U $Superuser -d postgres -c $terminateQuery 2>&1 | Out-Null

# Step 3: Drop database
Write-Host "`nStep 3: Dropping database '$Database'..." -ForegroundColor Cyan
& psql -h $Host -p $Port -U $Superuser -d postgres -c "DROP DATABASE IF EXISTS $Database;"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to drop database '$Database'"
    exit 1
}
Write-Host "  [OK] Database dropped" -ForegroundColor Green

# Step 4: Recreate
Write-Host "`nStep 4: Recreating database '$Database'..." -ForegroundColor Cyan
& psql -h $Host -p $Port -U $Superuser -d postgres -c "CREATE DATABASE $Database;"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create database '$Database'"
    exit 1
}

# Grant privileges
$User = "starwing_test_user"
& psql -h $Host -p $Port -U $Superuser -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $Database TO $User;" 2>&1 | Out-Null
& psql -h $Host -p $Port -U $Superuser -d postgres -c "ALTER DATABASE $Database OWNER TO $User;" 2>&1 | Out-Null

Write-Host "  [OK] Database recreated" -ForegroundColor Green

# Step 5: Import schema
Write-Host "`nStep 5: Importing legacy schema..." -ForegroundColor Cyan
$importScript = Join-Path $PSScriptRoot "import-legacy-schema.ps1"
& $importScript -Host $Host -Port $Port
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to import schema"
    exit 1
}

Write-Host "`nReset complete." -ForegroundColor Green
Write-Host "  Database: $Database"
Write-Host "  Backup: $backupFile"
exit 0
