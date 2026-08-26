"""Unit tests for matching state machine transitions."""

import enum


class MatchingState(enum.Enum):
    CREATED = "created"
    QUEUED = "queued"
    CANDIDATE_FOUND = "candidate_found"
    ROOM_CREATED = "room_created"
    WAITING_READY = "waiting_ready"
    READY = "ready"
    BATTLE_ASSIGNED = "battle_assigned"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


VALID_TRANSITIONS = {
    MatchingState.CREATED: [MatchingState.QUEUED, MatchingState.CANCELLED],
    MatchingState.QUEUED: [
        MatchingState.CANDIDATE_FOUND,
        MatchingState.TIMED_OUT,
        MatchingState.CANCELLED,
        MatchingState.DISCONNECTED,
    ],
    MatchingState.CANDIDATE_FOUND: [
        MatchingState.ROOM_CREATED,
        MatchingState.DISCONNECTED,
        MatchingState.FAILED,
    ],
    MatchingState.ROOM_CREATED: [
        MatchingState.WAITING_READY,
        MatchingState.FAILED,
    ],
    MatchingState.WAITING_READY: [
        MatchingState.READY,
        MatchingState.TIMED_OUT,
        MatchingState.DISCONNECTED,
        MatchingState.CANCELLED,
    ],
    MatchingState.READY: [
        MatchingState.BATTLE_ASSIGNED,
        MatchingState.DISCONNECTED,
    ],
    MatchingState.BATTLE_ASSIGNED: [
        MatchingState.COMPLETED if hasattr(MatchingState, "COMPLETED") else None,
        MatchingState.DISCONNECTED,
    ],
    MatchingState.CANCELLED: [],
    MatchingState.TIMED_OUT: [],
    MatchingState.DISCONNECTED: [],
    MatchingState.FAILED: [],
}


def is_valid_transition(from_state: MatchingState, to_state: MatchingState) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, [])


class TestMatchingStateMachine:
    """Test matching state machine transitions."""

    def test_created_to_queued(self):
        assert is_valid_transition(MatchingState.CREATED, MatchingState.QUEUED)

    def test_created_to_cancelled(self):
        assert is_valid_transition(MatchingState.CREATED, MatchingState.CANCELLED)

    def test_queued_to_candidate_found(self):
        assert is_valid_transition(MatchingState.QUEUED, MatchingState.CANDIDATE_FOUND)

    def test_queued_to_timed_out(self):
        assert is_valid_transition(MatchingState.QUEUED, MatchingState.TIMED_OUT)

    def test_queued_to_cancelled(self):
        assert is_valid_transition(MatchingState.QUEUED, MatchingState.CANCELLED)

    def test_queued_to_disconnected(self):
        assert is_valid_transition(MatchingState.QUEUED, MatchingState.DISCONNECTED)

    def test_candidate_found_to_room_created(self):
        assert is_valid_transition(MatchingState.CANDIDATE_FOUND, MatchingState.ROOM_CREATED)

    def test_candidate_found_to_disconnected(self):
        assert is_valid_transition(MatchingState.CANDIDATE_FOUND, MatchingState.DISCONNECTED)

    def test_candidate_found_to_failed(self):
        assert is_valid_transition(MatchingState.CANDIDATE_FOUND, MatchingState.FAILED)

    def test_room_created_to_waiting_ready(self):
        assert is_valid_transition(MatchingState.ROOM_CREATED, MatchingState.WAITING_READY)

    def test_room_created_to_failed(self):
        assert is_valid_transition(MatchingState.ROOM_CREATED, MatchingState.FAILED)

    def test_waiting_ready_to_ready(self):
        assert is_valid_transition(MatchingState.WAITING_READY, MatchingState.READY)

    def test_waiting_ready_to_timed_out(self):
        assert is_valid_transition(MatchingState.WAITING_READY, MatchingState.TIMED_OUT)

    def test_waiting_ready_to_disconnected(self):
        assert is_valid_transition(MatchingState.WAITING_READY, MatchingState.DISCONNECTED)

    def test_waiting_ready_to_cancelled(self):
        assert is_valid_transition(MatchingState.WAITING_READY, MatchingState.CANCELLED)

    def test_ready_to_battle_assigned(self):
        assert is_valid_transition(MatchingState.READY, MatchingState.BATTLE_ASSIGNED)

    def test_ready_to_disconnected(self):
        assert is_valid_transition(MatchingState.READY, MatchingState.DISCONNECTED)

    def test_battle_assigned_to_disconnected(self):
        assert is_valid_transition(MatchingState.BATTLE_ASSIGNED, MatchingState.DISCONNECTED)

    def test_terminal_states_no_transitions(self):
        """Terminal states should have no outgoing transitions."""
        for state in [
            MatchingState.CANCELLED,
            MatchingState.TIMED_OUT,
            MatchingState.DISCONNECTED,
            MatchingState.FAILED,
        ]:
            assert len(VALID_TRANSITIONS[state]) == 0, f"{state} should be terminal"

    def test_invalid_transitions(self):
        """Invalid transitions should be rejected."""
        invalid = [
            (MatchingState.CREATED, MatchingState.READY),
            (MatchingState.CREATED, MatchingState.BATTLE_ASSIGNED),
            (MatchingState.QUEUED, MatchingState.READY),
            (MatchingState.QUEUED, MatchingState.BATTLE_ASSIGNED),
            (MatchingState.CANCELLED, MatchingState.QUEUED),
            (MatchingState.FAILED, MatchingState.CREATED),
        ]
        for from_state, to_state in invalid:
            assert not is_valid_transition(from_state, to_state), (
                f"Transition {from_state} -> {to_state} should be invalid"
            )

    def test_full_happy_path(self):
        """Test the complete happy path: CREATED -> QUEUED -> ... -> BATTLE_ASSIGNED."""
        happy_path = [
            MatchingState.CREATED,
            MatchingState.QUEUED,
            MatchingState.CANDIDATE_FOUND,
            MatchingState.ROOM_CREATED,
            MatchingState.WAITING_READY,
            MatchingState.READY,
            MatchingState.BATTLE_ASSIGNED,
        ]
        for i in range(len(happy_path) - 1):
            assert is_valid_transition(happy_path[i], happy_path[i + 1]), (
                f"Transition {happy_path[i]} -> {happy_path[i + 1]} should be valid"
            )
