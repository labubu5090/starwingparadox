<#
.SYNOPSIS
    Create the starwing_test database and starwing_test_user.
.DESCRIPTION
    Creates the test database and a dedicated user with limited permissions.
    Refuses to create databases with production-looking names.
.PARAMETER Host
    PostgreSQL host (default: localhost)
.PARAMETER Superuser
    PostgreSQL superuser for admin operations (default: postgres)
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
$User = "starwing_test_user"
$Password = "starwing_test_pw"

# Safety: refuse production-looking names
$forbiddenNames = @("postgres", "template0", "template1", "paradox")
if ($Database -in $forbiddenNames) {
    Write-Error "Refusing to create forbidden database: $Database"
    exit 1
}
if ($Database -notmatch "_test$") {
    Write-Error "Database name must end with '_test': $Database"
    exit 1
}

Write-Host "Creating test database '$Database' and user '$User'..." -ForegroundColor Cyan

# Check if database already exists
$exists = & psql -h $Host -p $Port -U $Superuser -t -A -c "SELECT 1 FROM pg_database WHERE datname='$Database'" 2>&1
if ($exists -eq "1") {
    Write-Host "  [INFO] Database '$Database' already exists" -ForegroundColor Yellow
} else {
    & psql -h $Host -p $Port -U $Superuser -c "CREATE DATABASE $Database OWNER $Superuser;"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create database '$Database'"
        exit 1
    }
    Write-Host "  [OK] Database '$Database' created" -ForegroundColor Green
}

# Check if user already exists
$userExists = & psql -h $Host -p $Port -U $Superuser -t -A -c "SELECT 1 FROM pg_roles WHERE rolname='$User'" 2>&1
if ($userExists -eq "1") {
    Write-Host "  [INFO] User '$User' already exists" -ForegroundColor Yellow
} else {
    & psql -h $Host -p $Port -U $Superuser -c "CREATE USER $User WITH PASSWORD '$Password';"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create user '$User'"
        exit 1
    }
    Write-Host "  [OK] User '$User' created" -ForegroundColor Green
}

# Grant privileges
& psql -h $Host -p $Port -U $Superuser -c "GRANT ALL PRIVILEGES ON DATABASE $Database TO $User;"
& psql -h $Host -p $Port -U $Superuser -c "ALTER DATABASE $Database OWNER TO $User;"

Write-Host "Test database ready." -ForegroundColor Cyan
Write-Host "  Connection: postgresql+asyncpg://$User`:$Password@$Host`:$Port/$Database"
exit 0
