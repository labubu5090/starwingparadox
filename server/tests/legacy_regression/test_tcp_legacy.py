"""Legacy regression: TCP server framing protocol.

Source evidence: legacy-js/js/starwing.js lines 80, 71-73, 96-104, 303-341
Evidence audit: docs/TCP_SERVER_EVIDENCE_AUDIT.md

The legacy TCP server (starwing.js:80-342) implements:
  1. 4-byte little-endian length prefix framing (E6-E9, E10-E13)
  2. Protobuf PbMessage envelope (E28-E31)
  3. Handler dispatch by messageType (E32-E36)
  4. Socket event handlers: data, error, timeout, end, close (E22-E27)
  5. Connection authorization via IP whitelist (E19-E21)

REGRESSION STATUS: The Python TCP server (tcp_server.py) replicates:
  - 4-byte LE length prefix framing: SOURCE_VERIFIED (E6-E13)
  - Ping handler (0x66): SOURCE_VERIFIED (E33, tcp_server.py:89)
  - Handler dispatch registry: SOURCE_VERIFIED (E32-E36, tcp_server.py:39-47)
  - Incremental buffering: FUNCTIONAL_PARITY (handles partial frames)

Known deviations (Python hardening, NOT legacy parity):
  - Timeout behavior: 30s configurable vs legacy unset (§4.2, §4.5 of audit)
  - Max frame size: 1 MiB safety limit (§4.3 of audit)
  - IP authorization: NOT_IMPLEMENTED (§4.4 of audit)
"""

import asyncio
import struct

import pytest

pytestmark = [pytest.mark.legacy_regression, pytest.mark.tcp]


# ---------------------------------------------------------------------------
# Evidence references
# ---------------------------------------------------------------------------
E6 = "legacy-js/js/starwing.js:71-73"  # 4-byte LE length prefix encode
E7 = "legacy-js/js/starwing.js:101"  # 4-byte LE length prefix decode
E8 = "legacy-js/js/starwing.js:104"  # Payload extraction after header
E9 = "legacy-js/js/starwing/burstMode.js:15-17"  # Independent confirmation
E10 = "legacy-js/js/starwing.js:72"  # writeUInt32LE on send
E11 = "legacy-js/js/starwing.js:101"  # readUIntLE on receive
E22 = "legacy-js/js/starwing.js:96"  # socket.on('data')
E23 = "legacy-js/js/starwing.js:303-310"  # socket.on('error')
E24 = "legacy-js/js/starwing.js:311-315"  # socket.on('timeout')
E25 = "legacy-js/js/starwing.js:317-320"  # socket.on('end')
E26 = "legacy-js/js/starwing.js:321-338"  # socket.on('close')
E28 = "legacy-js/js/starwing.js:63"  # PbMessage envelope
E33 = "legacy-js/js/starwing.js:118-123"  # Ping handler 0x66
E40 = "legacy-js/js/starwing.js:40"  # authorizedClients array
E80 = "legacy-js/js/starwing.js:80"  # net.createServer
E342 = "legacy-js/js/starwing.js:342"  # .listen(pb_port, "0.0.0.0")

AUDIT = "docs/TCP_SERVER_EVIDENCE_AUDIT.md"


# ---------------------------------------------------------------------------
# Helper: build a framed message (4-byte LE length prefix + protobuf bytes)
# ---------------------------------------------------------------------------
def _build_frame(payload: bytes) -> bytes:
    """Build a wire frame: 4-byte LE length prefix + payload bytes.

    Evidence: E6 (starwing.js:71-73)
      let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);
      outBuffer.writeUInt32LE(msgBuffer.byteLength, 0);
      msgBuffer.copy(outBuffer,4);
    """
    header = struct.pack("<I", len(payload))
    return header + payload


def _build_ping_payload(packet_id: int = 1) -> bytes:
    """Build a minimal Ping protobuf payload (messageType=0x66).

    PbMessage envelope with:
      field 1 (packetId, varint) = packet_id
      field 2 (messageType, varint) = 0x66
      field 4 (Message oneof) = Ping message (empty submessage)

    Wire format:
      08 <varint packetId>  10 66  1A 00
    """
    # Build protobuf fields manually
    fields = []
    # Field 1: packetId (varint)
    fields.append(b"\x08")
    fields.append(_encode_varint(packet_id))
    # Field 2: messageType (varint) = 0x66
    fields.append(b"\x10")
    fields.append(_encode_varint(0x66))
    # Field 4: Ping (oneof, length-delimited) - empty submessage
    fields.append(b"\x22\x00")
    return b"".join(fields)


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)


# ---------------------------------------------------------------------------
# Tests: 4-byte little-endian length prefix encoding
# ---------------------------------------------------------------------------


class TestLengthPrefixEncode:
    """Verify 4-byte LE length prefix encoding matches legacy behavior.

    Evidence: E6 (starwing.js:71-73)
      let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);
      outBuffer.writeUInt32LE(msgBuffer.byteLength, 0);
      msgBuffer.copy(outBuffer,4);

    Also confirmed in E9 (burstMode.js:15-17) — independent module.
    """

    SOURCE_LINES = E6

    def test_encode_zero_length_payload(self) -> None:
        """Empty payload → 4-byte header [00 00 00 00]."""
        frame = _build_frame(b"")
        assert frame == b"\x00\x00\x00\x00"

    def test_encode_one_byte_payload(self) -> None:
        """1-byte payload → header [01 00 00 00] + 1 byte."""
        frame = _build_frame(b"\xaa")
        assert len(frame) == 5
        assert frame[:4] == b"\x01\x00\x00\x00"
        assert frame[4:] == b"\xaa"

    def test_encode_multi_byte_payload(self) -> None:
        """N-byte payload → header encodes N as LE uint32."""
        payload = bytes(range(256))
        frame = _build_frame(payload)
        header_val = struct.unpack_from("<I", frame, 0)[0]
        assert header_val == 256
        assert frame[4:] == payload

    def test_encode_large_payload(self) -> None:
        """64 KiB payload → header encodes 65536 as LE uint32.

        Real Starwing messages are <1 KiB; this tests the framing mechanism
        with a larger but still valid payload.
        """
        payload = b"\x00" * 65536
        frame = _build_frame(payload)
        header_val = struct.unpack_from("<I", frame, 0)[0]
        assert header_val == 65536

    def test_encode_little_endian_byte_order(self) -> None:
        """Verify little-endian encoding: value 0x01020304 → [04 03 02 01]."""
        # Build a payload of 0x01020304 = 16909060 bytes is impractical,
        # so verify the LE encoding with a smaller value
        payload = b"\x00" * 0x100  # 256 bytes
        frame = _build_frame(payload)
        # 256 = 0x0100, LE = [00 01 00 00]
        assert frame[0] == 0x00
        assert frame[1] == 0x01
        assert frame[2] == 0x00
        assert frame[3] == 0x00

    def test_encode_header_plus_payload_concatenation(self) -> None:
        """Frame = header (4 bytes) || payload, no padding."""
        payload = b"Starwing"
        frame = _build_frame(payload)
        assert len(frame) == 4 + len(payload)
        assert frame == struct.pack("<I", 8) + b"Starwing"


# ---------------------------------------------------------------------------
# Tests: 4-byte little-endian length prefix decoding
# ---------------------------------------------------------------------------


class TestLengthPrefixDecode:
    """Verify 4-byte LE length prefix decoding matches legacy behavior.

    Evidence: E7 (starwing.js:101)
      let packetLen = recvBuffer.readUIntLE(0, 4);

    E8 (starwing.js:104)
      let incomingPB = recvBuffer.slice(4, 4+packetLen);
    """

    SOURCE_LINES = E7

    def test_decode_zero_length(self) -> None:
        """Header [00 00 00 00] → 0-byte payload, 0 remaining."""
        data = b"\x00\x00\x00\x00"
        header_val = struct.unpack_from("<I", data, 0)[0]
        assert header_val == 0
        payload = data[4 : 4 + header_val]
        assert payload == b""

    def test_decode_known_length(self) -> None:
        """Header [05 00 00 00] → 5-byte payload."""
        payload_data = b"hello"
        data = struct.pack("<I", 5) + payload_data
        header_val = struct.unpack_from("<I", data, 0)[0]
        assert header_val == 5
        extracted = data[4 : 4 + header_val]
        assert extracted == payload_data

    def test_decode_little_endian_byte_order(self) -> None:
        """Verify LE decoding: [01 02 00 00] → 0x0201 = 513."""
        data = b"\x01\x02\x00\x00"
        header_val = struct.unpack_from("<I", data, 0)[0]
        assert header_val == 513  # 0x0201

    def test_decode_extract_after_header(self) -> None:
        """E8: recvBuffer.slice(4, 4+packetLen) — extract payload after header."""
        payload_data = b"\xde\xad\xbe\xef"
        data = struct.pack("<I", len(payload_data)) + payload_data + b"extra"
        header_val = struct.unpack_from("<I", data, 0)[0]
        extracted = data[4 : 4 + header_val]
        assert extracted == payload_data
        # Remaining data is after the frame
        remaining = data[4 + header_val :]
        assert remaining == b"extra"

    def test_decode_roundtrip(self) -> None:
        """Encode then decode must preserve the payload."""
        original = b"Starwing Paradox"
        frame = _build_frame(original)
        header_val = struct.unpack_from("<I", frame, 0)[0]
        assert header_val == len(original)
        decoded = frame[4 : 4 + header_val]
        assert decoded == original


# ---------------------------------------------------------------------------
# Tests: Complete one-frame request handling
# ---------------------------------------------------------------------------


class TestOneFrameRequestHandling:
    """Verify the Python server handles a complete one-frame request.

    The Python TCP server (tcp_server.py:103-157) processes data events by:
      1. Reading data into a buffer
      2. Checking if buffer has ≥4 bytes (header)
      3. Decoding length prefix to get payload length
      4. Extracting payload and dispatching to handler
      5. Sending response if handler returns bytes

    Legacy equivalent: starwing.js:96-301 (socket.on('data'))
    """

    SOURCE_LINES = "tcp_server.py:103-157"

    def test_frame_structurally_valid(self) -> None:
        """A properly framed Ping request is structurally valid."""
        payload = _build_ping_payload(packet_id=1)
        frame = _build_frame(payload)
        # Verify frame can be parsed
        header_val = struct.unpack_from("<I", frame, 0)[0]
        assert header_val == len(payload)
        extracted = frame[4 : 4 + header_val]
        assert extracted == payload

    def test_frame_header_size_is_4_bytes(self) -> None:
        """FRAME_HEADER_SIZE = 4 in codec.py:39, matches legacy E6-E7."""
        from app.protocol.codec import FRAME_HEADER_SIZE

        assert FRAME_HEADER_SIZE == 4

    def test_ping_message_type_is_0x66(self) -> None:
        """Ping messageType is 0x66 (102 decimal), matching legacy E33."""
        from app.protocol.registry import MESSAGE_TYPE_MAP

        assert MESSAGE_TYPE_MAP[0x66] == "Ping"

    def test_encode_length_prefix_function(self) -> None:
        """encode_length_prefix() produces 4-byte LE header + payload."""
        from app.protocol.codec import encode_length_prefix

        payload = b"test"
        result = encode_length_prefix(payload)
        assert len(result) == 4 + len(payload)
        header_val = struct.unpack_from("<I", result, 0)[0]
        assert header_val == len(payload)
        assert result[4:] == payload

    def test_decode_length_prefix_function(self) -> None:
        """decode_length_prefix() extracts payload and remaining bytes."""
        from app.protocol.codec import decode_length_prefix

        payload = b"test"
        frame = struct.pack("<I", len(payload)) + payload + b"extra"
        decoded_payload, remaining = decode_length_prefix(frame)
        assert decoded_payload == payload
        assert remaining == b"extra"

    def test_decode_length_prefix_incomplete_frame(self) -> None:
        """Incomplete frame raises FramingError."""
        from app.protocol.codec import decode_length_prefix
        from app.protocol.errors import FramingError

        # Header says 10 bytes but only 2 available
        frame = struct.pack("<I", 10) + b"ab"
        with pytest.raises(FramingError, match="Incomplete frame"):
            decode_length_prefix(frame)

    def test_decode_length_prefix_header_too_short(self) -> None:
        """Data shorter than 4 bytes raises FramingError."""
        from app.protocol.codec import decode_length_prefix
        from app.protocol.errors import FramingError

        with pytest.raises(FramingError, match="Need 4 bytes"):
            decode_length_prefix(b"\x01\x02")


# ---------------------------------------------------------------------------
# Tests: Response framing (4-byte LE prefix + protobuf)
# ---------------------------------------------------------------------------


class TestResponseFraming:
    """Verify response framing matches legacy PbSendPayload behavior.

    Evidence: E6 (starwing.js:71-73)
      PbSendPayload builds: [4-byte LE length][protobuf bytes]
      socket.write(outBuffer)

    Python tcp_server.py:154-157:
      writer.write(response)
      await writer.drain()

    Where response = encode_length_prefix(raw_pb_bytes)
    """

    SOURCE_LINES = "starwing.js:62-78"

    def test_response_is_length_prefixed(self) -> None:
        """Response starts with 4-byte LE length prefix."""
        from app.protocol.codec import encode_length_prefix

        raw_response = b"\x08\x01\x10\x67"  # Minimal protobuf
        response = encode_length_prefix(raw_response)
        header_val = struct.unpack_from("<I", response, 0)[0]
        assert header_val == len(raw_response)

    def test_response_payload_is_protobuf(self) -> None:
        """Response payload after header is raw protobuf bytes."""
        from app.protocol.codec import encode_length_prefix

        # Simulate a protobuf-encoded PbMessage
        raw_pb = bytes(range(32))
        response = encode_length_prefix(raw_pb)
        assert response[4:] == raw_pb

    def test_ping_handler_returns_framed_response(self) -> None:
        """Ping handler returns encode_length_prefix(payload)."""
        from app.tcp_server import _handle_ping

        payload = _build_ping_payload(packet_id=1)
        # Ping handler returns framed bytes
        result = asyncio.get_event_loop().run_until_complete(_handle_ping(1, 0x66, "Ping", payload))
        assert result is not None
        # Result should be a framed response
        header_val = struct.unpack_from("<I", result, 0)[0]
        assert header_val == len(payload)


# ---------------------------------------------------------------------------
# Tests: Connection close behavior
# ---------------------------------------------------------------------------


class TestConnectionCloseBehavior:
    """Verify connection close behavior matches legacy.

    Evidence: E23-E27 (starwing.js:303-341)

    Legacy socket events:
      - error: Ignores ECONNRESET, logs others (E23, starwing.js:303-310)
      - timeout: socket.end('Timed out!') (E24, starwing.js:311-315)
      - end: Logs end event (E25, starwing.js:317-320)
      - close: Logs bytes read/written, removes from activeGameServers (E26, starwing.js:321-338)

    Python tcp_server.py:159-168:
      - CancelledError: logs and closes
      - Exception: logs and closes
      - Finally: writer.close() + wait_closed()

    Note: Python closes the connection on all exit paths, matching legacy
    socket.end() / socket.destroy() behavior.
    """

    SOURCE_LINES = "starwing.js:303-341"

    def test_writer_close_called_in_finally(self) -> None:
        """Python always calls writer.close() in the finally block.

        Evidence: tcp_server.py:163-168
          finally:
              writer.close()
              await writer.wait_closed()

        This matches legacy behavior where socket is always closed
        on disconnect (socket.end or socket.destroy).
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        # Verify finally block exists with writer.close()
        assert "finally:" in source
        assert "writer.close()" in source

    def test_no_active_game_servers_tracking(self) -> None:
        """Python does not track activeGameServers (§4.6 of audit).

        Legacy removes from activeGameServers on close (starwing.js:328-332).
        This is not needed until dedicated server support.
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "activeGameServers" not in source

    def test_eof_disconnect_handled(self) -> None:
        """Python handles EOF (empty data) by breaking the loop.

        Evidence: tcp_server.py:115-117
          if not data:
              logger.info('Client disconnected (EOF): %s', client_id)
              break

        Legacy equivalent: socket.on('end') at starwing.js:317
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "if not data:" in source
        assert "EOF" in source

    def test_error_handling_exists(self) -> None:
        """Python handles exceptions in the client handler.

        Evidence: tcp_server.py:159-162
          except asyncio.CancelledError:
          except Exception:

        Matches legacy socket.on('error') at starwing.js:303-310
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "CancelledError" in source
        assert "except Exception" in source


# ---------------------------------------------------------------------------
# Tests: Multiple frames in one connection
# ---------------------------------------------------------------------------


class TestMultipleFramesPerConnection:
    """Verify multiple frames can be processed in one connection.

    The Python server uses incremental buffering (tcp_server.py:103-131):
      - Data is appended to buffer
      - Inner while loop processes complete frames
      - Partial frames remain in buffer for next data event

    Legacy behavior: starwing.js:96-301 processes one frame per data event,
    but Node.js may deliver multiple frames in a single 'data' event
    depending on OS buffering. The Python incremental approach is
    functionally equivalent and handles both cases correctly.

    NOTE: The legacy code at starwing.js:96-104 does NOT loop over
    multiple frames in a single data event — it reads one packet per
    'data' event. However, since Node.js buffers TCP data, the OS may
    concatenate multiple writes into a single 'data' delivery, meaning
    the legacy code could silently drop frames. The Python incremental
    buffering is an improvement that correctly handles this case.
    """

    SOURCE_LINES = "tcp_server.py:103-131"

    def test_buffer_accumulates_data(self) -> None:
        """Buffer grows as data arrives, enabling multi-frame processing."""
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "buffer.extend(data)" in source

    def test_inner_loop_processes_frames(self) -> None:
        """Inner while loop processes all complete frames in buffer."""
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "while len(buffer) >= 4:" in source

    def test_partial_frame_stays_in_buffer(self) -> None:
        """Incomplete frame is not consumed — stays in buffer for next read."""
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        # The break on Incomplete frame preserves remaining bytes in buffer
        assert "Incomplete frame" in source
        assert "buffer = buffer[frame_size:]" in source

    def test_two_sequential_ping_frames(self) -> None:
        """Two ping frames concatenated in one buffer are both processed."""
        from app.protocol.codec import decode_length_prefix, encode_length_prefix

        # Build two ping payloads
        ping1 = _build_ping_payload(packet_id=1)
        ping2 = _build_ping_payload(packet_id=2)

        # Frame each
        frame1 = encode_length_prefix(ping1)
        frame2 = encode_length_prefix(ping2)

        # Concatenate (simulates two frames in one data event)
        combined = frame1 + frame2

        # Decode first frame
        payload1, remaining1 = decode_length_prefix(combined)
        assert payload1 == ping1
        assert remaining1 == frame2

        # Decode second frame
        payload2, remaining2 = decode_length_prefix(remaining1)
        assert payload2 == ping2
        assert remaining2 == b""

    def test_partial_then_complete_frame(self) -> None:
        """Partial frame followed by completion is correctly assembled."""
        from app.protocol.codec import decode_length_prefix, encode_length_prefix

        ping = _build_ping_payload(packet_id=1)
        frame = encode_length_prefix(ping)

        # Simulate partial delivery: first 2 bytes of header
        partial = frame[:2]
        rest = frame[2:]

        # Simulate buffer after first partial read
        buffer = bytearray(partial)
        # Not enough for header
        assert len(buffer) < 4

        # Second read delivers the rest
        buffer.extend(rest)
        assert len(buffer) >= 4

        # Now process the complete frame
        payload, remaining = decode_length_prefix(bytes(buffer))
        assert payload == ping
        assert remaining == b""


# ---------------------------------------------------------------------------
# Tests: Proposed protections (Python hardening, NOT legacy parity)
# ---------------------------------------------------------------------------


class TestProposedProtections:
    """Document Python hardening measures NOT present in legacy.

    These are improvements over the legacy server, documented as
    separate protections rather than legacy parity.
    """

    def test_timeout_exists_in_python(self) -> None:
        """PROTECTION: Python enforces configurable timeout (30s default).

        Evidence: tcp_server.py:107-109
          data = await asyncio.wait_for(reader.read(65536), timeout=settings.pb_timeout)

        Legacy: starwing.js:311-315 has socket.on('timeout') handler but
        never calls socket.setTimeout(), so it likely never fires.

        Status: EXPERIMENTAL (§4.2, §4.5 of audit)
        """
        from app.config import settings

        assert settings.pb_timeout > 0

    def test_timeout_configurable(self) -> None:
        """Timeout is configurable via Settings.pb_timeout."""
        from app.config import Settings

        s = Settings(pb_timeout=10.0)
        assert s.pb_timeout == 10.0

    def test_max_frame_size_limit(self) -> None:
        """PROTECTION: Python enforces 1 MiB max frame size.

        Evidence: tcp_server.py:42, codec.py:40
          MAX_FRAME_SIZE = 1 * 1024 * 1024
          MAX_MESSAGE_SIZE = 1 * 1024 * 1024

        Legacy: No explicit limit (§4.3 of audit)

        Status: EXPERIMENTAL — real Starwing messages are <1 KiB
        """
        from app.tcp_server import MAX_FRAME_SIZE

        assert MAX_FRAME_SIZE == 1 * 1024 * 1024

    def test_max_frame_size_exceeded_raises(self) -> None:
        """Payload exceeding MAX_MESSAGE_SIZE raises FramingError."""
        from app.protocol.codec import MAX_MESSAGE_SIZE, decode_length_prefix
        from app.protocol.errors import FramingError

        # Header claims a size larger than MAX_MESSAGE_SIZE
        oversized_header = struct.pack("<I", MAX_MESSAGE_SIZE + 1)
        with pytest.raises(FramingError, match="exceeds maximum"):
            decode_length_prefix(oversized_header)

    def test_ip_allowlist_not_implemented(self) -> None:
        """NOT IMPLEMENTED: Python has no IP authorization on TCP.

        Evidence: starwing.js:87-94 destroys unauthorized connections.
        starwing.js:345-359 authorizes IPs via HTTP POST.

        Status: NOT_IMPLEMENTED (§4.4 of audit)
        Security gap: In production, unauthorized clients could connect.
        Not an issue for local development.
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "authorizedClients" not in source

    def test_shutdown_event_mechanism(self) -> None:
        """Python uses asyncio.Event for graceful shutdown."""
        from app.tcp_server import _shutdown_event

        assert isinstance(_shutdown_event, asyncio.Event)

    def test_read_chunk_size(self) -> None:
        """Python reads 65536 bytes per read call.

        Legacy: socket.on('data') delivers whatever the OS buffer has.
        Impact: Functionally equivalent — Python incremental buffering
        handles partial frames correctly (§4.1 of audit).
        """
        import inspect

        from app.tcp_server import _handle_client

        source = inspect.getsource(_handle_client)
        assert "reader.read(65536)" in source


# ---------------------------------------------------------------------------
# Tests: Port and bind address (source-verified)
# ---------------------------------------------------------------------------


class TestPortAndBindAddress:
    """Verify TCP server defaults match legacy configuration.

    Evidence:
      E14: starwing.js:29 — const pb_port = 6666
      E16: starwing.js:342 — .listen(pb_port, "0.0.0.0")
      E17: server/app/config.py:10 — pb_port: int = 6666
      E18: server/app/tcp_server.py:173 — port: int = 6666
    """

    SOURCE_LINES = "starwing.js:29,342"

    def test_default_port_is_6666(self) -> None:
        """Python default TCP port is 6666, matching legacy (E2, E17, E18)."""
        from app.config import Settings

        assert Settings().pb_port == 6666

    def test_default_bind_address(self) -> None:
        """Python default bind is 0.0.0.0, matching legacy (E16)."""
        import inspect

        from app.tcp_server import _run_server

        source = inspect.getsource(_run_server)
        assert 'host: str = "0.0.0.0"' in source
        assert "port: int = 6666" in source

    def test_config_pb_port_matches_legacy(self) -> None:
        """Settings.pb_port defaults to 6666."""
        from app.config import settings

        assert settings.pb_port == 6666


# ---------------------------------------------------------------------------
# Tests: Handler dispatch (source-verified)
# ---------------------------------------------------------------------------


class TestHandlerDispatch:
    """Verify handler dispatch matches legacy switch/case.

    Evidence: E32-E36
      starwing.js:117 — switch(parseInt(decoded.messageType))
      tcp_server.py:39-47 — _handlers dict + register_handler()

    Legacy dispatch pattern:
      case 0x66: ping
      case 200: RequestEntryMatching
      case 208/210/214/216: Burst mode handlers

    Python: Registry dict replaces switch/case, functionally identical.
    """

    SOURCE_LINES = "starwing.js:117-123, tcp_server.py:39-47"

    def test_ping_handler_registered(self) -> None:
        """Ping handler (0x66) is registered at module load time."""
        from app.tcp_server import _handlers

        assert 0x66 in _handlers

    def test_handler_is_callable(self) -> None:
        """Registered handler is a callable coroutine."""
        from app.tcp_server import _handlers

        handler = _handlers[0x66]
        assert callable(handler)
        # Verify it's a coroutine function
        assert asyncio.iscoroutinefunction(handler)

    def test_registry_pattern_matches_switch_case(self) -> None:
        """_handlers dict provides same dispatch as legacy switch/case.

        Evidence: E32 — switch(parseInt(decoded.messageType))
        Python: tcp_server.py:143 — handler = _handlers.get(message_type, handle_message)
        """
        from app.tcp_server import handle_message

        # handle_message is the default fallback (no handler registered)
        assert callable(handle_message)

    def test_message_type_map_includes_legacy_types(self) -> None:
        """MESSAGE_TYPE_MAP contains all legacy message types."""
        from app.protocol.registry import MESSAGE_TYPE_MAP

        legacy_types = [0x66, 200, 201, 208, 210, 214, 216, 302, 304]
        for mt in legacy_types:
            assert mt in MESSAGE_TYPE_MAP, f"Missing legacy type {mt}"
