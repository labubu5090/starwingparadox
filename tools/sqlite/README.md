# SQLite Tools

## Overview

PowerShell scripts for managing the Starwing Paradox SQLite database.

## Tools

### create-database.ps1

Creates a new SQLite database with WAL mode and required PRAGMAs.

```powershell
.\tools\sqlite\create-database.ps1 -Path ".\data\starwing.db"
```

### verify-database.ps1

Verifies database integrity, WAL mode, and required schema.

```powershell
.\tools\sqlite\verify-database.ps1 -Path ".\data\starwing.db"
```

### backup-database.ps1

Creates a timestamped backup of the database.

```powershell
.\tools\sqlite\backup-database.ps1 -Path ".\data\starwing.db" -BackupDir ".\data\backups"
```

### restore-database.ps1

Restores a database from a backup.

```powershell
.\tools\sqlite\restore-database.ps1 -BackupPath ".\data\backups\starwing_20260827_120000.db" -TargetPath ".\data\starwing.db"
```

### integrity-check.ps1

Runs a full integrity check on the database.

```powershell
.\tools\sqlite\integrity-check.ps1 -Path ".\data\starwing.db"
```

### reset-test-database.ps1

Resets a test database (only accepts paths ending in `_test.db`).

```powershell
.\tools\sqlite\reset-test-database.ps1 -Path ".\data\starwing_test.db"
```

## Requirements

- Python 3.10+
- aiosqlite package
- SQLite3 (optional, for direct CLI access)

## Safety

- All tools verify the database path is local
- UNC paths and network shares are rejected
- Test database tools only accept `_test.db` suffix
- Backups are never overwritten
- Integrity checks run after restore
