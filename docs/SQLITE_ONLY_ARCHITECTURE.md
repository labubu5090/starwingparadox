# SQLite-Only Architecture

## Overview

The Starwing Paradox server uses SQLite as its only supported database backend. This document describes the architecture, configuration, and operational characteristics.

## Database Configuration

### Default URLs

| Environment | URL |
|-------------|-----|
| Runtime | `sqlite+aiosqlite:///./data/starwing.db` |
| Test | `sqlite+aiosqlite:///:memory:` |

### PRAGMA Configuration

Every SQLite connection is configured with:

```sql
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 10000;
```

Database provisioning additionally sets:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

### Database Location

- Default: `./data/starwing.db` (relative to server directory)
- Backups: `./data/backups/` (timestamped copies)
- Test databases: In-memory (`:memory:`)

## Connection Management

- SQLAlchemy 2.0 async engine with aiosqlite
- AsyncSession with `expire_on_commit=False`
- Connection pool with `pool_pre_ping=True`
- Engine disposal on application shutdown

## Schema Management

- Alembic migrations for schema versioning
- SQLite batch mode for table recreation
- `render_as_batch=True` for ALTER TABLE support

## Backup and Recovery

- SQLite backup API for online backups
- Timestamped backup filenames
- Integrity check after restore
- Pre-migration automatic backup

## Concurrency Model

- **WAL mode**: Enables concurrent reads while writing
- **busy_timeout**: 10 seconds for write contention
- **Single writer**: One server process is the supported default
- **No network shares**: Database must be on local filesystem

## Security

- No network exposure of database
- No superuser privileges required
- Local filesystem permissions only
- No password authentication (file-based access control)

## Limitations

1. **Single writer process**: Multiple independent server processes writing to the same SQLite file are unsupported
2. **No network database**: SQLite must be on local filesystem
3. **No multi-server**: Cannot share database across multiple servers
4. **Concurrent write contention**: Under heavy write load, readers may experience brief delays

## Migration from PostgreSQL

The project migrated from PostgreSQL to SQLite. PostgreSQL tools and documentation are archived in `archive/postgresql/`. See `docs/ADR_001_SQLITE_ONLY.md` for the decision record.
