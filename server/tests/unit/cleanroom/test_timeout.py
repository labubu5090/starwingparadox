"""Tests for deterministic clock and timeout model (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.timeout import (
    DeterministicClock,
    SyntheticTimeoutModel,
    TimeoutEvidenceLevel,
    TimeoutRecord,
)


class TestDeterministicClock:
    """Test deterministic clock."""

    def test_initial_time(self):
        clock = DeterministicClock()
        assert clock.now() == 0.0

    def test_custom_initial_time(self):
        clock = DeterministicClock(initial_time=10.0)
        assert clock.now() == 10.0

    def test_advance(self):
        clock = DeterministicClock()
        clock.advance(5.0)
        assert clock.now() == 5.0

    def test_advance_multiple(self):
        clock = DeterministicClock()
        clock.advance(5.0)
        clock.advance(3.0)
        assert clock.now() == 8.0

    def test_advance_negative_raises(self):
        clock = DeterministicClock()
        with pytest.raises(ValueError):
            clock.advance(-1.0)

    def test_reset(self):
        clock = DeterministicClock()
        clock.advance(10.0)
        clock.reset()
        assert clock.now() == 0.0

    def test_reset_custom_time(self):
        clock = DeterministicClock()
        clock.advance(10.0)
        clock.reset(initial_time=5.0)
        assert clock.now() == 5.0


class TestTimeoutRecord:
    """Test timeout record."""

    def test_record_creation(self):
        record = TimeoutRecord(
            name="TEST_TIMEOUT",
            value_ms=1000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="test source",
            constraints="test constraints",
        )
        assert record.name == "TEST_TIMEOUT"
        assert record.value_ms == 1000
        assert record.evidence_level == TimeoutEvidenceLevel.SYNTHETIC
        assert record.source == "test source"
        assert record.constraints == "test constraints"

    def test_record_frozen(self):
        record = TimeoutRecord(
            name="TEST_TIMEOUT",
            value_ms=1000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="test source",
        )
        with pytest.raises(AttributeError):
            record.value_ms = 2000


class TestSyntheticTimeoutModel:
    """Test synthetic timeout model."""

    def test_default_timeouts(self):
        model = SyntheticTimeoutModel()
        assert model.get_timeout("PING_INTERVAL_MS") == 30000
        assert model.get_timeout("PING_TIMEOUT_MS") == 5000
        assert model.get_timeout("SESSION_TIMEOUT_MS") == 300000
        assert model.get_timeout("ERROR_TIMEOUT_MS") == 1000

    def test_custom_timeout(self):
        model = SyntheticTimeoutModel(
            custom_timeouts={"PING_TIMEOUT_MS": 10000}
        )
        assert model.get_timeout("PING_TIMEOUT_MS") == 10000

    def test_unknown_timeout_raises(self):
        model = SyntheticTimeoutModel()
        with pytest.raises(KeyError):
            model.get_timeout("UNKNOWN_TIMEOUT")

    def test_get_timeout_record(self):
        model = SyntheticTimeoutModel()
        record = model.get_timeout_record("PING_TIMEOUT_MS")
        assert record.name == "PING_TIMEOUT_MS"
        assert record.value_ms == 5000
        assert record.evidence_level == TimeoutEvidenceLevel.SYNTHETIC

    def test_get_all_records(self):
        model = SyntheticTimeoutModel()
        records = model.get_all_records()
        assert len(records) == 4

    def test_start_timer(self):
        clock = DeterministicClock()
        model = SyntheticTimeoutModel(clock=clock)
        model.start_timer("PING_TIMEOUT_MS")
        assert not model.is_expired("PING_TIMEOUT_MS")

    def test_timer_expires(self):
        clock = DeterministicClock()
        model = SyntheticTimeoutModel(clock=clock)
        model.start_timer("PING_TIMEOUT_MS")
        clock.advance(6.0)
        assert model.is_expired("PING_TIMEOUT_MS")

    def test_timer_not_expired(self):
        clock = DeterministicClock()
        model = SyntheticTimeoutModel(clock=clock)
        model.start_timer("PING_TIMEOUT_MS")
        clock.advance(4.0)
        assert not model.is_expired("PING_TIMEOUT_MS")

    def test_unstarted_timer_raises(self):
        model = SyntheticTimeoutModel()
        with pytest.raises(KeyError):
            model.is_expired("PING_TIMEOUT_MS")

    def test_reset_timer(self):
        clock = DeterministicClock()
        model = SyntheticTimeoutModel(clock=clock)
        model.start_timer("PING_TIMEOUT_MS")
        model.reset_timer("PING_TIMEOUT_MS")
        with pytest.raises(KeyError):
            model.is_expired("PING_TIMEOUT_MS")

    def test_clear_all_timers(self):
        clock = DeterministicClock()
        model = SyntheticTimeoutModel(clock=clock)
        model.start_timer("PING_TIMEOUT_MS")
        model.start_timer("SESSION_TIMEOUT_MS")
        model.clear_all_timers()
        with pytest.raises(KeyError):
            model.is_expired("PING_TIMEOUT_MS")
