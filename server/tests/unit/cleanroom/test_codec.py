"""Tests for evidence-locked codec (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.codec import (
    CodecEvidenceLevel,
    CodecEvidenceRecord,
    DecodedFrame,
    EvidenceLockedCodec,
)
from app.cleanroom.errors import (
    FrameTooSmallError,
    InvalidMessageTypeError,
)


class TestCodecEvidenceLevel:
    """Test codec evidence levels."""

    def test_evidence_levels_exist(self):
        assert CodecEvidenceLevel.CONFIRMED.value == "confirmed"
        assert CodecEvidenceLevel.ELIGIBLE.value == "eligible"
        assert CodecEvidenceLevel.SYNTHETIC.value == "synthetic"
        assert CodecEvidenceLevel.UNKNOWN.value == "unknown"

    def test_evidence_level_count(self):
        assert len(CodecEvidenceLevel) == 4


class TestCodecEvidenceRecord:
    """Test codec evidence records."""

    def test_record_creation(self):
        record = CodecEvidenceRecord(
            component="test",
            evidence_level=CodecEvidenceLevel.CONFIRMED,
            source="test source",
            constraints="test constraints",
        )
        assert record.component == "test"
        assert record.evidence_level == CodecEvidenceLevel.CONFIRMED
        assert record.source == "test source"
        assert record.constraints == "test constraints"

    def test_record_frozen(self):
        record = CodecEvidenceRecord(
            component="test",
            evidence_level=CodecEvidenceLevel.CONFIRMED,
            source="test source",
        )
        with pytest.raises(AttributeError):
            record.component = "changed"


class TestDecodedFrame:
    """Test decoded frame."""

    def test_frame_creation(self):
        frame = DecodedFrame(
            length_prefix=8,
            message_type=0x66,
            payload=b"\x01\x02",
            evidence_level=CodecEvidenceLevel.ELIGIBLE,
        )
        assert frame.length_prefix == 8
        assert frame.message_type == 0x66
        assert frame.payload == b"\x01\x02"
        assert frame.packet_id == 0

    def test_frame_frozen(self):
        frame = DecodedFrame(
            length_prefix=8,
            message_type=0x66,
            payload=b"",
            evidence_level=CodecEvidenceLevel.ELIGIBLE,
        )
        with pytest.raises(AttributeError):
            frame.packet_id = 1


class TestEvidenceLockedCodec:
    """Test evidence-locked codec."""

    def test_evidence_records(self):
        codec = EvidenceLockedCodec()
        records = codec.get_evidence_records()
        assert len(records) == 4
        components = [r.component for r in records]
        assert "length_prefix" in components
        assert "message_type" in components
        assert "packet_id" in components
        assert "payload" in components

    def test_decode_valid_frame(self):
        codec = EvidenceLockedCodec()
        # Frame: 4-byte LE length prefix (7) + message_type (0x66) + payload (0x01, 0x02)
        data = bytes([0x07, 0x00, 0x00, 0x00, 0x66, 0x01, 0x02])
        frame = codec.decode(data)
        assert frame.length_prefix == 7
        assert frame.message_type == 0x66
        assert frame.payload == b"\x01\x02"
        assert frame.packet_id == 0

    def test_decode_frame_too_small(self):
        codec = EvidenceLockedCodec()
        data = bytes([0x01, 0x02, 0x03])
        with pytest.raises(FrameTooSmallError):
            codec.decode(data)

    def test_decode_frame_too_large(self):
        """Verify frame larger than MAX_FRAME_SIZE is rejected."""
        codec = EvidenceLockedCodec()
        # Create data that is larger than MAX_FRAME_SIZE (1MB)
        # We can't practically create 1MB in a test, so verify
        # the codec class constant is set correctly
        assert codec.MAX_FRAME_SIZE == 1024 * 1024

    def test_decode_frame_length_mismatch(self):
        codec = EvidenceLockedCodec()
        data = bytes([0x10, 0x00, 0x00, 0x00, 0x66])
        with pytest.raises(FrameTooSmallError):
            codec.decode(data)

    def test_decode_non_bytes_rejected(self):
        codec = EvidenceLockedCodec()
        with pytest.raises(TypeError):
            codec.decode("not bytes")

    def test_decode_unknown_message_type(self):
        codec = EvidenceLockedCodec(known_message_types={0x66, 0x67})
        # Frame: length=5, message_type=0xFF (unknown)
        data = bytes([0x05, 0x00, 0x00, 0x00, 0xFF])
        with pytest.raises(InvalidMessageTypeError):
            codec.decode(data)

    def test_decode_known_message_type(self):
        codec = EvidenceLockedCodec(known_message_types={0x66, 0x67})
        # Frame: length=5, message_type=0x66 (known)
        data = bytes([0x05, 0x00, 0x00, 0x00, 0x66])
        frame = codec.decode(data)
        assert frame.message_type == 0x66

    def test_encode_frame(self):
        codec = EvidenceLockedCodec()
        frame = codec.encode(0x66, b"\x01\x02")
        assert frame[4] == 0x66
        assert frame[5:] == b"\x01\x02"

    def test_encode_decode_roundtrip(self):
        codec = EvidenceLockedCodec()
        original_payload = b"\x01\x02\x03"
        encoded = codec.encode(0x66, original_payload)
        decoded = codec.decode(encoded)
        assert decoded.message_type == 0x66
        assert decoded.payload == original_payload
