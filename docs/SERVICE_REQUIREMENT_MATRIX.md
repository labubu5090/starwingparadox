# SERVICE_REQUIREMENT_MATRIX

## Status

**Classification:** PARTIAL_GAME_CLIENT_CONTRACT

## Services

### NESYS Service (NesysService.exe)
**Necessity:** MINIMAL_LOCAL_ADAPTER_MAY_BE_REQUIRED.
- Evidence: `\\.\pipe\nesys_games`, pipe primitives, card/control functions.
- Decision: Do NOT rebuild full NesysService. Minimal local adapter only where game
  demonstrably requires local IPC, after pipe-role resolution.
- Commands (CLIENT_START, CLIENT_END, PING, PING_RESPONSE, CERT_ERROR, NW_ERROR,
  NWRECOVER_NOTICE): all UNKNOWN/LOW from game side. CERT_ERROR/NW_ERROR/NWRECOVER_NOTICE
  treated as OPAQUE — no automatic FAILED/recovery without control-flow proof.

### Game Server (HTTP)
**Necessity:** DIRECT_SERVER_PROTOCOL.
- Evidence: WININET imports, Bind* endpoints, `https://log.starwing.jp/acr/public/`.
- Decision: Python server provides the HTTP endpoints the game calls directly. Priority HIGH.

### Matching Server (TCP)
**Necessity:** DIRECT_SERVER_PROTOCOL.
- Evidence: WS2_32 socket imports, `[Client->Gameserver]EntryMatching` etc., `CPP_TestTCP.cpp`.
- Decision: Python server provides a TCP endpoint for matching/battle, protocol confirmed from game side. Priority MEDIUM.

### Production services (event agents, update agents, crash reporters, monitoring)
**Necessity:** NOT_REQUIRED_BY_CURRENT_EVIDENCE. Do not implement. EXCLUDED.

### Certificate provisioning / production authentication
**Necessity:** PRODUCTION_TRUST_DEPENDENCY (production cert trust + AMIC card). EXCLUDED.

## Frame Reconciliation

- 4-byte minimum: PROTOCOL_CONFIRMED.
- Identifier width: HIGH_CONFIDENCE.
- Byte order: LITTLE_ENDIAN.
- Frame length mechanism: 4-byte uint32 LE length prefix (G8/G17).
- Payload start offset: UNRESOLVED.
- Stream decoder: NOT_IMPLEMENTED (no frame-boundary proof).
- 1 MiB max: IMPLEMENTATION_SAFETY_LIMIT.

## References

- `artifacts/phase_2a_g19/service_requirement_matrix.json`
- `docs/NESYSERVICE_MINIMUM_NECESSITY_ASSESSMENT.md`
