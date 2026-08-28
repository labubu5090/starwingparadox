"""Tests for clean-room error types."""
from __future__ import annotations

import pytest

from app.cleanroom.errors import (
    CleanroomError,
    CommandAfterEndError,
    CommandBeforeStartError,
    DuplicateHandlerError,
    DuplicateStartError,
    FrameError,
    FrameTooLargeError,
    FrameTooSmallError,
    InvalidMessageTypeError,
    InvalidPacketIdError,
    InvalidTransitionError,
    SessionError,
    TransportClosedError,
    TransportError,
    TransportStateError,
    TransportTimeoutError,
    UnsupportedCommandError,
    WrongDirectionError,
)


class TestErrorHierarchy:
    """Test error class hierarchy."""

    def test_transport_errors_inherit_cleanroom_error(self):
        assert issubclass(TransportError, CleanroomError)
        assert issubclass(TransportClosedError, TransportError)
        assert issubclass(TransportStateError, TransportError)
        assert issubclass(TransportTimeoutError, TransportError)

    def test_frame_errors_inherit_cleanroom_error(self):
        assert issubclass(FrameError, CleanroomError)
        assert issubclass(FrameTooSmallError, FrameError)
        assert issubclass(FrameTooLargeError, FrameError)
        assert issubclass(InvalidMessageTypeError, FrameError)
        assert issubclass(InvalidPacketIdError, FrameError)

    def test_session_errors_inherit_cleanroom_error(self):
        assert issubclass(SessionError, CleanroomError)
        assert issubclass(InvalidTransitionError, SessionError)
        assert issubclass(DuplicateStartError, SessionError)
        assert issubclass(CommandBeforeStartError, SessionError)
        assert issubclass(CommandAfterEndError, SessionError)

    def test_dispatch_errors_inherit_cleanroom_error(self):
        assert issubclass(UnsupportedCommandError, CleanroomError)
        assert issubclass(WrongDirectionError, CleanroomError)
        assert issubclass(DuplicateHandlerError, CleanroomError)

    def test_all_errors_are_exception_subclasses(self):
        assert issubclass(CleanroomError, Exception)
        assert issubclass(TransportError, Exception)
        assert issubclass(FrameError, Exception)
        assert issubclass(SessionError, Exception)

    def test_errors_can_be_raised_and_caught(self):
        with pytest.raises(CleanroomError):
            raise CleanroomError("test")
        with pytest.raises(TransportClosedError):
            raise TransportClosedError("test")
        with pytest.raises(FrameTooSmallError):
            raise FrameTooSmallError("test")
        with pytest.raises(InvalidTransitionError):
            raise InvalidTransitionError("test")
        with pytest.raises(UnsupportedCommandError):
            raise UnsupportedCommandError("test")
