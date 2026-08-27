# Single-Cabinet Deployment Runbook

## Status: SINGLE_CABINET_DEPLOYMENT_CANDIDATE

## Supported Production Model

| Parameter | Value |
|-----------|-------|
| Server processes | 1 |
| Database | 1 local SQLite file |
| Filesystem | Local only |
| Network clients | Multiple TCP/HTTP connections to same process |
| WAL mode | Enabled |
| Backup before migration | Required |
| Shared network database | NOT supported |
| Multiple writer processes | NOT supported |
| Distributed matching state | NOT supported |
| Battle orchestration | NOT supported |

## Prerequisites

- Python 3.10+
- No external database service required
- No Redis required (optional caching)

## Installation

```bash
cd server
pip install -e .
```

## Configuration

Copy `config/single-cabinet.sqlite.example.env` to `.env`:

```bash
cp config/single-cabinet.sqlite.example.env .env
```

Key settings:
- `DATABASE_URL=sqlite+aiosqlite:///./data/starwing.db`
- `APP_PORT=4001`
- `PB_PORT=6666`

## First Run

```bash
# Create database directory
mkdir -p data

# Run Alembic migration
alembic upgrade head

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 4001
```

## Backup

```bash
# Using SQLite backup API (recommended)
python -c "
import sqlite3
src = sqlite3.connect('data/starwing.db')
dst = sqlite3.connect('data/backups/starwing_$(date +%Y%m%d_%H%M%S).db')
src.backup(dst)
dst.close()
src.close()
"
```

## Restore

```bash
# Stop server first
# Then restore
python -c "
import sqlite3
src = sqlite3.connect('backups/starwing_YYYYMMDD_HHMMSS.db')
dst = sqlite3.connect('data/starwing.db')
src.backup(dst)
dst.close()
src.close()
"
# Restart server
```

## Integrity Check

```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/starwing.db')
result = conn.execute('PRAGMA integrity_check').fetchone()
print(f'Integrity: {result[0]}')
conn.close()
"
```

## Monitoring

- `/health` - Basic health check
- `/ready` - Readiness check (verifies schema, WAL, integrity)
- SQLite WAL mode enables concurrent reads during writes
- busy_timeout=10000 prevents SQLITE_BUSY errors

## Limitations

1. Single writer process only
2. No network database access
3. No multi-server support
4. Concurrency limited to WAL mode capabilities
5. Cannot share database across multiple servers
