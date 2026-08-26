"""Tests for app.domain.matching and app.domain.battle state enums."""

from app.domain.battle import BattleState
from app.domain.matching import MatchingState


class TestMatchingStateEnum:
    def test_all_states_exist(self):
        expected = [
            "CREATED",
            "QUEUED",
            "CANDIDATE_FOUND",
            "ROOM_CREATED",
            "WAITING_READY",
            "READY",
            "BATTLE_ASSIGNED",
            "CANCELLED",
            "TIMED_OUT",
            "DISCONNECTED",
            "FAILED",
        ]
        for name in expected:
            assert hasattr(MatchingState, name)

    def test_state_values(self):
        assert MatchingState.CREATED.value == "created"
        assert MatchingState.QUEUED.value == "queued"
        assert MatchingState.BATTLE_ASSIGNED.value == "battle_assigned"

    def test_state_count(self):
        assert len(MatchingState) == 11


class TestBattleStateEnum:
    def test_all_states_exist(self):
        expected = [
            "CREATED",
            "ASSIGNED",
            "WAITING_READY",
            "READY",
            "RUNNING",
            "RESULT_PENDING",
            "COMPLETED",
            "CANCELLED",
            "DISCONNECTED",
            "EXPIRED",
            "FAILED",
        ]
        for name in expected:
            assert hasattr(BattleState, name)

    def test_state_values(self):
        assert BattleState.CREATED.value == "created"
        assert BattleState.RUNNING.value == "running"
        assert BattleState.COMPLETED.value == "completed"

    def test_state_count(self):
        assert len(BattleState) == 11


class TestMatchingStateMembership:
    def test_created_in_set(self):
        assert MatchingState.CREATED in MatchingState

    def test_comparison(self):
        assert MatchingState.CREATED == MatchingState.CREATED
        assert MatchingState.CREATED != MatchingState.QUEUED


class TestBattleStateMembership:
    def test_created_in_set(self):
        assert BattleState.CREATED in BattleState

    def test_comparison(self):
        assert BattleState.RUNNING == BattleState.RUNNING
        assert BattleState.RUNNING != BattleState.COMPLETED
