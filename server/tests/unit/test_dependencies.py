"""Tests for app.dependencies – FastAPI dependency injection."""

import contextlib

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import Settings
from app.dependencies import (
    _get_engine,
    _get_session_factory,
    get_db_session,
    get_settings,
    require_header,
    set_override_engine,
)


class TestSetOverrideEngine:
    def test_sets_override(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        set_override_engine(engine)
        from app import dependencies

        assert dependencies._override_engine is engine
        set_override_engine(None)

    def test_clears_cached_engine(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        set_override_engine(engine)
        from app import dependencies

        assert dependencies._engine is None
        assert dependencies._async_session_factory is None
        set_override_engine(None)


class TestGetEngine:
    def test_returns_override(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        set_override_engine(engine)
        try:
            result = _get_engine()
            assert result is engine
        finally:
            set_override_engine(None)

    def test_creates_engine_once(self):
        set_override_engine(None)
        from app import dependencies

        dependencies._engine = None
        e1 = _get_engine()
        e2 = _get_engine()
        assert e1 is e2


class TestGetSessionFactory:
    def test_creates_factory_once(self):
        set_override_engine(None)
        from app import dependencies

        dependencies._async_session_factory = None
        f1 = _get_session_factory()
        f2 = _get_session_factory()
        assert f1 is f2


class TestGetDbSession:
    @pytest.mark.asyncio
    async def test_yields_session(self):
        from sqlalchemy.ext.asyncio import AsyncSession

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        set_override_engine(engine)
        try:
            gen = get_db_session()
            session = await gen.__anext__()
            assert isinstance(session, AsyncSession)
            with contextlib.suppress(StopAsyncIteration):
                await gen.__anext__()
        finally:
            set_override_engine(None)

    @pytest.mark.asyncio
    async def test_session_rolls_back_on_error(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        set_override_engine(engine)
        try:
            gen = get_db_session()
            await gen.__anext__()
            with pytest.raises(RuntimeError):
                await gen.athrow(RuntimeError, RuntimeError("db error"), None)
        finally:
            set_override_engine(None)


class TestGetSettings:
    def test_returns_settings(self):
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.app_port == 4001


class TestRequireHeader:
    @pytest.mark.asyncio
    async def test_valid_header(self):
        result = await require_header(x_galaxy_api_id="valid-id")
        assert result == "valid-id"

    @pytest.mark.asyncio
    async def test_empty_header_raises(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            await require_header(x_galaxy_api_id="")
