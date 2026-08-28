# NESYSERVICE_MINIMUM_NECESSITY_ASSESSMENT

## Status

**Classification:** MINIMAL_LOCAL_ADAPTER_MAY_BE_REQUIRED

## Question

Is the full NesysService.exe required for the private server, or is a minimal local adapter
sufficient?

## Finding

**Do NOT rebuild full NesysService.** Build a minimal local adapter only where the game
demonstrably requires local IPC, and only after the pipe role (server vs client) is resolved.

## Evidence

The game references the named pipe `\\.\pipe\nesys_games` and NESYS card/control functions, but:

- The game imports **both** server-side (`ConnectNamedPipe`) and client-side (`WaitNamedPipeA`)
  pipe functions, so its role is unresolved.
- The exact pipe message format, command IDs, and payloads are unknown.
- `CERT_ERROR`, `NW_ERROR`, `NWRECOVER_NOTICE` payloads are **opaque**; no certificate
  operation or automatic lifecycle transition may be inferred without control-flow proof.
- Card flow (read, reissue, status, competition ticket) runs through the NESYS path.

## Commands Assessed (all classification UNKNOWN/LOW from game side)

`CLIENT_START`, `CLIENT_START_REPLY`, `CLIENT_END`, `PING`, `PING_RESPONSE`, `CERT_ERROR`,
`NW_ERROR`, `NWRECOVER_NOTICE`.

- Direction, framing, payload, and lifecycle confidence all **LOW**.
- `CERT_ERROR` / `NW_ERROR` / `NWRECOVER_NOTICE` are treated as **OPAQUE**. No automatic
  FAILED/recovery/retry may be triggered without direct control-flow proof.

## Decision Criteria

A local adapter is justified ONLY when:

1. The game demonstrably requires local IPC (pipe role confirmed).
2. The pipe message format is known.
3. The card operations the adapter must service are enumerated.

None of these are satisfied in G19. G19 therefore makes **no live adapter**; it records the
minimum necessary assessment for future implementation.

## References

- `artifacts/phase_2a_g19/service_requirement_matrix.json`
- `artifacts/phase_2a_g19/game_pipe_contract.json`
