"""Unit tests for battle state machine transitions."""

import enum


class BattleState(enum.Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    WAITING_READY = "waiting_ready"
    READY = "ready"
    RUNNING = "running"
    RESULT_PENDING = "result_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    FAILED = "failed"


VALID_TRANSITIONS = {
    BattleState.CREATED: [BattleState.ASSIGNED, BattleState.CANCELLED],
    BattleState.ASSIGNED: [
        BattleState.WAITING_READY,
        BattleState.DISCONNECTED,
    ],
    BattleState.WAITING_READY: [
        BattleState.READY,
        BattleState.TIMED_OUT if hasattr(BattleState, "TIMED_OUT") else BattleState.EXPIRED,
        BattleState.DISCONNECTED,
    ],
    BattleState.READY: [
        BattleState.RUNNING,
        BattleState.CANCELLED,
    ],
    BattleState.RUNNING: [
        BattleState.RESULT_PENDING,
        BattleState.EXPIRED,
        BattleState.DISCONNECTED,
    ],
    BattleState.RESULT_PENDING: [
        BattleState.COMPLETED,
        BattleState.FAILED,
    ],
    BattleState.COMPLETED: [],
    BattleState.CANCELLED: [],
    BattleState.DISCONNECTED: [],
    BattleState.EXPIRED: [],
    BattleState.FAILED: [],
}


def is_valid_transition(from_state: BattleState, to_state: BattleState) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, [])


class TestBattleStateMachine:
    """Test battle state machine transitions."""

    def test_created_to_assigned(self):
        assert is_valid_transition(BattleState.CREATED, BattleState.ASSIGNED)

    def test_created_to_cancelled(self):
        assert is_valid_transition(BattleState.CREATED, BattleState.CANCELLED)

    def test_assigned_to_waiting_ready(self):
        assert is_valid_transition(BattleState.ASSIGNED, BattleState.WAITING_READY)

    def test_assigned_to_disconnected(self):
        assert is_valid_transition(BattleState.ASSIGNED, BattleState.DISCONNECTED)

    def test_waiting_ready_to_ready(self):
        assert is_valid_transition(BattleState.WAITING_READY, BattleState.READY)

    def test_waiting_ready_to_expired(self):
        assert is_valid_transition(BattleState.WAITING_READY, BattleState.EXPIRED)

    def test_waiting_ready_to_disconnected(self):
        assert is_valid_transition(BattleState.WAITING_READY, BattleState.DISCONNECTED)

    def test_ready_to_running(self):
        assert is_valid_transition(BattleState.READY, BattleState.RUNNING)

    def test_ready_to_cancelled(self):
        assert is_valid_transition(BattleState.READY, BattleState.CANCELLED)

    def test_running_to_result_pending(self):
        assert is_valid_transition(BattleState.RUNNING, BattleState.RESULT_PENDING)

    def test_running_to_expired(self):
        assert is_valid_transition(BattleState.RUNNING, BattleState.EXPIRED)

    def test_running_to_disconnected(self):
        assert is_valid_transition(BattleState.RUNNING, BattleState.DISCONNECTED)

    def test_result_pending_to_completed(self):
        assert is_valid_transition(BattleState.RESULT_PENDING, BattleState.COMPLETED)

    def test_result_pending_to_failed(self):
        assert is_valid_transition(BattleState.RESULT_PENDING, BattleState.FAILED)

    def test_terminal_states_no_transitions(self):
        """Terminal states should have no outgoing transitions."""
        for state in [
            BattleState.COMPLETED,
            BattleState.CANCELLED,
            BattleState.DISCONNECTED,
            BattleState.EXPIRED,
            BattleState.FAILED,
        ]:
            assert len(VALID_TRANSITIONS[state]) == 0, f"{state} should be terminal"

    def test_invalid_transitions(self):
        """Invalid transitions should be rejected."""
        invalid = [
            (BattleState.CREATED, BattleState.RUNNING),
            (BattleState.CREATED, BattleState.COMPLETED),
            (BattleState.READY, BattleState.ASSIGNED),
            (BattleState.RUNNING, BattleState.CREATED),
            (BattleState.COMPLETED, BattleState.RUNNING),
        ]
        for from_state, to_state in invalid:
            assert not is_valid_transition(from_state, to_state), (
                f"Transition {from_state} -> {to_state} should be invalid"
            )

    def test_full_happy_path(self):
        """Test the complete happy path: CREATED -> ASSIGNED -> ... -> COMPLETED."""
        happy_path = [
            BattleState.CREATED,
            BattleState.ASSIGNED,
            BattleState.WAITING_READY,
            BattleState.READY,
            BattleState.RUNNING,
            BattleState.RESULT_PENDING,
            BattleState.COMPLETED,
        ]
        for i in range(len(happy_path) - 1):
            assert is_valid_transition(happy_path[i], happy_path[i + 1]), (
                f"Transition {happy_path[i]} -> {happy_path[i + 1]} should be valid"
            )

    def test_cancelled_before_start(self):
        """Battle can be cancelled at early stages."""
        early_cancel = [
            (BattleState.CREATED, BattleState.CANCELLED),
            (BattleState.READY, BattleState.CANCELLED),
        ]
        for from_state, to_state in early_cancel:
            assert is_valid_transition(from_state, to_state)

    def test_disconnect_at_any_active_state(self):
        """Disconnection can happen at most active states."""
        disconnectable = [
            BattleState.ASSIGNED,
            BattleState.WAITING_READY,
            BattleState.RUNNING,
        ]
        for state in disconnectable:
            assert is_valid_transition(state, BattleState.DISCONNECTED), (
                f"{state} should allow disconnection"
            )
