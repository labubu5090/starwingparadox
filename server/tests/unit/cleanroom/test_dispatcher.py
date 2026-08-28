"""Tests for dispatcher."""
from __future__ import annotations

import pytest

from app.cleanroom.commands import CommandCatalog
from app.cleanroom.dispatcher import Dispatcher
from app.cleanroom.errors import (
    DuplicateHandlerError,
    UnsupportedCommandError,
    WrongDirectionError,
)
from app.cleanroom.state import SessionStateMachine


async def dummy_handler(
    packet_id: int, message_type: int, message_name: str, payload: bytes
) -> bytes | None:
    """Dummy handler for testing."""
    return b"response"


async def failing_handler(
    packet_id: int, message_type: int, message_name: str, payload: bytes
) -> bytes | None:
    """Handler that raises an exception."""
    raise ValueError("handler error")


class TestDispatcherRegister:
    """Test handler registration."""

    def test_register_eligible_command(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        assert dispatcher.is_registered(0x66)

    def test_register_ineligible_command(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        # 0x66 is eligible, so test with non-existent type
        with pytest.raises(UnsupportedCommandError):
            dispatcher.register(999, dummy_handler)

    def test_register_duplicate(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        with pytest.raises(DuplicateHandlerError):
            dispatcher.register(0x66, dummy_handler)

    def test_register_service_to_client_command(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        # SCOMMAND_PING_RESPONSE (0x67) is service-to-client
        with pytest.raises(WrongDirectionError):
            dispatcher.register(0x67, dummy_handler)

    def test_unregister(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        dispatcher.unregister(0x66)
        assert dispatcher.is_registered(0x66) is False


class TestDispatcherDispatch:
    """Test command dispatch."""

    @pytest.mark.asyncio
    async def test_dispatch_eligible_command(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        sm.open_transport()
        sm.receive_client_start()
        sm.send_start_reply()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        result = await dispatcher.dispatch(0x66, 1, "PING", b"")
        assert result == b"response"

    @pytest.mark.asyncio
    async def test_dispatch_unsupported_command(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        sm.open_transport()
        dispatcher = Dispatcher(catalog, sm)
        with pytest.raises(UnsupportedCommandError):
            await dispatcher.dispatch(999, 1, "UNKNOWN", b"")

    @pytest.mark.asyncio
    async def test_dispatch_before_start(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        # State is CREATED, command not allowed
        from app.cleanroom.errors import CommandBeforeStartError
        with pytest.raises(CommandBeforeStartError):
            await dispatcher.dispatch(0x66, 1, "PING", b"")

    @pytest.mark.asyncio
    async def test_dispatch_after_close(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        sm.open_transport()
        sm.close()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        from app.cleanroom.errors import CommandAfterEndError
        with pytest.raises(CommandAfterEndError):
            await dispatcher.dispatch(0x66, 1, "PING", b"")


class TestDispatcherRegisteredTypes:
    """Test registered types listing."""

    def test_registered_types(self):
        catalog = CommandCatalog()
        sm = SessionStateMachine()
        dispatcher = Dispatcher(catalog, sm)
        dispatcher.register(0x66, dummy_handler)
        types = dispatcher.registered_types()
        assert 0x66 in types
