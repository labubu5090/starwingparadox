"""FastAPI dependency injection with SQLite-only database layer."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings, settings

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None
_override_engine: AsyncEngine | None = None


def set_override_engine(engine: AsyncEngine | None) -> None:
    """Set an override engine for testing."""
    global _override_engine, _engine, _async_session_factory
    _override_engine = engine
    _engine = None
    _async_session_factory = None


def _ensure_database_directory(url: str) -> None:
    """Ensure the parent directory of the SQLite database file exists and is writable."""
    from urllib.parse import unquote, urlparse

    parsed = urlparse(url)
    db_path = unquote(parsed.path)
    if not db_path:
        return
    parent = Path(db_path).resolve().parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
            logger.info("Created database directory: %s", parent)
        except OSError as exc:
            logger.critical("Cannot create database directory %s: %s", parent, exc)
            raise SystemExit(f"Cannot create database directory: {parent}") from exc
    if not os.access(parent, os.W_OK):
        logger.critical("Database directory is not writable: %s", parent)
        raise SystemExit(f"Database directory is not writable: {parent}")


def _configure_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
    """Configure SQLite PRAGMAs on every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA busy_timeout = 10000")
    cursor.close()


def _get_engine() -> AsyncEngine:
    global _engine
    if _override_engine is not None:
        return _override_engine
    if _engine is None:
        db_url = settings.get_database_url()
        _ensure_database_directory(db_url)
        _engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        event.listen(_engine.sync_engine, "connect", _configure_sqlite_pragmas)
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_factory


def get_active_engine() -> AsyncEngine:
    """Get the currently active engine (for health checks etc.)."""
    return _get_engine()


def is_memory_database(engine: AsyncEngine) -> bool:
    """Check if the engine is connected to an in-memory database."""
    url_str = str(engine.url)
    return ":memory:" in url_str


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = _get_session_factory()
    async with factory() as session:
        yield session


def get_settings() -> Settings:
    return settings


async def require_header(x_galaxy_api_id: str = Header(...)) -> str:
    if not x_galaxy_api_id:
        raise HTTPException(status_code=400, detail="x-galaxy-api-id header required")
    return x_galaxy_api_id


async def verify_sqlite_pragmas(engine: AsyncEngine) -> dict[str, str]:
    """Verify SQLite PRAGMAs are correctly configured. Used for readiness checks."""
    result: dict[str, str] = {}
    async with engine.connect() as conn:
        for pragma in ("journal_mode", "foreign_keys", "busy_timeout", "synchronous"):
            row = await conn.execute(text(f"PRAGMA {pragma}"))  # noqa: S608
            result[pragma] = str(row.scalar())
        row = await conn.execute(text("PRAGMA integrity_check"))
        result["integrity_check"] = str(row.scalar())
    return result


async def init_database() -> None:
    """Initialize the SQLite database: ensure WAL mode and verify schema."""
    engine = _get_engine()
    if is_memory_database(engine):
        logger.info("In-memory database detected, skipping WAL initialization")
        return
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA journal_mode = WAL"))
        await conn.execute(text("PRAGMA synchronous = NORMAL"))
        await conn.commit()
    logger.info("SQLite database initialized with WAL mode")


async def dispose_database() -> None:
    """Dispose the database engine cleanly on shutdown."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database engine disposed")
