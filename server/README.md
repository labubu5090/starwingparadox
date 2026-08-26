# Starwing Paradox Server

Python (FastAPI) server for the Starwing Paradox arcade cabinet game, replacing the legacy JavaScript prototype.

## Current Status

**Phase 1: Python Foundation** — In Progress

| Component | Status |
|-----------|--------|
| FastAPI application | Functional |
| HTTP endpoints | Placeholders returning legacy-compatible JSON |
| Database layer | SQLAlchemy async with PostgreSQL |
| Protobuf codec | In progress |
| TCP server | Not yet implemented |
| Matching engine | Not yet implemented |
| Battle system | Not yet implemented |

> **Warning**: The matching and battle systems are NOT complete. This server currently only handles HTTP endpoints with stub responses. Full matching and battle lifecycle will be implemented in Phases 4-6.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Cabinet (UE4)                   │
│            FMV Mecha Fight Simulator             │
└─────────┬───────────────────────┬───────────────┘
          │ HTTP (port 4001)      │ TCP (port 6666)
          │ POST /matching/server │ Protobuf wire
          │ POST /player/*        │
          │ POST /battle/*        │
          ▼                       ▼
┌─────────────────────────────────────────────────┐
│              Nginx Reverse Proxy                 │
│           (adds x-galaxy-real-ip)                │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│            FastAPI Application                   │
│                                                 │
│  HTTP Routes:                                   │
│    /version, /resource, /health, /ready         │
│    /matching/*, /player/*, /battle/*            │
│    /ranking/*, /mission/*, /credit/*            │
│    /tutorial/*, /game_data/*                    │
│                                                 │
│  TCP Server (Phase 5):                          │
│    Protobuf decode, message routing             │
└─────────┬───────────────────────┬───────────────┘
          │                       │
┌─────────▼───────────┐ ┌────────▼────────────────┐
│   PostgreSQL 16     │ │       Redis 7           │
│  (player data,      │ │  (match queue,          │
│   battle results)   │ │   session cache)        │
└─────────────────────┘ └─────────────────────────┘
```

## Directory Structure

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Settings via env vars
│   ├── dependencies.py       # FastAPI dependency injection
│   ├── logging_config.py     # Structured logging setup
│   ├── api/
│   │   ├── health.py         # GET /health, GET /ready
│   │   ├── version.py        # POST /version
│   │   ├── resource.py       # POST /resource
│   │   ├── player.py         # POST /player/*
│   │   ├── matching.py       # POST /matching/*
│   │   ├── battle.py         # POST /battle/*
│   │   ├── ranking.py        # POST /ranking/*
│   │   ├── mission.py        # POST /mission/*
│   │   ├── credit.py         # POST /credit/*
│   │   ├── tutorial.py       # POST /tutorial/*
│   │   └── game_data.py      # POST /game_data/*
│   ├── db/
│   │   ├── session.py        # Async session factory
│   │   ├── base.py           # SQLAlchemy base
│   │   ├── models/           # ORM models
│   │   └── repositories/     # Data access layer
│   ├── middleware/
│   │   ├── request_id.py     # X-Request-ID middleware
│   │   └── protocol_logging.py
│   └── protocol/
│       ├── __init__.py       # Protobuf codec
│       ├── generated/        # Generated protobuf code
│       └── proto/            # .proto source files
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── unit/                 # Unit tests
│   ├── api/                  # API endpoint tests
│   ├── protocol/             # Protocol codec tests
│   └── fixtures/             # Test data fixtures
├── scripts/
│   ├── inspect_legacy_schema.py  # DB schema inspector
│   └── compare_responses.py      # Legacy response comparator
├── alembic/                  # Database migrations
├── pyproject.toml            # Project config
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── .env.example
└── README.md
```

## Prerequisites

- **Python** 3.12+
- **PostgreSQL** 16
- **Redis** 7
- **uv** (Python package manager) — [Install](https://docs.astral.sh/uv/getting-started/installation/)

## Windows PowerShell Setup

### 1. Install uv

```powershell
# Via pip
pip install uv

# Or via winget
winget install astral-sh.uv
```

### 2. Create virtual environment and install dependencies

```powershell
cd server
uv venv
.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
```

### 3. Environment setup

```powershell
Copy-Item .env.example .env
# Edit .env with your database credentials
```

### 4. PostgreSQL setup

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE paradox;"
psql -U postgres -c "CREATE USER paradox WITH PASSWORD 'changeme';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE paradox TO paradox;"
psql -U paradox -d paradox -f ..\legacy-js\paradox.sql
```

### 5. Protobuf generation

```powershell
cd app\protocol
python -m grpc_tools.protoc -I. --python_out=generated --pyi_out=generated proto\starwingMessage.proto
```

### 6. Local startup

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 4001 --reload
```

### 7. Run tests

```powershell
pytest -v
pytest -v --cov=app --cov-report=term-missing
```

## Docker Startup

```powershell
docker compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI server on port 4001

## Legacy Reference Policy

This project maintains backward compatibility with the legacy JavaScript server:

- **Response format**: All HTTP responses match the legacy JSON structure exactly
- **Wire format**: TCP uses 4-byte LE length prefix + Protobuf, same as legacy
- **Message types**: All existing messageType values are preserved
- **Test data**: Player IDs 10010 and 10011 from legacy schema are supported

The legacy code in `legacy-js/` is reference-only and must NOT be modified.

## Database Backup Warning

**Always back up the database before running migrations:**

```powershell
pg_dump -U paradox paradox > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

## Troubleshooting

### Database connection refused
- Ensure PostgreSQL is running: `Get-Service postgresql*`
- Check credentials in `.env` match PostgreSQL user/password

### Port 4001 already in use
- Find the process: `netstat -ano | findstr :4001`
- Kill it or change `APP_PORT` in `.env`

### Protobuf generation fails
- Ensure `grpcio-tools` is installed: `pip install grpcio-tools`
- Check `.proto` file path is correct

### Tests fail with import errors
- Ensure virtual environment is activated
- Run `uv pip install -e ".[dev]"`

## Current Limitations

1. **No TCP server** — Protobuf TCP handling not yet implemented
2. **No matchmaking** — Matching endpoints return stubs
3. **No battle processing** — Battle results accepted but not processed
4. **No real ranking** — Rankings served from static JSON files
5. **No authentication** — Only IP-based authorization (same as legacy)
6. **No rate limiting** — No request throttling

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Forensic audit | Complete |
| 1 | Python foundation | In Progress |
| 2 | Player identity & profile | Planned |
| 3 | Mission, ranking, resources | Planned |
| 4 | Battle result parity | Planned |
| 5 | Matching engine | Planned |
| 6 | Full battle lifecycle | Planned |
| 7 | Production hardening | Planned |

See `docs/IMPLEMENTATION_PLAN.md` for detailed phase descriptions.
