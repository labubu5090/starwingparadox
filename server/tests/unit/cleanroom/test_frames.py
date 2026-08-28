"""Tests for frame validation."""
from __future__ import annotations

import struct

import pytest

from app.cleanroom.commands import CommandCatalog
from app.cleanroom.errors import (
    FrameTooLargeError,
    FrameTooSmallError,
    InvalidMessageTypeError,
)
from app.cleanroom.frames import (
    MIN_FRAME_SIZE,
    Frame,
    is_empty_payload,
    validate_frame,
    validate_payload_size,
)


class TestValidateFrame:
    """Test frame validation."""

    def test_valid_frame(self):
        data = struct.pack("<I", 8) + b"\x66" + b"\x00" * 3
        frame = validate_frame(data)
        assert isinstance(frame, Frame)

    def test_frame_too_small(self):
        data = b"\x00" * 3
        with pytest.raises(FrameTooSmallError):
            validate_frame(data)

    def test_frame_empty(self):
        data = b""
        with pytest.raises(FrameTooSmallError):
            validate_frame(data)

    def test_frame_exactly_min_size(self):
        data = struct.pack("<I", MIN_FRAME_SIZE)
        frame = validate_frame(data)
        assert isinstance(frame, Frame)

    def test_frame_too_large(self):
        data = struct.pack("<I", 100) + b"\x00" * 96
        with pytest.raises(FrameTooLargeError):
            validate_frame(data, max_frame_size=50)

    def test_frame_length_mismatch(self):
        # Header says 100 bytes, but only 8 provided
        data = struct.pack("<I", 100) + b"\x00" * 4
        with pytest.raises(FrameTooSmallError):
            validate_frame(data)

    def test_non_bytes_rejected(self):
        with pytest.raises(TypeError):
            validate_frame("not bytes")  # type: ignore

    def test_bytearray_accepted(self):
        data = struct.pack("<I", 8) + b"\x66" + b"\x00" * 3
        frame = validate_frame(bytearray(data))
        assert isinstance(frame, Frame)


class TestValidateFrameWithCatalog:
    """Test frame validation with catalog."""

    def test_known_message_type(self):
        catalog = CommandCatalog()
        data = struct.pack("<I", 8) + bytes([0x66]) + b"\x00" * 3
        frame = validate_frame(data, catalog=catalog)
        assert frame.message_type == 0x66

    def test_unknown_message_type_rejected(self):
        catalog = CommandCatalog()
        data = struct.pack("<I", 8) + bytes([0xFF]) + b"\x00" * 3
        with pytest.raises(InvalidMessageTypeError):
            validate_frame(data, catalog=catalog)


class TestValidatePayloadSize:
    """Test payload size validation."""

    def test_payload_within_limit(self):
        validate_payload_size(b"\x00" * 100, max_size=200)

    def test_payload_exceeds_limit(self):
        with pytest.raises(FrameTooLargeError):
            validate_payload_size(b"\x00" * 100, max_size=50)

    def test_payload_at_limit(self):
        validate_payload_size(b"\x00" * 100, max_size=100)


class TestIsEmptyPayload:
    """Test empty payload check."""

    def test_empty_payload(self):
        assert is_empty_payload(b"") is True

    def test_non_empty_payload(self):
        assert is_empty_payload(b"\x00") is False

    def test_single_byte_payload(self):
        assert is_empty_payload(b"\x01") is False
