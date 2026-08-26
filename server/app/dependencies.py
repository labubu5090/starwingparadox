"""FastAPI dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings, settings

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None
_override_engine: AsyncEngine | None = None


def set_override_engine(engine: AsyncEngine | None) -> None:
    """Set an override engine for testing."""
    global _override_engine, _engine, _async_session_factory
    _override_engine = engine
    _engine = None
    _async_session_factory = None


def _get_engine() -> AsyncEngine:
    global _engine
    if _override_engine is not None:
        return _override_engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            _get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_factory


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
