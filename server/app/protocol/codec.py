"""Protocol codec for encoding/decoding Starwing protobuf messages.

Binary framing: 4-byte uint32 little-endian length prefix, then protobuf bytes.

Usage with generated code (after running proto/generate_proto.py):
    from app.protocol.generated import starwingMessage_pb2 as pb
    msg = pb.PbMessage()
    msg.ParseFromString(raw_bytes)

Fallback mode (no generated code): logs warnings and operates on raw bytes.
"""

from __future__ import annotations

import hashlib
import logging
import struct
from typing import Any

from app.protocol.errors import DecodeError, FramingError, UnknownMessageType
from app.protocol.registry import MESSAGE_TYPE_MAP

logger = logging.getLogger(__name__)

# Try importing generated protobuf modules
try:
    from app.protocol.generated import starwingMessage_pb2 as pb_module

    HAS_GENERATED = True
    logger.info("Generated protobuf modules loaded successfully")
except ImportError:
    HAS_GENERATED = False
    logger.warning(
        "Generated protobuf modules not found. "
        "Run server/scripts/generate_proto.py to generate them. "
        "Operating in raw-bytes fallback mode."
    )

FRAME_HEADER_SIZE = 4
MAX_MESSAGE_SIZE = 1 * 1024 * 1024  # 1 MiB safety limit


def _compute_digest(data: bytes) -> str:
    """Compute SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()[:16]


def decode_length_prefix(data: bytes) -> tuple[bytes, bytes]:
    """Decode the 4-byte LE length prefix and extract the protobuf payload.

    Args:
        data: Raw bytes starting from the length prefix.

    Returns:
        Tuple of (payload_bytes, remaining_bytes).

    Raises:
        FramingError: If the frame is invalid.
    """
    if len(data) < FRAME_HEADER_SIZE:
        raise FramingError(f"Need {FRAME_HEADER_SIZE} bytes for header, got {len(data)}")

    msg_len = struct.unpack_from("<I", data, 0)[0]

    if msg_len > MAX_MESSAGE_SIZE:
        raise FramingError(f"Message length {msg_len} exceeds maximum {MAX_MESSAGE_SIZE}")

    end = FRAME_HEADER_SIZE + msg_len
    if len(data) < end:
        raise FramingError(f"Incomplete frame: need {end} bytes, got {len(data)}")

    payload = data[FRAME_HEADER_SIZE:end]
    remaining = data[end:]
    return payload, remaining


def encode_length_prefix(payload: bytes) -> bytes:
    """Encode a payload with a 4-byte LE length prefix."""
    header = struct.pack("<I", len(payload))
    return header + payload


def decode_request(data: bytes) -> tuple[int, int, str, bytes]:
    """Decode a raw request frame into its components.

    Args:
        data: Full frame bytes (length prefix + protobuf payload).

    Returns:
        Tuple of (packet_id, message_type, message_name, payload_bytes).

    Raises:
        FramingError: If frame is invalid.
        DecodeError: If protobuf parsing fails.
        UnknownMessageType: If messageType is not in the registry.
    """
    payload, _ = decode_length_prefix(data)

    digest = _compute_digest(payload)
    logger.debug("Decoding frame: %d bytes, sha256=%s", len(payload), digest)

    if HAS_GENERATED:
        return _decode_with_generated(payload)
    else:
        return _decode_raw(payload)


def _decode_with_generated(payload: bytes) -> tuple[int, int, str, bytes]:
    """Decode using generated protobuf classes."""
    msg = pb_module.PbMessage()  # type: ignore[attr-defined]
    try:
        msg.ParseFromString(payload)
    except Exception as e:
        raise DecodeError(f"Protobuf parse failed: {e}") from e

    packet_id = msg.packetId
    message_type = msg.messageType
    inner = msg.WhichOneof("Message")

    if inner is None:
        raise DecodeError("PbMessage has no Message oneof set")

    message_name = inner
    logger.info(
        "Decoded: packetId=%d messageType=%d name=%s payload=%d bytes",
        packet_id,
        message_type,
        message_name,
        len(payload),
    )
    return packet_id, message_type, message_name, payload


def _decode_raw(payload: bytes) -> tuple[int, int, str, bytes]:
    """Fallback decode: extract packetId and messageType via raw varint parsing.

    This is a minimal parser for the PbMessage envelope:
      field 1 (packetId, int64)   = varint
      field 2 (messageType, int64) = varint
      field 3 (sessionId, int64)  = varint (optional)
      field 4 (Message oneof)     = length-delimited
    """
    pos = 0
    packet_id = 0
    message_type = 0
    has_session_id = False

    # Scan for field tags
    while pos < len(payload):
        tag, pos = _read_varint(payload, pos)
        field_number = tag >> 3
        wire_type = tag & 0x07

        if wire_type == 0:  # varint
            value, pos = _read_varint(payload, pos)
            if field_number == 1:
                packet_id = value
            elif field_number == 2:
                message_type = value
            elif field_number == 3:
                has_session_id = True
        elif wire_type == 2:  # length-delimited
            length, pos = _read_varint(payload, pos)
            pos += length  # skip the embedded message bytes
        else:
            raise DecodeError(f"Unexpected wire type {wire_type} at field {field_number}")

    message_name = MESSAGE_TYPE_MAP.get(message_type)
    if message_name is None:
        raise UnknownMessageType(f"Unknown messageType={message_type} (0x{message_type:X})")

    logger.info(
        "Raw decoded: packetId=%d messageType=%d name=%s payload=%d bytes%s",
        packet_id,
        message_type,
        message_name,
        len(payload),
        " (has sessionId)" if has_session_id else "",
    )
    return packet_id, message_type, message_name, payload


def _read_varint(data: bytes, pos: int) -> tuple[int, int]:
    """Read a protobuf varint from data at pos. Returns (value, new_pos)."""
    result = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if (byte & 0x80) == 0:
            return result, pos
        shift += 7
    raise DecodeError("Truncated varint")


def encode_response(packet_id: int, message_type: int, payload_dict: dict[str, Any]) -> bytes:
    """Encode a PbMessage response frame.

    Args:
        packet_id: The packet ID (echoed from request or new).
        message_type: The messageType value for the response.
        payload_dict: Dictionary of fields for the inner message.

    Returns:
        Fully framed bytes: 4-byte LE length prefix + protobuf PbMessage bytes.

    Raises:
        RuntimeError: If no generated code is available for encoding.
    """
    if not HAS_GENERATED:
        raise RuntimeError(
            "Encoding requires generated protobuf modules. "
            "Run server/scripts/generate_proto.py first."
        )

    inner_class_name = MESSAGE_TYPE_MAP.get(message_type)
    if inner_class_name is None:
        raise ValueError(f"Unknown message type: {message_type}")

    # Get the inner message class from the generated module
    inner_class = getattr(pb_module, inner_class_name, None)
    if inner_class is None:
        raise ValueError(f"Generated class not found: {inner_class_name}")

    inner_msg = inner_class(**payload_dict)

    # Build PbMessage envelope
    pb_msg = pb_module.PbMessage()  # type: ignore[attr-defined]
    pb_msg.packetId = packet_id
    pb_msg.messageType = message_type
    getattr(pb_msg, inner_class_name).CopyFrom(inner_msg)

    raw_bytes = pb_msg.SerializeToString()

    logger.info(
        "Encoded: packetId=%d messageType=%d name=%s payload=%d bytes",
        packet_id,
        message_type,
        inner_class_name,
        len(raw_bytes),
    )

    return encode_length_prefix(raw_bytes)
