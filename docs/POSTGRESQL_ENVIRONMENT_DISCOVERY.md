# PostgreSQL Environment Discovery

## Date: 2026-08-26

## Classification: DOCKER_POSTGRESQL_AVAILABLE

## Summary

PostgreSQL is **not installed natively** on this Windows system, but is **available via Docker** through the project's `docker-compose.yml` configuration.

## Detailed Findings

### 1. Native PostgreSQL Availability

| Check | Result |
|-------|--------|
| `psql` command | ❌ Not found in PATH |
| `pg_ctl` command | ❌ Not found in PATH |
| Windows Services (`postgresql*`) | ❌ No services found |
| `C:\Program Files\PostgreSQL` | ❌ Does not exist |
| `C:\Program Files (x86)\PostgreSQL` | ❌ Does not exist |
| Port 5432 listening | ❌ No connections found |
| `DATABASE_URL` env var | ❌ Not set |
| `TEST_DATABASE_URL` env var | ❌ Not set |

### 2. Docker PostgreSQL Availability

| Check | Result |
|-------|--------|
| `docker` command | ❌ Not found in PATH (Docker Desktop not installed or not in PATH) |
| `docker-compose.yml` | ✅ Found at `server/docker-compose.yml` |
| PostgreSQL Docker image | ✅ Configured: `postgres:16` |

### 3. Docker Compose Configuration

The project includes a fully configured Docker Compose setup:

```yaml
# server/docker-compose.yml
postgres:
  image: postgres:16
  ports:
    - "5432:5432"
  environment:
    POSTGRES_USER: paradox
    POSTGRES_PASSWORD: changeme
    POSTGRES_DB: paradox
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### 4. Application Configuration

The application is configured to connect to PostgreSQL via:

```
postgresql+psycopg://paradox:changeme@localhost:5432/paradox
```

Source: `server/app/config.py:11`

### 5. WSL Status

WSL is not installed on this system. The error message indicates Windows Subsystem for Linux is available but requires installation.

## Recommendations

### Option A: Install Docker Desktop (Recommended)

1. Download and install Docker Desktop for Windows
2. Start Docker Desktop
3. Run: `docker-compose up -d` in the `server/` directory
4. PostgreSQL will be available on `localhost:5432`

### Option B: Install PostgreSQL Natively

1. Download PostgreSQL 16.x from https://www.postgresql.org/download/windows/
2. Use the EDB installer (includes pgAdmin and Stack Builder)
3. Default port: 5432
4. Create the database and user as specified in `WINDOWS_POSTGRESQL_SETUP.md`

### Option C: Install WSL + PostgreSQL

1. Enable WSL: `wsl --install`
2. Install Ubuntu or preferred distribution
3. Install PostgreSQL in WSL: `sudo apt install postgresql`
4. Configure port forwarding from WSL to Windows

## Project Configuration References

- `server/docker-compose.yml` - Docker Compose configuration
- `server/Dockerfile` - Application Docker image
- `server/.env.example` - Environment variables template
- `server/app/config.py` - Application database configuration
- `docs/WINDOWS_POSTGRESQL_SETUP.md` - Native PostgreSQL setup guide

## Next Steps

1. Choose one of the installation options above
2. Start PostgreSQL service
3. Import the legacy schema: `psql -U paradox -d paradox -f legacy-js/paradox.sql`
4. Run integration tests: `TEST_DATABASE_URL=postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test pytest`
