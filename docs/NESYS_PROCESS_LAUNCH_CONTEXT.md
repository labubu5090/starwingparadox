# NESYS Process Launch Context

## Bootstrap Chain

| Step | Process | PID | Evidence |
|------|---------|-----|----------|
| 1 | AcrGame.exe | Bootstrap | Launched by user |
| 2 | AcrGame-Win64-Shipping.exe | Auto-spawned | Created by bootstrap |

## NesysService Launch Attempt

**NOT_OBSERVED** — Neither AcrGame.exe nor AcrGame-Win64-Shipping.exe attempted to launch NesysService.exe during the observed boot.

## Analysis

The game's NESYS client plugin initializes at frame 2 and begins CertError retries at frame 4. The game does NOT attempt to launch NesysService.exe. This implies:

1. NesysService.exe is expected to be running BEFORE the game starts
2. Or NesysService.exe is launched by an external service manager
3. Or the arcade cabinet hardware/software starts NesysService

## Working Directory

- AcrGame.exe: `X:\StarwingParadox\WindowsNoEditor`
- AcrGame-Win64-Shipping.exe: Spawned by bootstrap (working dir inherited)

## Command Line

Not captured (Process Monitor not available). No sensitive values observed.

## Exit Behavior

- Bootstrap (AcrGame.exe): Remains running
- Shipping (AcrGame-Win64-Shipping.exe): Crashed with EXCEPTION_ACCESS_VIOLATION in post-process AA renderer at the title screen

## Conclusion

NesysService is NOT launched by the game processes. It must be started externally before game launch.
