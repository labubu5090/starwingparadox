# NESYS Service Runtime Result

## Isolated Launch

| Property | Value |
|----------|-------|
| Executable | `X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe` |
| Architecture | x64 |
| Subsystem | Windows Console |
| Working directory | `X:\StarwingParadox\D DRIVE CONTENTS\system\Service` |
| Command line | None (bare execution) |
| PID | 7204 |
| Exit code | 0xFFFFFFFF (-1) |
| Runtime | < 1 second |
| Listeners created | None |
| Connections made | None |
| Files written | None |
| Window created | No |

## Analysis

NesysService exits immediately with exit code -1 when launched standalone. Possible reasons:

1. **Missing named pipe client** — The game must be running to connect to the pipe
2. **Missing configuration** — May require specific command-line arguments
3. **Missing D: drive** — May look for configuration on D:\
4. **Missing parent process** — May require specific process context
5. **Missing registry entries** — May check for installed service state

## Named Pipe Architecture

From binary analysis:
- **Pipe format**: `\\.\pipe\nesys_games\%s%s`
- **IPC method**: Named pipes (CreateNamedPipeA, ConnectNamedPipe)
- **External connection**: WINHTTP to `cert3.nesys.jp`
- **Protocol**: NESYS card/network protocol

## Conclusion

NesysService cannot be launched in isolation. It requires:
1. The game to be running (pipe client)
2. Possibly specific command-line arguments
3. Possibly D: drive configuration

**Status**: UNSAFE_TO_EXECUTE without game context
