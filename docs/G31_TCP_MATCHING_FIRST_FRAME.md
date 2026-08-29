# G31 TCP Matching First Frame

## Connection Chain Proven

```
Game accepts matching discovery response
  -> game attempts 127.0.0.1:6666
  -> Python TCP listener accepts connection
  -> first client frame received
  -> Ping (0x66) identified
  -> server responds with Ping
  -> game accepts response
  -> TCP communication working
```

## Evidence

| Step | Timestamp | Evidence |
|------|-----------|----------|
| Game connects | 12:15:40.478 | `ACCEPT #1 client=127.0.0.1:42854` |
| First frame | 12:15:40.570 | `RECV #1 packetId=1 messageType=102 (0x66) name=Ping` |
| Server responds | 12:15:40.570 | `SEND #1 bytes=17` |
| Game sends Ping | 12:15:53.352 | `RECV #1 packetId=3 messageType=102 (0x66) name=Ping` |
| Tick report | 12:17:10.803 | `TickCount[120] ErrorCount[0] ReportSendCount[2]` |

## First Frame Metadata

- **Message Type:** 102 (0x66) = Ping
- **Packet ID:** 1
- **Frame Length:** 17 bytes
- **Server Response:** 17 bytes (Ping echo)
- **Decode Error:** "PbMessage has no Message oneof set" (PingResponse from game)

## Next Boundary

```
Error No MatchingServer so initialize Nesys before.
```

The game requires NESYS initialization before proceeding to matching entry.

## Classification

**TCP_MATCHING_FIRST_FRAME_CAPTURED**
