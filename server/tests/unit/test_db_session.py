"""Tests for app.db.session – async session factory and engine creation."""

import contextlib

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory, get_async_session


class TestAsyncSessionFactory:
    def test_factory_creates_async_session(self):
        session = async_session_factory()
        assert isinstance(session, AsyncSession)
        session.close()

    def test_session_expire_on_commit_false(self):
        session = async_session_factory()
        assert session.get_bind().pool is not None
        session.close()


class TestGetAsyncSession:
    @pytest.mark.asyncio
    async def test_yields_session(self):
        gen = get_async_session()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        with contextlib.suppress(StopAsyncIteration):
            await gen.__anext__()

    @pytest.mark.asyncio
    async def test_commits_on_success(self):
        gen = get_async_session()
        session = await gen.__anext__()
        assert session.is_active
        with contextlib.suppress(StopAsyncIteration):
            await gen.__anext__()

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        gen = get_async_session()
        await gen.__anext__()
        with pytest.raises(ValueError):
            await gen.athrow(ValueError, ValueError("test"), None)
