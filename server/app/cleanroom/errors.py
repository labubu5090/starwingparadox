"""Clean-room error types.

All errors in this module are specific to the clean-room compatibility
foundation and do not interact with production systems.
"""
from __future__ import annotations


class CleanroomError(Exception):
    """Base error for clean-room protocol foundation."""


class TransportError(CleanroomError):
    """Base error for transport operations."""


class TransportClosedError(TransportError):
    """Operation attempted on a closed transport."""


class TransportStateError(TransportError):
    """Operation not valid in current transport state."""


class TransportTimeoutError(TransportError):
    """Transport operation timed out."""


class FrameError(CleanroomError):
    """Base error for frame processing."""


class FrameTooSmallError(FrameError):
    """Frame is smaller than minimum size."""


class FrameTooLargeError(FrameError):
    """Frame exceeds maximum allowed size."""


class InvalidMessageTypeError(FrameError):
    """Message type is not registered in the catalog."""


class InvalidPacketIdError(FrameError):
    """Packet ID is invalid (negative or missing)."""


class SessionError(CleanroomError):
    """Base error for session state machine."""


class InvalidTransitionError(SessionError):
    """State transition is not allowed."""


class DuplicateStartError(SessionError):
    """SESSION_START received when already started."""


class CommandBeforeStartError(SessionError):
    """Command received before session start."""


class CommandAfterEndError(SessionError):
    """Command received after session end."""


class DispatchError(CleanroomError):
    """Base error for command dispatch."""


class UnsupportedCommandError(DispatchError):
    """Command is not supported or not implemented."""


class WrongDirectionError(DispatchError):
    """Command sent in wrong direction."""


class DuplicateHandlerError(DispatchError):
    """Handler already registered for this message type."""
