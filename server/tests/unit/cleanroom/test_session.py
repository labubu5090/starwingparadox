"""Tests for session lifecycle controller."""
from __future__ import annotations

import pytest

from app.cleanroom.events import EventType
from app.cleanroom.session import Session
from app.cleanroom.state import SessionState
from app.cleanroom.synthetic_transport import SyntheticTransport


class TestSessionInit:
    """Test session initialization."""

    def test_initial_state(self):
        transport = SyntheticTransport()
        session = Session(transport)
        assert session.state == SessionState.CREATED

    def test_default_catalog(self):
        transport = SyntheticTransport()
        session = Session(transport)
        assert session._catalog.count() == 28

    def test_default_event_log(self):
        transport = SyntheticTransport()
        session = Session(transport)
        assert session.event_log.count() == 0


class TestSessionOpen:
    """Test session open."""

    @pytest.mark.asyncio
    async def test_open_succeeds(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        assert session.state == SessionState.TRANSPORT_OPEN
        assert transport.is_open() is True

    @pytest.mark.asyncio
    async def test_open_records_event(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        events = session.event_log.get_events_by_type(EventType.TRANSPORT_OPENED)
        assert len(events) == 1


class TestSessionClose:
    """Test session close."""

    @pytest.mark.asyncio
    async def test_close_succeeds(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.close()
        assert session.state == SessionState.FAILED

    @pytest.mark.asyncio
    async def test_close_records_event(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.close()
        events = session.event_log.get_events_by_type(EventType.TRANSPORT_CLOSED)
        assert len(events) >= 1


class TestSessionClientStart:
    """Test client start handling."""

    @pytest.mark.asyncio
    async def test_client_start_succeeds(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.handle_client_start()
        assert session.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_client_start_records_events(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.handle_client_start()
        events = session.event_log.get_events_by_type(EventType.TRANSITION_ACCEPTED)
        assert len(events) == 2


class TestSessionClientEnd:
    """Test client end handling."""

    @pytest.mark.asyncio
    async def test_client_end_succeeds(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.handle_client_start()
        await session.handle_client_end()
        assert session.state == SessionState.CLOSED

    @pytest.mark.asyncio
    async def test_client_end_records_events(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.handle_client_start()
        await session.handle_client_end()
        events = session.event_log.get_events_by_type(EventType.TRANSITION_ACCEPTED)
        assert len(events) >= 3


class TestSessionErrorReporting:
    """Test error reporting methods."""

    @pytest.mark.asyncio
    async def test_cert_error(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.send_cert_error()
        assert session.state == SessionState.FAILED

    @pytest.mark.asyncio
    async def test_nw_error(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.send_nw_error()
        assert session.state == SessionState.FAILED

    @pytest.mark.asyncio
    async def test_nwrecover_notice(self):
        transport = SyntheticTransport()
        session = Session(transport)
        await session.open()
        await session.send_nwrecover_notice()
        # Does not change state
        assert session.state == SessionState.TRANSPORT_OPEN


class TestSessionRunLifecycle:
    """Test full lifecycle execution."""

    @pytest.mark.asyncio
    async def test_empty_lifecycle(self):
        transport = SyntheticTransport()
        session = Session(transport)
        responses = await session.run_lifecycle([])
        assert responses == []
        assert session.state == SessionState.TRANSPORT_OPEN

    @pytest.mark.asyncio
    async def test_lifecycle_with_start_and_end(self):
        """Test PING command through session lifecycle."""
        transport = SyntheticTransport()
        session = Session(transport)

        # Register a simple handler for PING
        async def ping_handler(
            packet_id: int, message_type: int, message_name: str, payload: bytes
        ) -> bytes | None:
            return b"pong"

        session.register_handler(0x66, ping_handler)

        await session.open()
        await session.handle_client_start()
        assert session.state == SessionState.ACTIVE

        # Dispatch PING
        result = await session.process_frame(0x66, 1, "PING", b"")
        assert result == b"pong"

        await session.handle_client_end()
        assert session.state == SessionState.CLOSED
