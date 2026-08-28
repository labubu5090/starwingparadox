"""Tests for synthetic transport."""
from __future__ import annotations

import pytest

from app.cleanroom.errors import TransportClosedError, TransportStateError, TransportTimeoutError
from app.cleanroom.synthetic_transport import SyntheticTransport


class TestSyntheticTransportInitial:
    """Test initial state of synthetic transport."""

    def test_initial_state_is_closed(self):
        transport = SyntheticTransport()
        assert transport.is_open() is False

    def test_initial_sent_count_is_zero(self):
        transport = SyntheticTransport()
        assert transport.sent_count() == 0

    def test_initial_sent_list_is_empty(self):
        transport = SyntheticTransport()
        assert transport.get_sent() == []


class TestSyntheticTransportOpen:
    """Test opening synthetic transport."""

    @pytest.mark.asyncio
    async def test_open_succeeds(self):
        transport = SyntheticTransport()
        await transport.open()
        assert transport.is_open() is True

    @pytest.mark.asyncio
    async def test_double_open_raises(self):
        transport = SyntheticTransport()
        await transport.open()
        with pytest.raises(TransportStateError):
            await transport.open()


class TestSyntheticTransportClose:
    """Test closing synthetic transport."""

    @pytest.mark.asyncio
    async def test_close_succeeds(self):
        transport = SyntheticTransport()
        await transport.open()
        await transport.close()
        assert transport.is_open() is False

    @pytest.mark.asyncio
    async def test_double_close_succeeds(self):
        transport = SyntheticTransport()
        await transport.open()
        await transport.close()
        await transport.close()
        assert transport.is_open() is False

    @pytest.mark.asyncio
    async def test_close_without_open_succeeds(self):
        transport = SyntheticTransport()
        await transport.close()
        assert transport.is_open() is False


class TestSyntheticTransportSend:
    """Test sending through synthetic transport."""

    @pytest.mark.asyncio
    async def test_send_when_open_succeeds(self):
        transport = SyntheticTransport()
        await transport.open()
        await transport.send(b"test data")
        assert transport.sent_count() == 1
        assert transport.get_sent() == [b"test data"]

    @pytest.mark.asyncio
    async def test_send_when_closed_raises(self):
        transport = SyntheticTransport()
        with pytest.raises(TransportClosedError):
            await transport.send(b"test data")

    @pytest.mark.asyncio
    async def test_send_multiple_frames(self):
        transport = SyntheticTransport()
        await transport.open()
        await transport.send(b"frame1")
        await transport.send(b"frame2")
        await transport.send(b"frame3")
        assert transport.sent_count() == 3
        assert transport.get_sent() == [b"frame1", b"frame2", b"frame3"]


class TestSyntheticTransportReceive:
    """Test receiving through synthetic transport."""

    @pytest.mark.asyncio
    async def test_receive_injected_data(self):
        transport = SyntheticTransport()
        await transport.open()
        transport.inject(b"test data")
        data = await transport.receive()
        assert data == b"test data"

    @pytest.mark.asyncio
    async def test_receive_when_closed_raises(self):
        transport = SyntheticTransport()
        with pytest.raises(TransportClosedError):
            await transport.receive()

    @pytest.mark.asyncio
    async def test_receive_timeout(self):
        transport = SyntheticTransport(timeout=0.1)
        await transport.open()
        with pytest.raises(TransportTimeoutError):
            await transport.receive()

    @pytest.mark.asyncio
    async def test_receive_disconnect(self):
        transport = SyntheticTransport()
        await transport.open()
        transport.inject_disconnect()
        with pytest.raises(TransportClosedError):
            await transport.receive()

    @pytest.mark.asyncio
    async def test_receive_preserves_order(self):
        transport = SyntheticTransport()
        await transport.open()
        transport.inject(b"first")
        transport.inject(b"second")
        transport.inject(b"third")
        assert await transport.receive() == b"first"
        assert await transport.receive() == b"second"
        assert await transport.receive() == b"third"


class TestSyntheticTransportClear:
    """Test clearing sent data."""

    @pytest.mark.asyncio
    async def test_clear_sent(self):
        transport = SyntheticTransport()
        await transport.open()
        await transport.send(b"data1")
        await transport.send(b"data2")
        transport.clear_sent()
        assert transport.sent_count() == 0
        assert transport.get_sent() == []


class TestSyntheticTransportMaxFrameSize:
    """Test maximum frame size enforcement."""

    @pytest.mark.asyncio
    async def test_receive_oversized_frame(self):
        transport = SyntheticTransport(max_frame_size=10)
        await transport.open()
        transport.inject(b"x" * 11)
        with pytest.raises(TransportStateError):
            await transport.receive()

    @pytest.mark.asyncio
    async def test_receive_frame_at_max_size(self):
        transport = SyntheticTransport(max_frame_size=10)
        await transport.open()
        transport.inject(b"x" * 10)
        data = await transport.receive()
        assert data == b"x" * 10
