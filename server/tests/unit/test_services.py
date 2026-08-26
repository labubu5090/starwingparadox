"""Tests for app.services – mission, battle, matching, ranking services."""

import pytest

from app.services.battle_service import BattleService
from app.services.matching_service import MatchingService
from app.services.mission_service import MissionService
from app.services.ranking_service import RankingService


class TestMissionService:
    @pytest.mark.asyncio
    async def test_load_missions(self):
        svc = MissionService()
        result = await svc.load_missions(10010)
        assert result["playerId"] == 10010
        assert result["missions"] == []

    @pytest.mark.asyncio
    async def test_update_mission(self):
        svc = MissionService()
        result = await svc.update_mission(10010, {"mission_id": 1})
        assert result["result"] == 0

    @pytest.mark.asyncio
    async def test_load_missions_different_player(self):
        svc = MissionService()
        result = await svc.load_missions(20020)
        assert result["playerId"] == 20020


class TestBattleService:
    @pytest.mark.asyncio
    async def test_assign_match(self):
        svc = BattleService()
        result = await svc.assign_match({"match": "test"}, game_mode=1)
        assert result["matchId"] == 0
        assert result["result"] == 0

    @pytest.mark.asyncio
    async def test_enter_match(self):
        svc = BattleService()
        result = await svc.enter_match(match_id=100, player_id=200)
        assert result["matchId"] == 100
        assert result["playerId"] == 200
        assert result["result"] == 0

    @pytest.mark.asyncio
    async def test_intrude_match(self):
        svc = BattleService()
        result = await svc.intrude_match(match_id=50, player={"id": 1})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_assign_match_different_modes(self):
        svc = BattleService()
        for mode in [0, 1, 2, 33]:
            result = await svc.assign_match({}, game_mode=mode)
            assert result["result"] == 0


class TestMatchingService:
    @pytest.mark.asyncio
    async def test_entry_matching(self):
        svc = MatchingService()
        result = await svc.entry_matching(10010, {})
        assert result["messageType"] == 201
        assert result["timeout"] == 30

    @pytest.mark.asyncio
    async def test_cancel_matching(self):
        svc = MatchingService()
        result = await svc.cancel_matching(10010, match_id=500)
        assert result["messageType"] == 0xCC
        assert result["matchId"] == 500

    @pytest.mark.asyncio
    async def test_join_matching(self):
        svc = MatchingService()
        result = await svc.join_matching(10010, match_id=500)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_entry_burst_group(self):
        svc = MatchingService()
        result = await svc.entry_burst_group(10010, {})
        assert result["messageType"] == 209
        assert result["burstNumMax"] == 4

    @pytest.mark.asyncio
    async def test_change_burst_group_mode(self):
        svc = MatchingService()
        result = await svc.change_burst_group_mode(10010, {})
        assert result["messageType"] == 211
        assert result["result"] == 0

    @pytest.mark.asyncio
    async def test_update_burst_group(self):
        svc = MatchingService()
        result = await svc.update_burst_group(10010)
        assert result["messageType"] == 215

    @pytest.mark.asyncio
    async def test_burst_group_select(self):
        svc = MatchingService()
        result = await svc.burst_group_select(10010, {})
        assert result["messageType"] == 217
        assert result["timeout"] == 30


class TestRankingService:
    @pytest.mark.asyncio
    async def test_get_rank(self):
        svc = RankingService()
        result = await svc.get_rank(10010)
        assert result["playerId"] == 10010
        assert result["rank"] == 0

    @pytest.mark.asyncio
    async def test_update_rank(self):
        svc = RankingService()
        result = await svc.update_rank(10010, {"result": "win"})
        assert result["result"] == 0

    @pytest.mark.asyncio
    async def test_get_rank_different_player(self):
        svc = RankingService()
        result = await svc.get_rank(20020)
        assert result["playerId"] == 20020
