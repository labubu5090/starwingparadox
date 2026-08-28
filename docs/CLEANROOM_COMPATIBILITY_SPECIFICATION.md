# Clean-room Compatibility Specification

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: G

## Overview

This specification defines a clean-room compatibility boundary for the Python implementation. It separates observed interface behavior from proprietary implementation and establishes explicit authorization and safety boundaries.

## Design Principles

1. **Transport abstraction**: Do not bind to original production pipe
2. **Offline-first**: No outbound network dependency by default
3. **Synthetic-only**: No production credentials or certificates
4. **Fail-closed**: Default to failure on unknown behavior
5. **Test-first**: Deterministic parsers, pure state machines
6. **No Windows mutation**: No service, registry, or certificate operations

## Architecture

### Transport Layer

```python
class Transport:
    """Abstract transport interface for named pipe communication."""
    
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send(self, data: bytes) -> None: ...
    async def receive(self) -> bytes: ...
    async def is_connected(self) -> bool: ...
```

**Implementations:**
- `SyntheticTransport`: In-memory transport for testing
- `FileTransport`: File-based transport for replay testing
- `PipeTransport`: Named pipe transport (future, requires explicit authorization)

### Session State

```python
class SessionState:
    """Tracks connection lifecycle state."""
    
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
```

**State transitions:**
- DISCONNECTED → CONNECTING → CONNECTED → STARTED → STOPPING → STOPPED
- Any state → DISCONNECTED (on error or timeout)

### Command Decoder

```python
class CommandDecoder:
    """Decodes incoming command frames."""
    
    def decode(self, data: bytes) -> Command: ...
    def decode_length_prefix(self, data: bytes) -> tuple[int, bytes]: ...
    def decode_varint(self, data: bytes) -> tuple[int, bytes]: ...
```

**Behavior:**
- Extract 4-byte LE length prefix
- Decode protobuf message
- Extract packet_id, message_type, payload
- Return Command object

### Command Encoder

```python
class CommandEncoder:
    """Encodes outgoing command frames."""
    
    def encode(self, command: Command) -> bytes: ...
    def encode_length_prefix(self, payload: bytes) -> bytes: ...
```

**Behavior:**
- Encode protobuf message
- Prepend 4-byte LE length prefix
- Return framed bytes

### Request Dispatcher

```python
class RequestDispatcher:
    """Dispatches commands to registered handlers."""
    
    def register(self, message_type: int, handler: Callable) -> None: ...
    async def dispatch(self, command: Command) -> Optional[Command]: ...
```

**Behavior:**
- Lookup handler by message_type
- Call handler with command
- Return response command or None
- Log unknown message types

### Compatibility Adapter

```python
class CompatibilityAdapter:
    """Adapts Python server to original protocol."""
    
    def __init__(self, transport: Transport, dispatcher: RequestDispatcher): ...
    async def handle_client_start(self, command: Command) -> Command: ...
    async def handle_client_end(self, command: Command) -> None: ...
    async def handle_ping(self, command: Command) -> Command: ...
    async def handle_card_read(self, command: Command) -> Command: ...
    async def handle_card_write(self, command: Command) -> Command: ...
    async def handle_card_check(self, command: Command) -> Command: ...
    async def handle_news_request(self, command: Command) -> Command: ...
    async def handle_event_request(self, command: Command) -> Command: ...
    async def handle_log_upload(self, command: Command) -> Command: ...
    async def handle_match_request(self, command: Command) -> Command: ...
    async def handle_match_cancel(self, command: Command) -> Command: ...
    async def handle_burst_group_join(self, command: Command) -> Command: ...
    async def handle_burst_group_leave(self, command: Command) -> Command: ...
```

**Behavior:**
- Implement confirmed interface behaviors
- Return synthetic responses for unknown behaviors
- Log all operations for debugging
- Fail closed on unknown commands

### Synthetic Test Transport

```python
class SyntheticTestTransport:
    """In-memory transport for testing."""
    
    def __init__(self): ...
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send(self, data: bytes) -> None: ...
    async def receive(self) -> bytes: ...
    async def is_connected(self) -> bool: ...
    def get_sent_data(self) -> list[bytes]: ...
    def inject_receive(self, data: bytes) -> None: ...
```

**Behavior:**
- In-memory buffer for sent/received data
- Configurable injection of receive data
- No network or pipe operations
- Deterministic behavior for testing

## Command Catalog

### Confirmed Commands

| Command | Type ID | Direction | Payload | Response | Behavior |
|---------|---------|-----------|---------|----------|----------|
| CLIENT_START | -- | Game→Service | None | CLIENT_START_REPLY | Acknowledge connection |
| CLIENT_END | -- | Game→Service | None | None | Acknowledge disconnection |
| PING | 0x66 | Game→Service | None | PING_RESPONSE (0x67) | Acknowledge keepalive |
| CERT_ERROR | -- | Service→Game | None | None | Report certificate error |
| NW_ERROR | -- | Service→Game | None | None | Report network error |
| NWRECOVER_NOTICE | -- | Service→Game | None | None | Report network recovery |

### Protocol-Identified Commands

| Command | Direction | Payload | Response | Behavior |
|---------|-----------|---------|----------|----------|
| CARD_READ | Game→Service | Card operation | CARD_DATA | Synthetic card data |
| CARD_WRITE | Game→Service | Card operation | CARD_RESULT | Synthetic result |
| CARD_CHECK | Game→Service | Card operation | CARD_STATUS | Synthetic status |
| NEWS_REQUEST | Game→Service | None | NEWS_DATA | Synthetic news |
| EVENT_REQUEST | Game→Service | None | EVENT_DATA | Synthetic events |
| LOG_UPLOAD | Game→Service | Log data | LOG_RESULT | Acknowledge |
| MATCH_REQUEST | Game→Service | Match criteria | MATCH_RESPONSE | Not implemented |
| MATCH_CANCEL | Game→Service | None | MATCH_CANCEL_ACK | Not implemented |
| BURST_GROUP_JOIN | Game→Service | Group criteria | BURST_GROUP_JOIN_ACK | Not implemented |
| BURST_GROUP_LEAVE | Game→Service | None | BURST_GROUP_LEAVE_ACK | Not implemented |

## State Machine

### Connection Lifecycle

```
DISCONNECTED
    ↓ (client connects)
CONNECTING
    ↓ (transport connected)
CONNECTED
    ↓ (LCOMMAND_CLIENT_START received)
STARTED
    ↓ (LCOMMAND_CLIENT_END received or timeout)
STOPPING
    ↓ (cleanup complete)
STOPPED
    ↓ (transport disconnected)
DISCONNECTED
```

### Error Handling

```
Any State
    ↓ (error occurred)
ERROR
    ↓ (send SCOMMAND_CERT_ERROR or SCOMMAND_NW_ERROR)
ERROR_REPORTED
    ↓ (cleanup)
DISCONNECTED
```

## Validation Rules

1. **Frame length**: Must be >= 4 bytes (length prefix)
2. **Message type**: Must be registered in MESSAGE_TYPE_MAP
3. **Packet ID**: Must be present and non-negative
4. **Session ID**: Optional, but must be consistent within connection
5. **Payload**: Must match expected structure for message type
6. **Ordering**: CLIENT_START must be first, CLIENT_END must be last
7. **Timeout**: Connection must receive data within configurable timeout

## Error Handling

| Error | Behavior | Response |
|-------|----------|----------|
| Invalid frame length | Drop connection | None |
| Unknown message type | Log and drop | None |
| Invalid payload | Log and drop | None |
| Timeout | Disconnect | None |
| Transport error | Disconnect | None |
| Certificate error | Report | SCOMMAND_CERT_ERROR |
| Network error | Report | SCOMMAND_NW_ERROR |

## Lifecycle

### Server Startup

1. Create transport
2. Create decoder/encoder
3. Create dispatcher
4. Register handlers
5. Start accept loop

### Client Connection

1. Accept transport connection
2. Create session state
3. Wait for CLIENT_START
4. Send CLIENT_START_REPLY
5. Enter command loop
6. Handle CLIENT_END or timeout
7. Cleanup and disconnect

### Command Processing

1. Receive data from transport
2. Decode frame
3. Validate message
4. Dispatch to handler
5. Encode response
6. Send response to transport

---

## G19 Update: Game-Client Contract Mapping

**Date**: 2026-08-29
**Phase**: 2A-G19
**Classification**: GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

### Impact of Game-Client Static Analysis on the Clean-room Boundary

G19 mapped the game client's actual network contracts (HTTP via WININET, raw TCP via WS2_32,
and a local NESYS named pipe `\\.\pipe\nesys_games`). Key consequences for this specification:

1. **Transport abstraction is validated**: The game uses multiple independent transports, so the
   clean-room `Transport` abstraction remains the correct seam. No production pipe transport is
   authorized without explicit, evidence-backed approval.

2. **Pipe role is UNRESOLVED**: The game imports both client (`WaitNamedPipeA`) and server
   (`ConnectNamedPipe`) pipe functions. This specification's `PipeTransport` remains future and
   must NOT be implemented until the game's pipe role and message format are resolved by
   control-flow evidence.

3. **91-command registry preserved**: Confirmed/high (8), protocol-identified/medium (20),
   unknown (63) = 91. Certificate/error commands remain OPAQUE; no automatic FAILED/recovery
   transition may be inferred without control-flow proof.

4. **No supported endpoint override**: The game hardcodes `http://dev.starwing.jp/mock` (port 80)
   with no game-side override. Any integration operates at the operator network/TLS/DNS/proxy
   boundary, consistent with the two-tier (Option A) architecture.

5. **Synthetic foundation remains intact**: The clean-room codec, timeout model, scenario
   harness, and safety guards are unchanged by G19 analysis. G19 produced documentation and
   artifacts only (plus two narrow unused-import fixes in G18 test files).

### Updated Validation Rules Note

Rule 5 (payload must match expected structure) and the timeout model remain synthetic until the
game-side HTTP JSON and TCP protobuf payload structures are confirmed by capture. G20 is the
planned phase for that confirmation.

