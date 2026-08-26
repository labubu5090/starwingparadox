# Windows PostgreSQL Development Setup

## PostgreSQL Version

Recommended: **PostgreSQL 14.x or 15.x** (both fully supported on Windows).

## Installer Source

Download from the official PostgreSQL download page:
- URL: https://www.postgresql.org/download/windows/
- Use the EDB installer which includes pgAdmin and Stack Builder
- Default port: `5432`
- Default superuser: `postgres`

## Service Verification

```powershell
# Check if PostgreSQL is running
pg_isready

# Check the Windows service status
Get-Service postgresql*

# Expected output: Status = Running
```

## psql Verification

```powershell
# Connect to the default database and verify version
psql -U postgres -c "SELECT version();"
```

## Database Creation

```powershell
# Create the development database
createdb starwing_dev
```

## User Creation

```powershell
# Create the dedicated development user
psql -U postgres -c "CREATE USER starwing WITH PASSWORD 'starwing_dev';"
```

## Development Credentials (Safe Examples)

| Field    | Value           |
|----------|-----------------|
| Host     | `localhost`     |
| Port     | `5432`          |
| Database | `starwing_dev`  |
| User     | `starwing`      |
| Password | `starwing_dev`  |

> These credentials are for **local development only**. Never use them in production.

## Importing the Legacy Schema

```powershell
# Import the paradox.sql dump into the development database
psql -U starwing -d starwing_dev -f legacy-js/paradox.sql
```

## Backup Before Migration

```powershell
# Create a full backup before any schema changes
pg_dump starwing_dev > backup.sql
```

## Restore Procedure

```powershell
# Restore from backup
psql -U starwing -d starwing_dev < backup.sql
```

## DATABASE_URL Format

```
postgresql+asyncpg://starwing:starwing_dev@localhost:5432/starwing_dev
```

## Connectivity Test in Python

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test_connection():
    url = "postgresql+asyncpg://starwing:starwing_dev@localhost:5432/starwing_dev"
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                sqlalchemy.text("SELECT 1")
            )
            print("Connection OK:", result.scalar() == 1)
    finally:
        await engine.dispose()

asyncio.run(test_connection())
```

## Test Database for pytest

Create a dedicated test database for the test suite:

```powershell
# Create the test database
psql -U postgres -c "CREATE DATABASE starwing_test OWNER starwing;"
```

Set the environment variable for integration tests:

```powershell
$env:TEST_DATABASE_URL = "postgresql+asyncpg://starwing:starwing_dev@localhost:5432/starwing_test"
```

## Cleanup Procedure

```powershell
# Drop the test database
psql -U postgres -c "DROP DATABASE IF EXISTS starwing_test;"

# Drop the development database
psql -U postgres -c "DROP DATABASE IF EXISTS starwing_dev;"

# Drop the user
psql -U postgres -c "DROP USER IF EXISTS starwing;"
```

---

## SQLite Test Mode

For unit tests that do not depend on PostgreSQL-specific behavior, use SQLite in-memory mode. This runs tests fast without requiring a database server.

### pytest Fixture Configuration

```python
@pytest.fixture
def engine():
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    yield eng
    eng.dispose()
```

### Running Tests

```bash
# Default: runs SQLite in-memory tests only
pytest --tb=short -q

# Integration: runs real PostgreSQL tests (requires running server)
TEST_DATABASE_URL=postgresql+asyncpg://starwing:starwing_dev@localhost:5432/starwing_test pytest
```

---

## Testing Best Practices

### Do Not Claim SQLite Proves PostgreSQL Compatibility

SQLite tests validate application logic and parameter handling. They do **not** prove PostgreSQL compatibility. Integration tests against PostgreSQL are required before any compatibility claim.

### Integration Tests Must Skip With Clear Reason

```python
import os
import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

@pytest.fixture
def requires_postgres():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL not set; skipping PostgreSQL integration test")
```

### Tests Must Use a Dedicated Test Database

Always connect to `starwing_test`, never to `starwing_dev` or production.

### Never Connect to Production Database

```python
import os

def validate_test_database(url: str):
    if not url:
        raise ValueError("TEST_DATABASE_URL is not set")
    if "prod" in url or "production" in url:
        raise ValueError("Refusing to connect to production database")
    if not url.endswith("_test"):
        raise ValueError("Test database URL must end with '_test'")
```

### Validate Database Name Against Explicit Test Suffix

```python
import re

def assert_test_database(url: str):
    assert re.search(r"starwing_test(?:$|\?)", url), (
        f"Database URL does not target starwing_test: {url}"
    )
```

### Run Inside Rollback-Controlled Transactions Where Possible

Wrap integration test database operations in transactions that roll back after each test to keep the database clean:

```python
@pytest.fixture
async def session(engine):
    async with engine.begin() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn)
        yield session
        await trans.rollback()
```
