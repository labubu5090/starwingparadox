"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.db.base import Base
from app.db.models import (  # noqa: F401
    Player,
    PlayerBuddy,
    PlayerBuddyWinPose,
    PlayerEmblem,
    PlayerEmblemPart,
    PlayerLineColor,
    PlayerLogin,
    PlayerMechaColor,
    PlayerMechaSet,
    PlayerMechaSetPart,
    PlayerMission,
    PlayerOption,
    PlayerProgress,
    PlayerSideWeapon,
    PlayerTitle,
    PlayerWeaponSet,
    PlayerWeaponSetSlot,
)
from app.dependencies import set_override_engine


def get_test_settings() -> Settings:
    return Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        log_level="DEBUG",
    )


SYNC_DATABASE_URL = "sqlite:///:memory:"
_sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSessionLocal = sessionmaker(bind=_sync_engine)

# Create tables on the sync engine once for all sync tests
Base.metadata.create_all(_sync_engine)


def _configure_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA busy_timeout = 10000")
    cursor.close()


@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    event.listen(async_engine.sync_engine, "connect", _configure_sqlite_pragmas)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await async_engine.dispose()


@pytest.fixture
def db_session() -> Session:
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient with an in-memory SQLite database."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    event.listen(test_engine.sync_engine, "connect", _configure_sqlite_pragmas)

    loop = asyncio.new_event_loop()

    async def _init():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(_init())

    set_override_engine(test_engine)
    from app.main import app

    return TestClient(app)


@pytest.fixture
def sample_player_id() -> int:
    return 10010


@pytest.fixture
def sample_player_name() -> str:
    return "TestPlayer"


@pytest.fixture
def sample_nesys_id() -> str:
    return "TESTNESYS00001"


@pytest.fixture
def sample_match_id() -> int:
    return 12345


@pytest.fixture
def sample_stage_id() -> int:
    return 20001


@pytest.fixture
def sample_battle_result() -> dict[str, Any]:
    return {
        "result": 1,
        "stage_id": 20001,
        "winner_side": 1,
        "player_score": 1000,
    }


@pytest.fixture
def sample_version_request() -> dict[str, str]:
    return {}


@pytest.fixture
def sample_matching_server_request() -> dict[str, str]:
    return {}
