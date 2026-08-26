"""Tests for app.tcp_server – handler registry, dispatch, and framing."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tcp_server import (
    MAX_FRAME_SIZE,
    _handle_client,
    _handle_ping,
    _handlers,
    handle_message,
    register_handler,
)

# ---------------------------------------------------------------------------
# register_handler
# ---------------------------------------------------------------------------


class TestRegisterHandler:
    def test_stores_handler(self):
        async def dummy(pid, mt, mn, pl):
            return None

        register_handler(999, dummy)
        assert _handlers[999] is dummy
        # cleanup
        del _handlers[999]

    def test_overwrites_existing(self):
        async def h1(pid, mt, mn, pl):
            return b"v1"

        async def h2(pid, mt, mn, pl):
            return b"v2"

        register_handler(998, h1)
        register_handler(998, h2)
        assert _handlers[998] is h2
        del _handlers[998]


# ---------------------------------------------------------------------------
# handle_message (default handler)
# ---------------------------------------------------------------------------


class TestHandleMessage:
    @pytest.mark.asyncio
    async def test_returns_none(self):
        result = await handle_message(1, 0x99, "UnknownType", b"")
        assert result is None


# ---------------------------------------------------------------------------
# Ping handler
# ---------------------------------------------------------------------------


class TestHandlePing:
    @pytest.mark.asyncio
    async def test_returns_framed_payload(self):
        payload = b"\x00\x01\x02"
        result = await _handle_ping(42, 0x66, "Ping", payload)
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) == 4 + len(payload)

    @pytest.mark.asyncio
    async def test_framing_is_4_byte_le(self):
        payload = b"\xaa\xbb"
        result = await _handle_ping(1, 0x66, "Ping", payload)
        import struct

        length = struct.unpack_from("<I", result, 0)[0]
        assert length == 2
        assert result[4:] == payload

    @pytest.mark.asyncio
    async def test_empty_payload(self):
        result = await _handle_ping(1, 0x66, "Ping", b"")
        assert result is not None
        assert len(result) == 4


# ---------------------------------------------------------------------------
# MAX_FRAME_SIZE
# ---------------------------------------------------------------------------


class TestMaxFrameSize:
    def test_is_1_mib(self):
        assert MAX_FRAME_SIZE == 1 * 1024 * 1024


# ---------------------------------------------------------------------------
# Handler dispatch via _handle_client
# ---------------------------------------------------------------------------


class TestHandlerDispatch:
    @pytest.mark.asyncio
    async def test_dispatch_calls_correct_handler(self):
        from app.protocol.generated import starwingMessage_pb2 as pb_mod

        called_with = {}

        async def spy_handler(packet_id, message_type, message_name, payload):
            called_with["packet_id"] = packet_id
            called_with["message_type"] = message_type
            return b"response"

        register_handler(0x77, spy_handler)
        try:
            from app.protocol.codec import encode_length_prefix

            msg = pb_mod.PbMessage()
            msg.packetId = 1
            msg.messageType = 0x77
            msg.Ping.SetInParent()
            inner = msg.SerializeToString()
            framed = encode_length_prefix(inner)

            reader = asyncio.StreamReader()
            reader.feed_data(framed)
            reader.feed_eof()

            writer = MagicMock()
            writer.get_extra_info.return_value = ("127.0.0.1", 12345)
            writer.drain = AsyncMock()
            writer.wait_closed = AsyncMock()

            await _handle_client(reader, writer)

            assert called_with["message_type"] == 0x77
            writer.write.assert_called_once()
            written = writer.write.call_args[0][0]
            assert written == b"response"
        finally:
            del _handlers[0x77]

    @pytest.mark.asyncio
    async def test_unknown_type_gets_default_handler(self):
        from app.protocol.codec import encode_length_prefix

        inner = b"\x08\x01\x10\xff"
        framed = encode_length_prefix(inner)

        reader = asyncio.StreamReader()
        reader.feed_data(framed)
        reader.feed_eof()

        writer = MagicMock()
        writer.get_extra_info.return_value = ("127.0.0.1", 12345)
        writer.drain = AsyncMock()
        writer.wait_closed = AsyncMock()

        await _handle_client(reader, writer)
        writer.write.assert_not_called()

    @pytest.mark.asyncio
    async def test_eof_disconnects(self):
        reader = asyncio.StreamReader()
        reader.feed_eof()

        writer = MagicMock()
        writer.get_extra_info.return_value = ("127.0.0.1", 9999)
        writer.wait_closed = AsyncMock()

        await _handle_client(reader, writer)
        writer.write.assert_not_called()
