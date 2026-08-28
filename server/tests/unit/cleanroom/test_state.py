"""Tests for session state machine."""
from __future__ import annotations

import pytest

from app.cleanroom.errors import (
    CommandAfterEndError,
    CommandBeforeStartError,
    DuplicateStartError,
    InvalidTransitionError,
)
from app.cleanroom.state import SessionState, SessionStateMachine


class TestStateMachineInitial:
    """Test initial state."""

    def test_initial_state_is_created(self):
        sm = SessionStateMachine()
        assert sm.state == SessionState.CREATED

    def test_initial_history_is_empty(self):
        sm = SessionStateMachine()
        assert sm.transition_history == []


class TestStateMachineTransitions:
    """Test state transitions."""

    def test_open_transport(self):
        sm = SessionStateMachine()
        sm.open_transport()
        assert sm.state == SessionState.TRANSPORT_OPEN

    def test_receive_client_start(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        assert sm.state == SessionState.START_PENDING

    def test_send_start_reply(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        assert sm.state == SessionState.ACTIVE

    def test_receive_client_end(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        sm.receive_client_end()
        assert sm.state == SessionState.END_PENDING

    def test_close(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        sm.receive_client_end()
        sm.close()
        assert sm.state == SessionState.CLOSED

    def test_full_lifecycle(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        sm.receive_client_end()
        sm.close()
        assert sm.state == SessionState.CLOSED
        assert len(sm.transition_history) == 5


class TestStateMachineRejections:
    """Test rejected transitions."""

    def test_duplicate_start(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        with pytest.raises(DuplicateStartError):
            sm.receive_client_start()

    def test_start_before_open(self):
        sm = SessionStateMachine()
        with pytest.raises(CommandBeforeStartError):
            sm.receive_client_start()

    def test_end_before_active(self):
        sm = SessionStateMachine()
        sm.open_transport()
        with pytest.raises(CommandBeforeStartError):
            sm.receive_client_end()

    def test_command_after_close(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.close()
        with pytest.raises(CommandAfterEndError):
            sm.validate_command_allowed()

    def test_invalid_transition(self):
        sm = SessionStateMachine()
        with pytest.raises(InvalidTransitionError):
            sm.transition(SessionState.ACTIVE)

    def test_cannot_transition_from_closed(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.close()
        with pytest.raises(InvalidTransitionError):
            sm.open_transport()

    def test_cannot_transition_from_failed(self):
        sm = SessionStateMachine()
        sm.fail()
        with pytest.raises(InvalidTransitionError):
            sm.open_transport()


class TestStateMachineFail:
    """Test failure state."""

    def test_fail_from_created(self):
        sm = SessionStateMachine()
        sm.fail()
        assert sm.state == SessionState.FAILED

    def test_fail_from_transport_open(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.fail()
        assert sm.state == SessionState.FAILED

    def test_fail_from_active(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        sm.fail()
        assert sm.state == SessionState.FAILED

    def test_fail_from_closed_does_nothing(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.close()
        sm.fail()
        assert sm.state == SessionState.CLOSED

    def test_fail_from_failed_does_nothing(self):
        sm = SessionStateMachine()
        sm.fail()
        sm.fail()
        assert sm.state == SessionState.FAILED


class TestStateMachineTerminal:
    """Test terminal state checks."""

    def test_is_terminal_created(self):
        sm = SessionStateMachine()
        assert sm.is_terminal() is False

    def test_is_terminal_closed(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.close()
        assert sm.is_terminal() is True

    def test_is_terminal_failed(self):
        sm = SessionStateMachine()
        sm.fail()
        assert sm.is_terminal() is True


class TestStateMachineReset:
    """Test reset functionality."""

    def test_reset(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.fail()
        sm.reset()
        assert sm.state == SessionState.CREATED
        assert sm.transition_history == []


class TestStateMachineHistory:
    """Test transition history."""

    def test_history_records_all_transitions(self):
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        history = sm.transition_history
        assert len(history) == 3
        assert history[0] == (SessionState.CREATED, SessionState.TRANSPORT_OPEN)
        assert history[1] == (SessionState.TRANSPORT_OPEN, SessionState.START_PENDING)
        assert history[2] == (SessionState.START_PENDING, SessionState.ACTIVE)

    def test_history_is_copy(self):
        sm = SessionStateMachine()
        sm.open_transport()
        history = sm.transition_history
        history.clear()
        assert len(sm.transition_history) == 1
