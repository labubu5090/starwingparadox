"""Tests for protocol framing and message type registry."""

import struct

import pytest


def encode_varint32(value: int) -> bytes:
    """Encode a 32-bit integer as a protobuf varint."""
    result = b""
    while value > 0x7F:
        result += bytes([0x80 | (value & 0x7F)])
        value >>= 7
    result += bytes([value])
    return result


def decode_varint32(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Decode a protobuf varint from bytes. Returns (value, bytes_consumed)."""
    result = 0
    shift = 0
    bytes_read = 0
    while True:
        if offset + bytes_read >= len(data):
            raise ValueError("Unexpected end of data while reading varint")
        byte = data[offset + bytes_read]
        bytes_read += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, bytes_read


def encode_length_prefixed(payload: bytes) -> bytes:
    """Encode a protobuf message with 4-byte LE length prefix."""
    length_bytes = struct.pack("<I", len(payload))
    return length_bytes + payload


def decode_length_prefixed(data: bytes) -> tuple[bytes, int]:
    """Decode a length-prefixed protobuf message. Returns (payload, total_bytes)."""
    if len(data) < 4:
        raise ValueError("Data too short for length prefix")
    length = struct.unpack("<I", data[:4])[0]
    if len(data) < 4 + length:
        raise ValueError(f"Data too short: need {4 + length} bytes, got {len(data)}")
    return data[4 : 4 + length], 4 + length


# Simulated PbMessage fields
PACKET_ID_FIELD = 1
MESSAGE_TYPE_FIELD = 2


def encode_pb_message(packet_id: int, message_type: int, payload: bytes = b"") -> bytes:
    """Encode a simplified PbMessage with packetId and messageType."""
    result = b""
    if packet_id:
        result += bytes([0x08])  # field 1, wire type 0 (varint)
        result += encode_varint32(packet_id)
    if message_type:
        result += bytes([0x10])  # field 2, wire type 0 (varint)
        result += encode_varint32(message_type)
    if payload:
        result += payload
    return result


def decode_pb_message(data: bytes) -> dict:
    """Decode a simplified PbMessage."""
    result = {"packetId": 0, "messageType": 0}
    offset = 0
    while offset < len(data):
        tag, tag_bytes = decode_varint32(data, offset)
        offset += tag_bytes
        field_number = tag >> 3
        wire_type = tag & 0x07

        if wire_type == 0:  # varint
            value, value_bytes = decode_varint32(data, offset)
            offset += value_bytes
            if field_number == PACKET_ID_FIELD:
                result["packetId"] = value
            elif field_number == MESSAGE_TYPE_FIELD:
                result["messageType"] = value
        else:
            raise ValueError(f"Unsupported wire type {wire_type} for field {field_number}")

    return result


class TestVarintEncoding:
    """Test protobuf varint encoding/decoding."""

    def test_encode_zero(self):
        assert encode_varint32(0) == b"\x00"

    def test_encode_one(self):
        assert encode_varint32(1) == b"\x01"

    def test_encode_127(self):
        assert encode_varint32(127) == b"\x7f"

    def test_encode_128(self):
        assert encode_varint32(128) == b"\x80\x01"

    def test_encode_300(self):
        assert encode_varint32(300) == b"\xac\x02"

    def test_roundtrip(self):
        for value in [0, 1, 127, 128, 255, 256, 1000, 65535, 70571]:
            encoded = encode_varint32(value)
            decoded, _ = decode_varint32(encoded)
            assert decoded == value, f"Roundtrip failed for {value}"


class TestLengthPrefixedFraming:
    """Test 4-byte LE length prefix framing."""

    def test_encode_short_payload(self):
        payload = b"\x08\x01"
        framed = encode_length_prefixed(payload)
        assert len(framed) == 6  # 4 prefix + 2 payload
        assert framed[:4] == b"\x02\x00\x00\x00"

    def test_encode_empty_payload(self):
        payload = b""
        framed = encode_length_prefixed(payload)
        assert len(framed) == 4
        assert framed[:4] == b"\x00\x00\x00\x00"

    def test_decode_short_payload(self):
        framed = b"\x02\x00\x00\x00\x08\x01"
        payload, total = decode_length_prefixed(framed)
        assert payload == b"\x08\x01"
        assert total == 6

    def test_decode_empty_payload(self):
        framed = b"\x00\x00\x00\x00"
        payload, total = decode_length_prefixed(framed)
        assert payload == b""
        assert total == 4

    def test_roundtrip(self):
        payload = b"\x08\x01\x10\x03"
        framed = encode_length_prefixed(payload)
        decoded, total = decode_length_prefixed(framed)
        assert decoded == payload
        assert total == len(framed)

    def test_decode_too_short_data(self):
        with pytest.raises(ValueError, match="too short"):
            decode_length_prefixed(b"\x01\x00")

    def test_decode_truncated_payload(self):
        framed = b"\x05\x00\x00\x00\x08\x01"
        with pytest.raises(ValueError, match="too short"):
            decode_length_prefixed(framed)


class TestPbMessageEncoding:
    """Test simplified PbMessage encoding/decoding."""

    def test_encode_ping(self):
        msg = encode_pb_message(packet_id=1, message_type=102)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 1
        assert decoded["messageType"] == 102

    def test_encode_request_entry_matching(self):
        msg = encode_pb_message(packet_id=42, message_type=200)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 42
        assert decoded["messageType"] == 200

    def test_encode_response_entry_matching(self):
        msg = encode_pb_message(packet_id=42, message_type=201)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 42
        assert decoded["messageType"] == 201

    def test_encode_notify_match_made(self):
        msg = encode_pb_message(packet_id=43, message_type=302)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 43
        assert decoded["messageType"] == 302

    def test_encode_notify_match_begin(self):
        msg = encode_pb_message(packet_id=44, message_type=304)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 44
        assert decoded["messageType"] == 304

    def test_full_wire_format(self):
        """Test complete wire format: 4-byte LE length + PbMessage."""
        inner = encode_pb_message(packet_id=1, message_type=102)
        framed = encode_length_prefixed(inner)
        payload, total = decode_length_prefixed(framed)
        decoded = decode_pb_message(payload)
        assert decoded["packetId"] == 1
        assert decoded["messageType"] == 102
        assert total == len(framed)

    def test_large_packet_id(self):
        msg = encode_pb_message(packet_id=999999, message_type=200)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 999999

    def test_zero_values(self):
        msg = encode_pb_message(packet_id=0, message_type=0)
        decoded = decode_pb_message(msg)
        assert decoded["packetId"] == 0
        assert decoded["messageType"] == 0


class TestWireFormatIntegration:
    """Integration tests simulating full packet encode/decode."""

    def test_simulate_cabinet_ping(self):
        """Simulate a cabinet sending a ping message."""
        # Cabinet sends: ping with timestamp 1234567890
        inner = encode_pb_message(packet_id=1, message_type=102)
        framed = encode_length_prefixed(inner)

        # Server receives and decodes
        payload, _ = decode_length_prefixed(framed)
        msg = decode_pb_message(payload)
        assert msg["messageType"] == 102

        # Server sends response: ping response with timestamp
        response_inner = encode_pb_message(packet_id=1, message_type=103)
        response_framed = encode_length_prefixed(response_inner)

        # Client receives response
        resp_payload, _ = decode_length_prefixed(response_framed)
        resp_msg = decode_pb_message(resp_payload)
        assert resp_msg["messageType"] == 103

    def test_simulate_match_entry(self):
        """Simulate a cabinet requesting match entry."""
        inner = encode_pb_message(packet_id=10, message_type=200)
        framed = encode_length_prefixed(inner)

        payload, _ = decode_length_prefixed(framed)
        msg = decode_pb_message(payload)
        assert msg["messageType"] == 200
        assert msg["packetId"] == 10
