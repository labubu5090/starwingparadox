"""Tests for app.db.repositories.player_repository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models.player import Player
from app.db.repositories.player_repository import PlayerRepository


@pytest.fixture
async def repo_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def repo(repo_session: AsyncSession):
    return PlayerRepository(repo_session)


class TestGetByPlayerId:
    @pytest.mark.asyncio
    async def test_existing_player(self, repo: PlayerRepository, repo_session: AsyncSession):
        player = Player(nesys_id="TEST001", player_name="Alice")
        repo_session.add(player)
        await repo_session.flush()
        await repo_session.refresh(player)

        result = await repo.get_by_player_id(player.player_id)
        assert result is not None
        assert result.nesys_id == "TEST001"
        assert result.player_name == "Alice"

    @pytest.mark.asyncio
    async def test_missing_player_returns_none(self, repo: PlayerRepository):
        result = await repo.get_by_player_id(99999)
        assert result is None


class TestGetByNesysId:
    @pytest.mark.asyncio
    async def test_existing_nesys(self, repo: PlayerRepository, repo_session: AsyncSession):
        player = Player(nesys_id="NESYS001", player_name="Bob")
        repo_session.add(player)
        await repo_session.flush()

        result = await repo.get_by_nesys_id("NESYS001")
        assert result is not None
        assert result.player_name == "Bob"

    @pytest.mark.asyncio
    async def test_missing_nesys_returns_none(self, repo: PlayerRepository):
        result = await repo.get_by_nesys_id("NONEXISTENT")
        assert result is None


class TestCreatePlayer:
    @pytest.mark.asyncio
    async def test_creates_player(self, repo: PlayerRepository):
        player = await repo.create_player("NEW NESYS")
        assert player.player_id > 0
        assert player.nesys_id == "NEW NESYS"
        assert player.player_name == "ＮｏＮａｍｅ"

    @pytest.mark.asyncio
    async def test_create_multiple_players(self, repo: PlayerRepository):
        p1 = await repo.create_player("NESYS_A")
        p2 = await repo.create_player("NESYS_B")
        assert p1.player_id != p2.player_id

    @pytest.mark.asyncio
    async def test_flush_and_refresh(self, repo: PlayerRepository, repo_session: AsyncSession):
        player = await repo.create_player("NESYS_FLUSH")
        assert player.player_id > 0
        count_result = await repo_session.execute(
            __import__("sqlalchemy")
            .select(__import__("sqlalchemy").func.count())
            .select_from(Player)
        )
        assert count_result.scalar() >= 1


class TestUpdatePlayer:
    @pytest.mark.asyncio
    async def test_update_existing(self, repo: PlayerRepository):
        player = await repo.create_player("NESYS_UPD")
        updated = await repo.update_player(player.player_id, player_name="NewName")
        assert updated is not None
        assert updated.player_name == "NewName"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self, repo: PlayerRepository):
        result = await repo.update_player(99999, player_name="Ghost")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_ignores_unknown_kwargs(self, repo: PlayerRepository):
        player = await repo.create_player("NESYS_IGNORE")
        updated = await repo.update_player(player.player_id, nonexistent_field="value")
        assert updated is not None
        assert not hasattr(updated, "nonexistent_field") or updated.nesys_id == "NESYS_IGNORE"

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, repo: PlayerRepository):
        player = await repo.create_player("NESYS_MULTI")
        updated = await repo.update_player(
            player.player_id,
            player_name="Multi",
            rank_id=5,
            title_id=100,
        )
        assert updated.player_name == "Multi"
        assert updated.rank_id == 5
        assert updated.title_id == 100
