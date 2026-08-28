"""Evidence-locked codec for clean-room protocol foundation.

This module implements a codec that explicitly documents what is
confirmed by G16 evidence vs what is inferred or synthetic.

Evidence hierarchy:
1. G16 confirmed facts (HIGH confidence)
2. G16 eligible behaviors (MEDIUM confidence)
3. G17 synthetic implementation (test-only)
4. Unknown / not confirmed

Codec constraints:
- No protobuf parsing (deferred to existing codec)
- No production binary format assumptions
- Frame structure: 4-byte LE length prefix + payload
- Message type: first byte of payload (simplified G17 model)
- Packet ID: NOT confirmed (always 0)
- No invented payload schemas
"""
from __future__ import annotations

import enum
import struct
from dataclasses import dataclass

from app.cleanroom.errors import (
    FrameTooLargeError,
    FrameTooSmallError,
    InvalidMessageTypeError,
)


class CodecEvidenceLevel(enum.Enum):
    """Evidence level for codec components."""

    CONFIRMED = "confirmed"
    ELIGIBLE = "eligible"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CodecEvidenceRecord:
    """Documents the evidence level for a codec component.

    Attributes:
        component: Name of the codec component.
        evidence_level: Evidence classification.
        source: Evidence source reference.
        constraints: Known constraints or limitations.
    """

    component: str
    evidence_level: CodecEvidenceLevel
    source: str
    constraints: str = ""


@dataclass(frozen=True)
class DecodedFrame:
    """A decoded protocol frame with evidence annotations.

    Attributes:
        length_prefix: The 4-byte LE length prefix value.
        message_type: First byte of payload (simplified G17 model).
        payload: Remaining payload bytes (opaque).
        evidence_level: Evidence level for this frame.
        packet_id: Always 0 (no evidence for extraction).
    """

    length_prefix: int
    message_type: int
    payload: bytes
    evidence_level: CodecEvidenceLevel
    packet_id: int = 0


class EvidenceLockedCodec:
    """Codec that enforces evidence-locked constraints.

    This codec:
    - Only parses what is confirmed by G16 evidence
    - Documents evidence levels for all components
    - Rejects unknown message types when catalog is provided
    - Never invents payload schemas
    - Never assumes protobuf structure
    - Never assumes production binary format

    Evidence records:
    - LENGTH_PREFIX: CONFIRMED (G16 observed 4-byte LE length prefix)
    - MESSAGE_TYPE: ELIGIBLE (first byte of payload, simplified G17 model)
    - PACKET_ID: UNKNOWN (always 0, no evidence for extraction)
    - PAYLOAD: CONFIRMED (opaque bytes, no parsing)
    """

    EVIDENCE_RECORDS = [
        CodecEvidenceRecord(
            component="length_prefix",
            evidence_level=CodecEvidenceLevel.CONFIRMED,
            source="G16 observed 4-byte LE length prefix",
            constraints="Must match total frame size",
        ),
        CodecEvidenceRecord(
            component="message_type",
            evidence_level=CodecEvidenceLevel.ELIGIBLE,
            source="G17 simplified model: first byte of payload",
            constraints="Real protocol may use different extraction",
        ),
        CodecEvidenceRecord(
            component="packet_id",
            evidence_level=CodecEvidenceLevel.UNKNOWN,
            source="No evidence in G16",
            constraints="Always returns 0",
        ),
        CodecEvidenceRecord(
            component="payload",
            evidence_level=CodecEvidenceLevel.CONFIRMED,
            source="G16 confirmed opaque bytes",
            constraints="No parsing, no schema assumptions",
        ),
    ]

    MIN_FRAME_SIZE = 4
    MAX_FRAME_SIZE = 1024 * 1024

    def __init__(
        self,
        known_message_types: set[int] | None = None,
    ) -> None:
        """Initialize the codec.

        Args:
            known_message_types: Set of known message type IDs.
                If provided, unknown types are rejected.
        """
        self._known_types = known_message_types or set()

    def get_evidence_records(self) -> list[CodecEvidenceRecord]:
        """Return all evidence records for this codec.

        Returns:
            List of CodecEvidenceRecord instances.
        """
        return list(self.EVIDENCE_RECORDS)

    def decode(self, data: bytes) -> DecodedFrame:
        """Decode a raw frame with evidence-locked constraints.

        Args:
            data: Raw frame bytes.

        Returns:
            DecodedFrame with evidence annotations.

        Raises:
            TypeError: If data is not bytes-like.
            FrameTooSmallError: If frame is too small.
            FrameTooLargeError: If frame exceeds maximum size.
            InvalidMessageTypeError: If message type not in catalog.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Frame data must be bytes-like")

        if len(data) < self.MIN_FRAME_SIZE:
            raise FrameTooSmallError(
                f"Frame too small: {len(data)} bytes < "
                f"{self.MIN_FRAME_SIZE} minimum"
            )

        if len(data) > self.MAX_FRAME_SIZE:
            raise FrameTooLargeError(
                f"Frame too large: {len(data)} bytes > "
                f"{self.MAX_FRAME_SIZE} maximum"
            )

        length_prefix = struct.unpack_from("<I", data, 0)[0]

        if length_prefix != len(data):
            raise FrameTooSmallError(
                f"Frame length mismatch: header says {length_prefix}, "
                f"actual {len(data)}"
            )

        if len(data) > self.MIN_FRAME_SIZE:
            message_type = data[self.MIN_FRAME_SIZE]
            payload = data[self.MIN_FRAME_SIZE + 1:]
        else:
            message_type = 0
            payload = b""

        if self._known_types and message_type != 0 and message_type not in self._known_types:
            raise InvalidMessageTypeError(
                f"Unknown message type: 0x{message_type:02x}"
            )

        return DecodedFrame(
            length_prefix=length_prefix,
            message_type=message_type,
            payload=payload,
            evidence_level=CodecEvidenceLevel.ELIGIBLE,
        )

    def encode(
        self,
        message_type: int,
        payload: bytes,
    ) -> bytes:
        """Encode a frame with evidence-locked constraints.

        This method creates a minimal frame for testing only.
        It does NOT assume any production binary format.

        The length prefix includes itself (4 bytes) + message_type (1 byte)
        + payload length.

        Args:
            message_type: Numeric message type.
            payload: Payload bytes.

        Returns:
            Encoded frame bytes.
        """
        frame_data = bytes([message_type]) + payload
        total_length = 4 + len(frame_data)
        length_prefix = struct.pack("<I", total_length)
        return length_prefix + frame_data
