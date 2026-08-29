# Phase 2A-G21 Final Report

## Classification

**RUNTIME_PATH_OBSERVED_CONTRACT_INCOMPLETE**

## Summary

G21 combined static IDA analysis and bounded runtime Wireshark observation of the operator-owned Starwing Paradox game to recover HTTP startup contract evidence.

### IDA Static Analysis
- **IDA 9.3** batch mode successfully loaded the 163MB shipping executable
- **578,427 functions** and **368,970 strings** analyzed
- **17 target HTTP strings** found in binary at known file offsets
- **16/17 verified** at correct virtual addresses
- **0 direct code xrefs** found — strings are referenced indirectly (UE4 FName/FString pattern)
- **Hex-Rays v9.3.0.260327** available for pseudocode generation

### Runtime Wireshark Observation
- **1,648 packets** captured over 90 seconds
- **9 HTTP health checks** to `127.0.0.1:5233/api/health` (every 10 seconds)
- **0 external HTTP requests** during capture window
- **0 DNS queries** during capture
- **No port 4001 or 6666** observed (NESYS pipe ports)
- **TCP connection attempts to port 1042** on localhost (all reset)

### Key Finding
The game is already configured to communicate with the Python private server on localhost:5233. The external game server connection (43.129.138.3:80) was established before the capture window, suggesting the startup HTTP sequence completed before observation began.

## Protected Hash Verification
| Binary | SHA-256 | Status |
|--------|---------|--------|
| AcrGame.exe | 97800621BB9... | ✓ UNCHANGED |
| AcrGame-Win64-Shipping.exe | CE4C89054BF7... | ✓ UNCHANGED |
| GALAXYIO.dll | 47B4E1EDD13A... | ✓ UNCHANGED |
| Lua524.dll | 5B8F9941F91C... | ✓ UNCHANGED |
| QRreader.dll | C6DDFDF67391... | ✓ UNCHANGED |

## Safety Confirmation
- No original binary modified
- No original binary executed
- No debugger attached
- No live named pipe created
- No service or Registry change
- No certificate access
- No hosts or DNS modification
- No port-80 listener created
- No crafted packet sent
- No external host scanned
- No TLS secrets collected
- No real card or account used
- All game processes closed
- Wireshark capture closed

## Recommended Next Phase
Phase 2A-G22: Extended runtime observation with capture started BEFORE game launch to observe the complete startup HTTP sequence. Consider using IDA GUI with Hex-Rays decompiler for targeted function analysis of the identified HTTP binding functions.
