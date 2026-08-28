"""Clean-room compatibility foundation for Starwing Paradox NESYS protocol.

This package implements an independent, synthetic protocol foundation based
only on confirmed interface observations from Phase 2A-G16.

This is NOT the original NesysService.
This is NOT an official vendor implementation.
It cannot authenticate to production NESYS.
It does not contain certificate emulation.
It does not create the original named pipe.
It uses synthetic tests only.
Unknown command semantics remain unimplemented.

G18 additions:
- Evidence-locked codec with explicit evidence levels
- Deterministic clock and timeout model
- Session scenario harness with versioned scenarios
- State-machine invariant checker
- Expanded safety guards
"""

