"""Tests for observability events."""
from __future__ import annotations

from app.cleanroom.events import Event, EventLog, EventType


class TestEventLogInit:
    """Test event log initialization."""

    def test_initial_count_is_zero(self):
        log = EventLog()
        assert log.count() == 0

    def test_initial_events_is_empty(self):
        log = EventLog()
        assert log.get_events() == []


class TestEventLogRecord:
    """Test event recording."""

    def test_record_event(self):
        log = EventLog()
        event = log.record(EventType.TRANSPORT_OPENED, source="test")
        assert isinstance(event, Event)
        assert event.event_type == EventType.TRANSPORT_OPENED
        assert event.source == "test"
        assert log.count() == 1

    def test_record_with_details(self):
        log = EventLog()
        event = log.record(
            EventType.FRAME_RECEIVED,
            source="test",
            details={"message_type": 0x66},
        )
        assert event.details == {"message_type": 0x66}

    def test_record_multiple_events(self):
        log = EventLog()
        log.record(EventType.TRANSPORT_OPENED, source="a")
        log.record(EventType.FRAME_RECEIVED, source="b")
        log.record(EventType.FRAME_SENT, source="c")
        assert log.count() == 3


class TestEventLogQuery:
    """Test event querying."""

    def test_get_events_by_type(self):
        log = EventLog()
        log.record(EventType.TRANSPORT_OPENED, source="a")
        log.record(EventType.FRAME_RECEIVED, source="b")
        log.record(EventType.TRANSPORT_OPENED, source="c")
        events = log.get_events_by_type(EventType.TRANSPORT_OPENED)
        assert len(events) == 2

    def test_get_events_returns_copy(self):
        log = EventLog()
        log.record(EventType.TRANSPORT_OPENED, source="a")
        events = log.get_events()
        events.clear()
        assert log.count() == 1


class TestEventLogClear:
    """Test event clearing."""

    def test_clear(self):
        log = EventLog()
        log.record(EventType.TRANSPORT_OPENED, source="a")
        log.record(EventType.FRAME_RECEIVED, source="b")
        log.clear()
        assert log.count() == 0


class TestEventType:
    """Test event type enum."""

    def test_all_event_types_exist(self):
        assert EventType.TRANSPORT_OPENED.value == "transport_opened"
        assert EventType.TRANSPORT_CLOSED.value == "transport_closed"
        assert EventType.FRAME_RECEIVED.value == "frame_received"
        assert EventType.FRAME_SENT.value == "frame_sent"
        assert EventType.TRANSITION_ACCEPTED.value == "transition_accepted"
        assert EventType.TRANSITION_REJECTED.value == "transition_rejected"
        assert EventType.UNSUPPORTED_COMMAND.value == "unsupported_command"
        assert EventType.SYNTHETIC_TIMEOUT.value == "synthetic_timeout"
        assert EventType.SYNTHETIC_DISCONNECT.value == "synthetic_disconnect"
        assert EventType.SESSION_FAILED.value == "session_failed"

    def test_event_type_count(self):
        assert len(EventType) == 10
