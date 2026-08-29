# G32 Ping Contract

## Ping Request

- **Message Type:** 102 (0x66)
- **Message Name:** Ping
- **Frame Length:** 17 bytes
- **Packet ID:** Odd numbers (1, 3, 5, 7, ...)
- **Session ID:** 0

## Ping Response

- **Message Type:** 102 (0x66)
- **Message Name:** Ping
- **Frame Length:** 17 bytes
- **Packet ID:** Same as request

## PingResponse (from game)

- **Message Type:** 103 (0x67)
- **Frame Length:** 19 bytes
- **Sent after:** Receiving server Ping

## Behavior

1. Game sends Ping every ~20 seconds
2. Server responds with Ping echo
3. Game sends PingResponse (0x67)
4. Game logs: `OnDecode_Ping: PingId:<id>`

## Decode Error

```
PbMessage has no Message oneof set
```

This error occurs when the server's Ping response doesn't set the Message oneof field. The game still accepts the response (connection remains open).

## Classification

**PING_ECHO_CONFIRMED**
