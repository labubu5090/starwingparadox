"""Protocol decode errors."""


class ProtocolError(Exception):
    """Base protocol error."""


class DecodeError(ProtocolError):
    """Failed to decode protobuf message."""


class UnknownMessageType(ProtocolError):  # noqa: N818
    """Unknown message type received."""


class FramingError(ProtocolError):
    """Invalid packet framing."""
