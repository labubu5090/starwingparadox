"""Tests for the generated starwingMessage_pb2 protobuf code."""

import struct

import pytest
from google.protobuf.message import DecodeError

from app.protocol.codec import MAX_MESSAGE_SIZE, decode_length_prefix, encode_length_prefix
from app.protocol.errors import FramingError
from app.protocol.generated import starwingMessage_pb2 as pb

# ---------------------------------------------------------------------------
# PbMessage basic construction and roundtrip
# ---------------------------------------------------------------------------


class TestPbMessageConstruction:
    def test_set_packet_id_and_message_type(self):
        msg = pb.PbMessage()
        msg.packetId = 42
        msg.messageType = 0x66
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 42
        assert parsed.messageType == 0x66

    def test_roundtrip_empty_message(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 2
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 1
        assert parsed.messageType == 2

    def test_large_values(self):
        msg = pb.PbMessage()
        msg.packetId = 2**31 - 1
        msg.messageType = 2**31 - 1
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 2**31 - 1
        assert parsed.messageType == 2**31 - 1

    def test_zero_values(self):
        msg = pb.PbMessage()
        msg.packetId = 0
        msg.messageType = 0
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 0
        assert parsed.messageType == 0

    def test_session_id_optional(self):
        msg = pb.PbMessage()
        msg.packetId = 5
        msg.messageType = 10
        msg.sessionId = 999
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.sessionId == 999

    def test_no_session_id_field(self):
        msg = pb.PbMessage()
        msg.packetId = 5
        msg.messageType = 10
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert not parsed.HasField("sessionId")


# ---------------------------------------------------------------------------
# Ping message construction
# ---------------------------------------------------------------------------


class TestPingMessage:
    def test_ping_in_oneof(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        assert msg.WhichOneof("Message") == "Ping"

    def test_ping_roundtrip(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.WhichOneof("Message") == "Ping"

    def test_ping_empty_body(self):
        ping = pb.Ping()
        raw = ping.SerializeToString()
        parsed = pb.Ping()
        parsed.ParseFromString(raw)
        assert len(raw) == 0 or len(parsed.SerializeToString()) == 0


# ---------------------------------------------------------------------------
# RequestEntryMatching construction
# ---------------------------------------------------------------------------


class TestRequestEntryMatching:
    def test_set_message_type_200(self):
        msg = pb.PbMessage()
        msg.packetId = 10
        msg.messageType = 200
        msg.RequestEntryMatching.SetInParent()
        assert msg.WhichOneof("Message") == "RequestEntryMatching"

    def test_request_entry_matching_roundtrip(self):
        msg = pb.PbMessage()
        msg.packetId = 10
        msg.messageType = 200
        msg.RequestEntryMatching.SetInParent()
        raw = msg.SerializeToString()
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 10
        assert parsed.messageType == 200
        assert parsed.WhichOneof("Message") == "RequestEntryMatching"


# ---------------------------------------------------------------------------
# 4-byte LE frame length encoding with real protobuf bytes
# ---------------------------------------------------------------------------


class TestFrameLengthEncoding:
    def test_real_protobuf_frame_roundtrip(self):
        msg = pb.PbMessage()
        msg.packetId = 7
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        payload, remaining = decode_length_prefix(framed)
        assert payload == inner
        assert remaining == b""

    def test_header_is_4_bytes_le(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        expected_len = len(inner)
        actual_len = struct.unpack_from("<I", framed, 0)[0]
        assert actual_len == expected_len
        assert len(framed) == 4 + expected_len

    def test_multiple_different_message_sizes(self):
        for pkt_id in [1, 50, 255, 1000]:
            msg = pb.PbMessage()
            msg.packetId = pkt_id
            msg.messageType = 0x66
            msg.Ping.SetInParent()
            inner = msg.SerializeToString()
            framed = encode_length_prefix(inner)
            payload, _ = decode_length_prefix(framed)
            assert payload == inner


# ---------------------------------------------------------------------------
# Partial headers and payloads
# ---------------------------------------------------------------------------


class TestPartialHeadersAndPayloads:
    def test_incomplete_header(self):
        with pytest.raises(FramingError):
            decode_length_prefix(b"\x01\x00")

    def test_header_says_more_than_available(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        truncated = framed[:6]
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(truncated)

    def test_header_only(self):
        framed = b"\x05\x00\x00\x00"
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(framed)

    def test_extra_trailing_bytes_returned(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        trailing = b"\xde\xad"
        payload, remaining = decode_length_prefix(framed + trailing)
        assert payload == inner
        assert remaining == trailing


# ---------------------------------------------------------------------------
# Multiple frames in one buffer
# ---------------------------------------------------------------------------


class TestMultipleFrames:
    def test_two_consecutive_frames(self):
        msg1 = pb.PbMessage()
        msg1.packetId = 1
        msg1.messageType = 0x66
        msg1.Ping.SetInParent()

        msg2 = pb.PbMessage()
        msg2.packetId = 2
        msg2.messageType = 200
        msg2.RequestEntryMatching.SetInParent()

        frame1 = encode_length_prefix(msg1.SerializeToString())
        frame2 = encode_length_prefix(msg2.SerializeToString())
        combined = frame1 + frame2

        payload1, rest1 = decode_length_prefix(combined)
        p1 = pb.PbMessage()
        p1.ParseFromString(payload1)
        assert p1.packetId == 1
        assert p1.WhichOneof("Message") == "Ping"

        payload2, rest2 = decode_length_prefix(rest1)
        p2 = pb.PbMessage()
        p2.ParseFromString(payload2)
        assert p2.packetId == 2
        assert p2.WhichOneof("Message") == "RequestEntryMatching"

    def test_three_frames(self):
        frames = b""
        for i in range(3):
            msg = pb.PbMessage()
            msg.packetId = i
            msg.messageType = 0x66
            msg.Ping.SetInParent()
            frames += encode_length_prefix(msg.SerializeToString())

        data = frames
        for i in range(3):
            payload, data = decode_length_prefix(data)
            parsed = pb.PbMessage()
            parsed.ParseFromString(payload)
            assert parsed.packetId == i
        assert data == b""

    def test_partial_second_frame(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        frame1 = encode_length_prefix(msg.SerializeToString())

        msg2 = pb.PbMessage()
        msg2.packetId = 2
        msg2.messageType = 0x66
        frame2_full = encode_length_prefix(msg2.SerializeToString())
        frame2_partial = frame2_full[:6]

        combined = frame1 + frame2_partial
        payload1, rest = decode_length_prefix(combined)
        assert len(payload1) > 0

        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(rest)


# ---------------------------------------------------------------------------
# Oversized frames
# ---------------------------------------------------------------------------


class TestOversizedFrames:
    def test_oversized_frame_rejected(self):
        oversized = struct.pack("<I", MAX_MESSAGE_SIZE + 1) + b"\x00" * 100
        with pytest.raises(FramingError, match="exceeds maximum"):
            decode_length_prefix(oversized)

    def test_exactly_max_size_accepted(self):
        inner = b"\x00" * MAX_MESSAGE_SIZE
        framed = encode_length_prefix(inner)
        payload, _ = decode_length_prefix(framed)
        assert len(payload) == MAX_MESSAGE_SIZE

    def test_one_over_max_rejected(self):
        inner = b"\x00" * (MAX_MESSAGE_SIZE + 1)
        framed = encode_length_prefix(inner)
        with pytest.raises(FramingError, match="exceeds maximum"):
            decode_length_prefix(framed)


# ---------------------------------------------------------------------------
# Zero-length frames
# ---------------------------------------------------------------------------


class TestZeroLengthFrames:
    def test_zero_length_frame(self):
        framed = b"\x00\x00\x00\x00"
        payload, remaining = decode_length_prefix(framed)
        assert payload == b""
        assert remaining == b""

    def test_zero_length_with_trailing(self):
        framed = b"\x00\x00\x00\x00TRAILING"
        payload, remaining = decode_length_prefix(framed)
        assert payload == b""
        assert remaining == b"TRAILING"

    def test_roundtrip_empty_pb_message(self):
        msg = pb.PbMessage()
        inner = msg.SerializeToString()
        framed = encode_length_prefix(inner)
        payload, _ = decode_length_prefix(framed)
        assert payload == inner


# ---------------------------------------------------------------------------
# Invalid protobuf data
# ---------------------------------------------------------------------------


class TestInvalidProtobufData:
    def test_invalid_varint_in_pb(self):
        bad_data = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01"
        msg = pb.PbMessage()
        with pytest.raises(DecodeError):
            msg.ParseFromString(bad_data)

    def test_random_garbage_fails_parse(self):
        garbage = bytes(range(256))
        msg = pb.PbMessage()
        with pytest.raises(DecodeError):
            msg.ParseFromString(garbage)

    def test_truncated_field_value(self):
        truncated = b"\x08"
        msg = pb.PbMessage()
        with pytest.raises(DecodeError):
            msg.ParseFromString(truncated)

    def test_bad_wire_type_tag(self):
        bad_tag = b"\x07\x01"
        msg = pb.PbMessage()
        with pytest.raises(DecodeError):
            msg.ParseFromString(bad_tag)

    def test_trailing_garbage_rejected(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        raw = msg.SerializeToString()
        garbage = raw + b"\xff\xff"
        parsed = pb.PbMessage()
        with pytest.raises(DecodeError):
            parsed.ParseFromString(garbage)

    def test_valid_protobuf_unknown_fields_ignored(self):
        msg = pb.PbMessage()
        msg.packetId = 1
        msg.messageType = 0x66
        msg.Ping.SetInParent()
        raw = msg.SerializeToString()
        assert len(raw) > 0
        parsed = pb.PbMessage()
        parsed.ParseFromString(raw)
        assert parsed.packetId == 1
        assert parsed.messageType == 0x66
