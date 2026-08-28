# GAME_SIDE_PIPE_PROTOCOL

## Status

**Classification:** PARTIAL_EVIDENCE

## Summary

The game executable references the NESYS named pipe `\\.\pipe\nesys_games` and imports both
client-side and server-side named-pipe functions. The exact message format, command IDs, and
role (server vs client) are NOT yet resolved.

## Evidence

| Evidence | Type | Location | Confidence |
|----------|------|----------|------------|
| `\\.\pipe\` | string | AcrGame-Win64-Shipping.exe | HIGH |
| `nesys_games` | string | AcrGame-Win64-Shipping.exe | HIGH |
| `ConnectNamedPipe` | import | KERNEL32.dll | HIGH (server-side fn) |
| `DisconnectNamedPipe` | import | KERNEL32.dll | HIGH |
| `SetNamedPipeHandleState` | import | KERNEL32.dll | HIGH |
| `PeekNamedPipe` | import | KERNEL32.dll | HIGH |
| `WaitNamedPipeA` | import | KERNEL32.dll | HIGH |
| `ReadFile` / `WriteFile` | import | KERNEL32.dll | HIGH |

## Role Analysis

- `ConnectNamedPipe` is a **server-side** function. Its presence suggests the game may act as a
  **pipe SERVER** (waiting for a client, e.g. NesysService, to connect), which contradicts the
  earlier assumption that the game is a pipe client.
- Alternatively, the game may link both client and server pipe functions.
- **Resolution required via control-flow analysis** (not resolvable from imports alone).

## GALAXYIO Relationship

- GALAXYIO.dll uses **WinHTTP + WINUSB**, NOT named pipes.
- GALAXYIO handles card HTTP (cert validation, AMIC endpoint) and USB I/O.
- The named pipe is therefore a separate NESYS-service IPC channel, not GALAXYIO.

## Framing (from prior G8/G17)

| Property | Value | Confidence |
|----------|-------|------------|
| 4-byte minimum | PROTOCOL_CONFIRMED | HIGH |
| Identifier width | HIGH_CONFIDENCE | HIGH |
| Byte order | LITTLE_ENDIAN | CONFIRMED (x86_64) |
| Payload start offset | UNKNOWN | LOW |

## Unknowns

- Exact pipe message format
- Command IDs and payload structures
- Synchronous vs overlapped I/O
- Pipe mode (byte vs message)
- Buffer sizes
- Timeout values
- Reconnection behavior

## Implementation Recommendation

- **Approach:** Game -> minimal local compatibility adapter -> Python private server.
- **Adapter surface (proposed, NOT implemented in G19):** named pipe handling for
  `\\.\pipe\nesys_games`, minimal command handling, HTTP proxy to the private server.
- **Constraint:** G19 implements NO live named-pipe server. This proposal is architecture-only.

## References

- `artifacts/phase_2a_g19/game_pipe_contract.json`
- `artifacts/phase_2a_g19/network_endpoint_classification.json`
