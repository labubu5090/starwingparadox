<#
.SYNOPSIS
    Import the legacy paradox.sql schema into the test database.
.DESCRIPTION
    Loads the legacy schema from legacy-js/paradox.sql into starwing_test.
    Validates the target database ends with _test before proceeding.
.PARAMETER Host
    PostgreSQL host (default: localhost)
.PARAMETER SchemaFile
    Path to paradox.sql (default: auto-detected)
#>
param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$User = "starwing_test_user",
    [string]$SchemaFile = ""
)

$ErrorActionPreference = "Stop"

# Load environment if exists
$envFile = Join-Path $PSScriptRoot "environment.ps1"
if (Test-Path $envFile) {
    . $envFile
    if ($Host -eq "localhost" -and $PG_HOST) { $Host = $PG_HOST }
    if ($Port -eq "5432" -and $PG_PORT) { $Port = $PG_PORT }
    if ($User -eq "starwing_test_user" -and $PG_USER) { $User = $PG_USER }
}

$Database = "starwing_test"

# Safety: refuse non-test databases
if ($Database -notmatch "_test$") {
    Write-Error "Refusing to import into non-test database: $Database"
    exit 1
}

# Resolve schema file
if (-not $SchemaFile) {
    $SchemaFile = Join-Path $PSScriptRoot "..\..\legacy-js\paradox.sql"
}
$SchemaFile = Resolve-Path $SchemaFile -ErrorAction SilentlyContinue
if (-not $SchemaFile -or -not (Test-Path $SchemaFile)) {
    Write-Error "Schema file not found: $SchemaFile"
    exit 1
}

Write-Host "Importing legacy schema into '$Database'..." -ForegroundColor Cyan
Write-Host "  Schema: $SchemaFile" -ForegroundColor Gray

# Import
& psql -h $Host -p $Port -U $User -d $Database -f $SchemaFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to import schema into '$Database'"
    exit 1
}

Write-Host "Schema imported successfully." -ForegroundColor Green
exit 0
