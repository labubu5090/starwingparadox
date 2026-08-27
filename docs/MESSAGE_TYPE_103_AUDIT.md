# Message Type 103 (0x67) Audit

## Date: 2026-08-28

## Classification: CAPTURE_SEQUENCE_CANDIDATE

**NOT PROVEN_PING_RESPONSE** — classified as candidate based on capture sequence and legacy JS evidence.

---

## 1. Evidence Sources

### 1.1 Legacy JavaScript (starwing.js:118-123)

```javascript
case 0x66: // ping!
    console.log("Processing message 0x66 (ping), TS:" + decoded.Ping.unixTimestamp);
    // reply!
    payload = { packetId: decoded.packetId, messageType: 0x67, Ping: { unixTimestamp: parseInt(Date.now()/1000)} };
    PbSendPayload(socket,payload);
    break;
```

**Interpretation**: When the client receives messageType 0x66 (Ping) from the server, it replies with messageType 0x67 containing a Ping with unixTimestamp.

### 1.2 Proto Definition (starwingMessage.proto)

```protobuf
message PbMessage {
    int64 packetId = 1;
    int64 messageType = 2;
    optional int64 sessionId = 3;
    oneof Message {
         Ping Ping = 0x66;
         // ... no separate PingResponse message type defined
    }
}

message Ping {
    int64 unixTimestamp = 1;
}
```

**Observation**: The proto defines Ping at oneof field 0x66. There is no separate PingResponse message type in the proto. The 0x67 value appears only in the legacy JS client code as a response direction.

### 1.3 Captured Sequence

| Run | Step | messageType | Direction | Source |
|-----|------|-------------|-----------|--------|
| A | 1 | 0x66 (Ping) | Game → Server | Game log + TCP server log |
| A | 2 | 0x66 (Ping) | Server → Game | TCP server echo |
| A | 3 | 0x67 (103) | Game → Server | TCP server log |
| B | 1 | 0x66 (Ping) | Game → Server | Game log |
| B | 2 | 0x66 (Ping) | Server → Game | TCP server echo |
| B | 3 | 0x67 (103) | Game → Server | TCP server log |

### 1.4 Raw Payload (from TCP server log)

- messageType: 103 (0x67)
- packetId: 169 (same as the Ping it responds to)
- Payload: Ping with unixTimestamp

---

## 2. Analysis

### 2.1 Direction

messageType 0x67 flows **from game to server** in response to receiving messageType 0x66 from the server. This matches the legacy JS pattern where the client replies to a server-initiated Ping.

### 2.2 PacketId Correlation

The game sends messageType 0x67 with the same packetId as the messageType 0x66 it received. This confirms it's a response to the Ping, not an independent message.

### 2.3 Proto Gap

The proto file does not define a PingResponse message type. The 0x67 value exists only in the legacy JS client code. This means:
- The proto is incomplete (missing the response direction)
- Or the response is implicit (server doesn't need to parse it)

### 2.4 No Server Response Required

The legacy JS client sends 0x67 and does not expect a response. The server handler for 0x67 should return None (no response).

---

## 3. Implementation Status

### Current Handler

```python
async def _handle_ping_response(
    packet_id: int,
    message_type: int,
    message_name: str,
    payload: bytes,
) -> bytes | None:
    """Handle PingResponse (0x67 / 103)."""
    logger.info("PingResponse received: packetId=%d", packet_id)
    return None  # No response needed
```

### Registry Entry

```python
MESSAGE_TYPE_MAP = {
    0x67: "PingResponse",
    # ...
}
```

---

## 4. Classification Justification

| Criterion | Evidence | Confidence |
|-----------|----------|------------|
| Follows 0x66 in sequence | Captured in both runs | HIGH |
| Legacy JS shows 0x67 as reply to 0x66 | starwing.js:121 | HIGH |
| Same packetId as 0x66 | Captured in TCP server log | HIGH |
| No response expected | Legacy JS doesn't wait for response | MEDIUM |
| Proto has no separate message | starwingMessage.proto | MEDIUM |
| Only 1 capture of each direction | Limited data | LOW |

**Overall classification**: CAPTURE_SEQUENCE_CANDIDATE

**Rationale**: The evidence strongly suggests 0x67 is a PingResponse, but we have only one capture sequence. The proto doesn't define it separately. The legacy JS code is the primary source for the "response" interpretation.

---

## 5. What Would Confirm Classification

1. Multiple capture sequences showing the same 0x66 → 0x67 pattern
2. A server-initiated Ping (0x66) followed by client PingResponse (0x67) with matching packetId
3. Raw payload analysis showing Ping.unixTimestamp field populated
4. Legacy JS code showing the server handling 0x67 (not just the client sending it)

---

## 6. Current Status

- Handler implemented: YES (returns None)
- Registry entry: YES (0x67: "PingResponse")
- Tests passing: YES
- Classification: CAPTURE_SEQUENCE_CANDIDATE
- NOT classified as: PROVEN_PING_RESPONSE
