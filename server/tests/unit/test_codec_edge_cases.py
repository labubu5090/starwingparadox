"""Tests for app.protocol.codec edge cases."""

import struct

import pytest

from app.protocol.codec import (
    FRAME_HEADER_SIZE,
    MAX_MESSAGE_SIZE,
    _compute_digest,
    _read_varint,
    decode_length_prefix,
    decode_request,
    encode_length_prefix,
)
from app.protocol.errors import DecodeError, FramingError, UnknownMessageType


class TestComputeDigest:
    def test_empty_bytes(self):
        result = _compute_digest(b"")
        assert len(result) == 16

    def test_deterministic(self):
        assert _compute_digest(b"hello") == _compute_digest(b"hello")

    def test_different_inputs(self):
        assert _compute_digest(b"a") != _compute_digest(b"b")

    def test_length_16_hex(self):
        result = _compute_digest(b"test")
        assert len(result) == 16
        int(result, 16)


class TestReadVarint:
    def test_single_byte_zero(self):
        val, pos = _read_varint(b"\x00", 0)
        assert val == 0
        assert pos == 1

    def test_single_byte_one(self):
        val, pos = _read_varint(b"\x01", 0)
        assert val == 1
        assert pos == 1

    def test_single_byte_127(self):
        val, pos = _read_varint(b"\x7f", 0)
        assert val == 127
        assert pos == 1

    def test_two_byte_128(self):
        val, pos = _read_varint(b"\x80\x01", 0)
        assert val == 128
        assert pos == 2

    def test_two_byte_300(self):
        val, pos = _read_varint(b"\xac\x02", 0)
        assert val == 300
        assert pos == 2

    def test_offset(self):
        data = b"\x00\x01\x02"
        val, pos = _read_varint(data, 1)
        assert val == 1
        assert pos == 2

    def test_truncated_varint(self):
        with pytest.raises(DecodeError, match="Truncated"):
            _read_varint(b"\x80", 0)

    def test_empty_data(self):
        with pytest.raises(DecodeError, match="Truncated"):
            _read_varint(b"", 0)


class TestDecodeLengthPrefix:
    def test_valid_frame(self):
        payload = b"\x08\x01"
        framed = encode_length_prefix(payload)
        result, remaining = decode_length_prefix(framed)
        assert result == payload
        assert remaining == b""

    def test_empty_payload(self):
        framed = encode_length_prefix(b"")
        result, remaining = decode_length_prefix(framed)
        assert result == b""
        assert remaining == b""

    def test_with_remaining(self):
        payload = b"\x08\x01"
        framed = encode_length_prefix(payload) + b"\xff\xff"
        result, remaining = decode_length_prefix(framed)
        assert result == payload
        assert remaining == b"\xff\xff"

    def test_too_short_for_header(self):
        with pytest.raises(FramingError, match="Need 4 bytes"):
            decode_length_prefix(b"\x01\x00")

    def test_incomplete_frame(self):
        header = struct.pack("<I", 100)
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(header + b"\x01")

    def test_exceeds_max_size(self):
        header = struct.pack("<I", MAX_MESSAGE_SIZE + 1)
        with pytest.raises(FramingError, match="exceeds maximum"):
            decode_length_prefix(header)

    def test_exact_max_size(self):
        header = struct.pack("<I", MAX_MESSAGE_SIZE)
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(header)


class TestEncodeLengthPrefix:
    def test_encode_nonempty(self):
        payload = b"\x08\x01\x10\x03"
        result = encode_length_prefix(payload)
        length = struct.unpack_from("<I", result, 0)[0]
        assert length == len(payload)
        assert result[4:] == payload

    def test_encode_empty(self):
        result = encode_length_prefix(b"")
        assert len(result) == 4
        assert struct.unpack_from("<I", result, 0)[0] == 0

    def test_roundtrip(self):
        for size in [0, 1, 100, 1000]:
            payload = bytes(range(256)) * (size // 256 + 1)
            payload = payload[:size]
            framed = encode_length_prefix(payload)
            decoded, remaining = decode_length_prefix(framed)
            assert decoded == payload
            assert remaining == b""
            assert len(framed) == 4 + size


class TestFrameConstants:
    def test_frame_header_size(self):
        assert FRAME_HEADER_SIZE == 4

    def test_max_message_size(self):
        assert MAX_MESSAGE_SIZE == 1 * 1024 * 1024


class TestDecodeRequestEdgeCases:
    def test_empty_payload_raises(self):
        framed = encode_length_prefix(b"")
        with pytest.raises((DecodeError, UnknownMessageType)):
            decode_request(framed)

    def test_unknown_message_type_raw_mode(self):
        from app.protocol.codec import HAS_GENERATED

        if HAS_GENERATED:
            pytest.skip("Generated protobuf loaded; raw mode not active")
        # Valid protobuf: field 1 (packetId)=1, field 2 (messageType)=0x77 (119)
        # 0x77 is not in MESSAGE_TYPE_MAP, so UnknownMessageType is raised.
        inner = b"\x08\x01\x10\x77"
        framed = encode_length_prefix(inner)
        with pytest.raises(UnknownMessageType):
            decode_request(framed)

    def test_valid_ping_message(self):
        from app.protocol.codec import HAS_GENERATED

        if not HAS_GENERATED:
            pytest.skip("Generated protobuf not available")
        from app.protocol.generated import starwingMessage_pb2 as pb_mod

        msg = pb_mod.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        packet_id, message_type, name, payload = decode_request(framed)
        assert message_type == 0x66
        assert name == "Ping"

    def test_varint_overflow_truncated(self):
        data = b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80"
        with pytest.raises(DecodeError, match="Truncated"):
            _read_varint(data, 0)
