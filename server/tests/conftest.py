"""Pytest configuration and shared fixtures."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.dependencies import set_override_engine

# ---------------------------------------------------------------------------
# Settings override for tests
# ---------------------------------------------------------------------------


def get_test_settings() -> Settings:
    return Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        log_level="DEBUG",
    )


# ---------------------------------------------------------------------------
# Synchronous SQLite engine for fixtures
# ---------------------------------------------------------------------------

SYNC_DATABASE_URL = "sqlite:///:memory:"
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine)


# ---------------------------------------------------------------------------
# Async SQLite engine for async tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session using SQLite in-memory."""
    async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session
    await async_engine.dispose()


# ---------------------------------------------------------------------------
# Synchronous DB session fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session() -> Session:
    """Provide a synchronous database session using SQLite in-memory."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI TestClient with test settings."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    set_override_engine(test_engine)
    from app.main import app

    return TestClient(app)


# ---------------------------------------------------------------------------
# Sample test data fixtures
# ---------------------------------------------------------------------------


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
        "match_id": "41772",
        "player_id": "10010",
        "player_name": "TestPlayer",
        "burst_group_id": "0",
        "mode_id": "33",
        "team_id": "0",
        "stage_id": "20001",
        "battle_result": "win",
        "battle_time": "143",
        "play_time": "143",
        "matching_time": "0",
        "left_time": "37",
        "score_2on2": '{"total":13019,"minute":5463,"is_win":true,"diff_rank":0}',
        "players_2on2": '[{"player_id":10010,"player_name":"TestPlayer","team_id":0,"rank_id":1,"total_score":14019,"score_rank":1}]',
        "detail_2on2": '{"player":{"give_damage":{"total":2188,"weapons_2on2":[]}}}',
    }


@pytest.fixture
def sample_version_request() -> dict[str, str]:
    return {}


@pytest.fixture
def sample_matching_server_request() -> dict[str, str]:
    return {}
