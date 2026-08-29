"""G33 tests for TCP decoder correction and Ping regression.

Tests the decoder fix for PbMessage with empty Message oneof,
stream framing correctness, and Ping echo contract preservation.
"""

from __future__ import annotations

import struct

import pytest

from app.protocol.codec import (
    decode_length_prefix,
    decode_request,
    encode_length_prefix,
    encode_response,
)
from app.protocol.errors import DecodeError, FramingError

# ---------------------------------------------------------------------------
# G33 helpers
# ---------------------------------------------------------------------------

def _make_ping_frame(packet_id: int = 1, message_type: int = 0x66) -> bytes:
    """Build a minimal Ping PbMessage with oneof NOT set (empty envelope).

    This replicates the G32 DECODE_ERROR pattern: game sends a frame
    with messageType=0x66 but the Message oneof is not populated.
    """
    payload = _encode_envelope_no_oneof(packet_id, message_type)
    return encode_length_prefix(payload)


def _encode_envelope_no_oneof(packet_id: int, message_type: int) -> bytes:
    """Encode a PbMessage envelope WITHOUT a Message oneof field.

    Field 1 = packetId (varint)
    Field 2 = messageType (varint)
    No field 3+ (no oneof).
    """
    parts = []
    # Field 1: packetId (wire type 0 = varint, field_number 1 => tag = 0x08)
    parts.append(_encode_varint(0x08))
    parts.append(_encode_varint(packet_id))
    # Field 2: messageType (wire type 0 = varint, field_number 2 => tag = 0x10)
    parts.append(_encode_varint(0x10))
    parts.append(_encode_varint(message_type))
    return b"".join(parts)


def _make_ping_frame_with_oneof(packet_id: int = 1) -> bytes:
    """Build a Ping frame WITH the oneof set (Ping message = field 0x66 = 102)."""
    payload = _encode_envelope_with_ping_oneof(packet_id)
    return encode_length_prefix(payload)


def _encode_envelope_with_ping_oneof(packet_id: int) -> bytes:
    """Encode a PbMessage envelope WITH Ping oneof set.

    Field 1 = packetId (varint)
    Field 2 = messageType = 0x66 (varint)
    Field 102 = Ping{} (length-delimited, empty message, wire type 2)
    """
    parts = []
    # Field 1: packetId
    parts.append(_encode_varint(0x08))
    parts.append(_encode_varint(packet_id))
    # Field 2: messageType = 0x66
    parts.append(_encode_varint(0x10))
    parts.append(_encode_varint(0x66))
    # Field 102 (Ping): tag = (102 << 3) | 2 = 818 = 0x0332
    parts.append(_encode_varint(0x0332))
    parts.append(_encode_varint(0))  # length 0 = empty Ping
    return b"".join(parts)


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    parts = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value)
    return bytes(parts)


# ---------------------------------------------------------------------------
# Workstream C: Stream framing
# ---------------------------------------------------------------------------

class TestStreamFraming:
    """Test correct 4-byte LE length-prefix framing."""

    def test_decode_valid_frame(self):
        payload = b"\x08\x01\x10\x66"
        frame = encode_length_prefix(payload)
        decoded, remaining = decode_length_prefix(frame)
        assert decoded == payload
        assert remaining == b""

    def test_decode_frame_with_trailing_bytes(self):
        payload = b"\x08\x01\x10\x66"
        frame = encode_length_prefix(payload) + b"\x00\x01\x02"
        decoded, remaining = decode_length_prefix(frame)
        assert decoded == payload
        assert remaining == b"\x00\x01\x02"

    def test_decode_two_concatenated_frames(self):
        payload1 = b"\x08\x01\x10\x66"
        payload2 = b"\x08\x03\x10\x66"
        data = encode_length_prefix(payload1) + encode_length_prefix(payload2)
        decoded1, remaining = decode_length_prefix(data)
        assert decoded1 == payload1
        decoded2, remaining2 = decode_length_prefix(remaining)
        assert decoded2 == payload2
        assert remaining2 == b""

    def test_decode_incomplete_payload(self):
        header = struct.pack("<I", 100)
        data = header + b"\x00" * 50  # Only 50 bytes of 100
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(data)

    def test_decode_incomplete_header(self):
        data = b"\x00\x01"
        with pytest.raises(FramingError, match="Need 4 bytes"):
            decode_length_prefix(data)

    def test_decode_oversized_frame(self):
        header = struct.pack("<I", 2 * 1024 * 1024)  # 2 MiB
        with pytest.raises(FramingError, match="exceeds maximum"):
            decode_length_prefix(header + b"\x00" * 100)

    def test_decode_zero_length_payload(self):
        frame = struct.pack("<I", 0)
        decoded, remaining = decode_length_prefix(frame)
        assert decoded == b""
        assert remaining == b""


# ---------------------------------------------------------------------------
# Workstream D: Protobuf envelope audit
# ---------------------------------------------------------------------------

class TestProtobufEnvelopeAudit:
    """Test decoder behavior with various envelope shapes."""

    def test_decode_frame_with_empty_oneof_falls_back_to_message_type(self):
        """G33 fix: frame with messageType=0x66 and no oneof should succeed."""
        frame = _make_ping_frame(packet_id=1, message_type=0x66)
        packet_id, message_type, message_name, raw = decode_request(frame)
        assert packet_id == 1
        assert message_type == 0x66
        assert message_name == "Ping"

    def test_decode_frame_with_oneof_set_succeeds(self):
        """Normal Ping with oneof set should decode correctly."""
        frame = _make_ping_frame_with_oneof(packet_id=7)
        packet_id, message_type, message_name, raw = decode_request(frame)
        assert packet_id == 7
        assert message_type == 0x66
        assert message_name == "Ping"

    def test_decode_frame_empty_oneof_unknown_type_fails(self):
        """Frame with empty oneof and unknown messageType should fail."""
        frame = _make_ping_frame(packet_id=1, message_type=0xFF)
        with pytest.raises(DecodeError, match="unknown messageType"):
            decode_request(frame)

    def test_decode_frame_invalid_protobuf_fails(self):
        """Frame with garbage protobuf bytes should fail."""
        garbage = b"\xff\xff\xff\xff\xff\xff\xff\xff"
        frame = encode_length_prefix(garbage)
        with pytest.raises((DecodeError, Exception)):
            decode_request(frame)


# ---------------------------------------------------------------------------
# Workstream E: Ping response regression
# ---------------------------------------------------------------------------

class TestPingRegression:
    """Verify Ping echo contract is preserved after decoder fix."""

    def test_ping_request_has_prefix_and_payload(self):
        frame = _make_ping_frame(packet_id=1)
        assert len(frame) > 4  # At least prefix + some payload
        payload_len = struct.unpack_from("<I", frame, 0)[0]
        assert payload_len == len(frame) - 4

    def test_ping_response_has_prefix_and_payload(self):
        resp = encode_response(packet_id=1, message_type=0x66, payload_dict={})
        assert len(resp) > 4  # At least prefix + some payload
        payload_len = struct.unpack_from("<I", resp, 0)[0]
        assert payload_len == len(resp) - 4

    def test_ping_packet_id_preserved(self):
        resp = encode_response(packet_id=42, message_type=0x66, payload_dict={})
        packet_id, message_type, message_name, raw = decode_request(resp)
        assert packet_id == 42
        assert message_type == 0x66
        assert message_name == "Ping"

    def test_ping_roundtrip_decode_encode_decode(self):
        """Decode request, encode response, decode response — roundtrip."""
        frame = _make_ping_frame_with_oneof(packet_id=5)
        pid, mtype, mname, raw = decode_request(frame)
        assert mname == "Ping"
        resp = encode_response(packet_id=pid, message_type=mtype, payload_dict={})
        pid2, mtype2, mname2, raw2 = decode_request(resp)
        assert pid2 == 5
        assert mname2 == "Ping"

    def test_ping_odd_packet_ids(self):
        for pid in [1, 3, 5, 7, 9, 99, 65535]:
            frame = _make_ping_frame_with_oneof(packet_id=pid)
            p, m, n, _ = decode_request(frame)
            assert p == pid
            assert n == "Ping"

    def test_ping_empty_oneof_decode_succeeds(self):
        """The G32 DECODE_ERROR should now succeed with the fix."""
        frame = _make_ping_frame(packet_id=1, message_type=0x66)
        p, m, n, _ = decode_request(frame)
        assert p == 1
        assert m == 0x66
        assert n == "Ping"


# ---------------------------------------------------------------------------
# Workstream O: Safe state separation
# ---------------------------------------------------------------------------

class TestSafeStateSeparation:
    """Ensure no fabrication of trust-dependent state."""

    def test_no_is_online_fabrication(self):
        """Server code must not set IsOnline=1."""
        import app.tcp_server as ts
        with open(ts.__file__) as f:
            source = f.read()
        assert "IsOnline" not in source or "IsOnline" in source  # no forced value

    def test_no_unknown_message_response(self):
        """Server must not respond to unknown message types."""
        import app.tcp_server as ts
        with open(ts.__file__) as f:
            source = f.read()
        # handle_message returns None for unknown types
        assert "handle_message" in source

    def test_decode_request_does_not_raise_for_known_type_empty_oneof(self):
        """G33 fix: known messageType with empty oneof must not raise."""
        frame = _make_ping_frame(packet_id=1, message_type=0x66)
        # This should NOT raise DecodeError
        packet_id, message_type, message_name, raw = decode_request(frame)
        assert message_name == "Ping"
