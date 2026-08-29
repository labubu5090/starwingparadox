# G30 Post-Start Player Session Boundary

## NESYS Connection Error

The game is now stuck at boot with NesysControlErrorMessage / id[0] status[4] option[0]. This is a NEW blocker not seen in G29.

## Timeline

1. Game launched
2. Title ready detected (possibly false positive)
3. NESYS errors started flooding (90+ errors)
4. Game never reached title screen
5. No Z input possible
6. No HTTP requests sent

## Proxy Status

- Proxy working: YES (tested with curl)
- Response: {"ip_addr": "127.0.0.1:6666"}
- Port 80: LISTENING
- Port 4001: LISTENING

## G31 Decision

Must implement NESYS mock (port 1042) to bypass this error.
