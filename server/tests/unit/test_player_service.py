"""Tests for app.services.player_service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models.player import Player
from app.services.player_service import PlayerService


@pytest.fixture
async def service_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def service(service_session: AsyncSession):
    return PlayerService(service_session)


class TestLoadProfileByNesys:
    @pytest.mark.asyncio
    async def test_existing_player(self, service: PlayerService, service_session: AsyncSession):
        player = Player(nesys_id="NESYS SVC 1", player_name="SvcPlayer", rank_id=5)
        service_session.add(player)
        await service_session.flush()

        profile = await service.load_profile_by_nesys("NESYS SVC 1")
        assert profile["playerId"] > 0
        assert profile["nesysId"] == "NESYS SVC 1"
        assert profile["playerName"] == "SvcPlayer"
        assert profile["playerRank"] == 5

    @pytest.mark.asyncio
    async def test_missing_returns_empty(self, service: PlayerService):
        result = await service.load_profile_by_nesys("MISSING")
        assert result == {}


class TestLoginPlayer:
    @pytest.mark.asyncio
    async def test_login_existing(self, service: PlayerService, service_session: AsyncSession):
        player = Player(nesys_id="NESYS LOGIN", player_name="LoginPlayer")
        service_session.add(player)
        await service_session.flush()
        await service_session.refresh(player)

        result = await service.login_player(player.player_id, "127.0.0.1", {})
        assert result["result"] == 0
        assert result["playerId"] == player.player_id

    @pytest.mark.asyncio
    async def test_login_missing_player(self, service: PlayerService):
        result = await service.login_player(99999, "127.0.0.1", {})
        assert result["result"] == 1
        assert "not found" in result["message"].lower()


class TestRegisterPlayer:
    @pytest.mark.asyncio
    async def test_register_new(self, service: PlayerService):
        result = await service.register_player(50001, {"nesysId": "NEW NESYS REG"})
        assert result["result"] == 0
        assert "registered" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate(self, service: PlayerService, service_session: AsyncSession):
        player = Player(nesys_id="NESYS DUP", player_name="Dup")
        service_session.add(player)
        await service_session.flush()
        await service_session.refresh(player)

        result = await service.register_player(player.player_id, {"nesysId": "NESYS DUP"})
        assert result["result"] == 1
        assert "already exists" in result["message"].lower()


class TestLoadGameData:
    @pytest.mark.asyncio
    async def test_load_existing(self, service: PlayerService, service_session: AsyncSession):
        player = Player(nesys_id="NESYS GD")
        service_session.add(player)
        await service_session.flush()
        await service_session.refresh(player)

        data = await service.load_game_data(player.player_id)
        assert data["playerId"] == player.player_id

    @pytest.mark.asyncio
    async def test_load_missing(self, service: PlayerService):
        data = await service.load_game_data(99999)
        assert data == {}


class TestLoadGameDataMissions:
    @pytest.mark.asyncio
    async def test_load_missions_existing(
        self, service: PlayerService, service_session: AsyncSession
    ):
        player = Player(nesys_id="NESYS MISSION")
        service_session.add(player)
        await service_session.flush()
        await service_session.refresh(player)

        data = await service.load_game_data_missions(player.player_id)
        assert data["playerId"] == player.player_id

    @pytest.mark.asyncio
    async def test_load_missions_missing(self, service: PlayerService):
        data = await service.load_game_data_missions(99999)
        assert data == {}


class TestSaveGameData:
    @pytest.mark.asyncio
    async def test_save_existing(self, service: PlayerService, service_session: AsyncSession):
        player = Player(nesys_id="NESYS SAVE")
        service_session.add(player)
        await service_session.flush()
        await service_session.refresh(player)

        result = await service.save_game_data(player.player_id, {"data": "test"})
        assert result["result"] == 0
        assert "saved" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_save_missing(self, service: PlayerService):
        result = await service.save_game_data(99999, {})
        assert result["result"] == 1
        assert "not found" in result["message"].lower()
