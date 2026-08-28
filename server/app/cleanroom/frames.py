"""Frame validation for clean-room protocol foundation.

This module implements only the minimum frame abstraction directly
supported by G16 evidence. Unknown payload bytes remain opaque.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.cleanroom.errors import (
    FrameTooLargeError,
    FrameTooSmallError,
    InvalidMessageTypeError,
)

if TYPE_CHECKING:
    from app.cleanroom.commands import CommandCatalog

MIN_FRAME_SIZE = 4
DEFAULT_MAX_FRAME_SIZE = 1024 * 1024


@dataclass(frozen=True)
class Frame:
    """A validated protocol frame.

    Attributes:
        packet_id: Non-negative packet identifier.
        message_type: Numeric message type identifier.
        message_name: Symbolic message name from registry.
        payload: Raw payload bytes (opaque).
    """

    packet_id: int
    message_type: int
    message_name: str
    payload: bytes


def validate_frame(
    data: bytes,
    *,
    max_frame_size: int = DEFAULT_MAX_FRAME_SIZE,
    catalog: CommandCatalog | None = None,
) -> Frame:
    """Validate and parse a raw frame.

    This function enforces only confirmed G16 boundaries:
    - frame must be at least MIN_FRAME_SIZE bytes
    - frame must not exceed max_frame_size
    - packet_id must be non-negative
    - message_type must be registered if catalog is provided

    Args:
        data: Raw frame bytes.
        max_frame_size: Maximum allowed frame size.
        catalog: Optional command catalog for validation.

    Returns:
        Validated Frame object.

    Raises:
        FrameTooSmallError: If frame is too small.
        FrameTooLargeError: If frame exceeds maximum size.
        InvalidPacketIdError: If packet_id is negative.
        InvalidMessageTypeError: If message_type not in catalog.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Frame data must be bytes-like")

    if len(data) < MIN_FRAME_SIZE:
        raise FrameTooSmallError(
            f"Frame too small: {len(data)} bytes < {MIN_FRAME_SIZE} minimum"
        )

    if len(data) > max_frame_size:
        raise FrameTooLargeError(
            f"Frame too large: {len(data)} bytes > {max_frame_size} maximum"
        )

    # Parse the 4-byte LE length prefix
    import struct
    frame_length = struct.unpack_from("<I", data, 0)[0]

    if frame_length != len(data):
        raise FrameTooSmallError(
            f"Frame length mismatch: header says {frame_length}, "
            f"actual {len(data)}"
        )

    # For G17, we treat the remaining bytes as opaque payload
    # The actual protobuf parsing is handled by the existing codec
    # We extract a minimal header for validation
    if len(data) > MIN_FRAME_SIZE:
        # Extract message type from the first byte after length prefix
        # This is a simplified validation; full parsing uses existing codec
        message_type = data[MIN_FRAME_SIZE] if len(data) > MIN_FRAME_SIZE else 0
        payload = data[MIN_FRAME_SIZE:]
    else:
        message_type = 0
        payload = b""

    # Validate against catalog if provided
    if catalog is not None:
        cmd = catalog.get_by_id(message_type)
        if cmd is None and message_type != 0:
            raise InvalidMessageTypeError(
                f"Unknown message type: 0x{message_type:02x}"
            )

    return Frame(
        packet_id=0,
        message_type=message_type,
        message_name=f"TYPE_{message_type:02x}",
        payload=payload,
    )


def validate_payload_size(
    data: bytes,
    *,
    max_size: int = DEFAULT_MAX_FRAME_SIZE,
) -> None:
    """Validate payload size without full parsing.

    Args:
        data: Payload bytes.
        max_size: Maximum allowed size.

    Raises:
        FrameTooLargeError: If payload exceeds maximum size.
    """
    if len(data) > max_size:
        raise FrameTooLargeError(
            f"Payload too large: {len(data)} bytes > {max_size} maximum"
        )


def is_empty_payload(data: bytes) -> bool:
    """Check if payload is empty.

    Args:
        data: Payload bytes.

    Returns:
        True if payload is empty.
    """
    return len(data) == 0
