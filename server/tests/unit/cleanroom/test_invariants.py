"""Tests for state-machine invariant checker (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.invariants import (
    InvariantCheck,
    InvariantLevel,
    StateMachineInvariantChecker,
)
from app.cleanroom.state import SessionState, SessionStateMachine


class TestInvariantCheck:
    """Test invariant check."""

    def test_check_creation(self):
        check = InvariantCheck(
            name="test",
            passed=True,
            level=InvariantLevel.CONFIRMED,
            details="test details",
        )
        assert check.name == "test"
        assert check.passed is True
        assert check.level == InvariantLevel.CONFIRMED
        assert check.details == "test details"

    def test_check_frozen(self):
        check = InvariantCheck(
            name="test",
            passed=True,
            level=InvariantLevel.CONFIRMED,
        )
        with pytest.raises(AttributeError):
            check.passed = False


class TestStateMachineInvariantChecker:
    """Test state-machine invariant checker."""

    def test_terminal_no_outgoing(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        result = checker.check_terminal_no_outgoing(sm)
        assert result.passed
        assert result.level == InvariantLevel.CONFIRMED

    def test_deterministic_transitions(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        result = checker.check_deterministic_transitions(sm)
        assert result.passed
        assert result.level == InvariantLevel.SYNTHETIC

    def test_transition_history_maintained(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        result = checker.check_transition_history_maintained(sm)
        assert result.passed
        assert result.level == InvariantLevel.CONFIRMED

    def test_fail_always_terminal(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        result = checker.check_fail_always_terminal(sm)
        assert result.passed
        assert result.level == InvariantLevel.CONFIRMED

    def test_reset_clears_history(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        result = checker.check_reset_clears_history(sm)
        assert result.passed
        assert result.level == InvariantLevel.SYNTHETIC

    def test_check_all_invariants(self):
        sm = SessionStateMachine()
        checker = StateMachineInvariantChecker()
        results = checker.check_all_invariants(sm)
        assert len(results) == 5
        assert all(r.passed for r in results)

    def test_invariant_count(self):
        assert len(InvariantLevel) == 3
