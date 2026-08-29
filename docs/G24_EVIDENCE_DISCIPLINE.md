# G24 Evidence Discipline

## Finding 1: CertError is Non-Blocking

**Previous assumption:** CertError blocks the boot sequence.

**Corrected finding:** CertError is a background retry loop. The game reaches the title screen despite CertError.

**Evidence:** G24 extended observation (180s) shows title screen with animations at T+180s. Log analysis shows CertError interleaved with asset preloading.

## Finding 2: Asset Preloading Continues

**Previous assumption:** CertError may prevent asset loading.

**Corrected finding:** Asset preloading runs concurrently with CertError retry loop. 5972/7553 assets loaded (79%) at log end.

**Evidence:** G24 log analysis shows preloader progress from 2/7553 to 5972/7553 while CertError logs continue.

## Finding 3: Title Screen Reached

**Previous assumption:** Game may not reach title screen without certificate validation.

**Corrected finding:** Title screen is reached with animations playing. WBP_Title_MainDisplay and WBP_InsertStart are active.

**Evidence:** Last 30 lines of G24 log show title screen state transitions.
