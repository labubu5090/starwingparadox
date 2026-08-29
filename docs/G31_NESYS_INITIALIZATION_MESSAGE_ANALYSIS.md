# G31 NESYS Initialization Message Analysis

## The Message

```
Error No MatchingServer so initialize Nesys before.
```

## Context

This message appears after:
1. Game connects to TCP port 6666
2. Game sends Ping messages
3. Server responds with Ping
4. Game receives TickReport
5. Game attempts to initialize matching entry

## Interpretation

The message "No MatchingServer so initialize Nesys before" suggests:

1. **MatchingServer object** - The game has a local MatchingServer object
2. **NESYS initialization** - This object requires NESYS to be initialized first
3. **Not a certificate check** - The game already passed certificate validation in boot
4. **Not a network check** - The game already resolved 127.0.0.1:6666

## Possible Meanings

1. **Local object initialization** - MatchingServer needs NesysControl to be initialized
2. **Network state** - MatchingServer needs a network state from NESYS
3. **Machine data** - MatchingServer needs machine data from NESYS
4. **Session state** - MatchingServer needs a session state from NESYS

## What It Is NOT

- NOT a certificate trust requirement
- NOT a port 1042 connection requirement
- NOT a production endpoint requirement
- NOT a fake success response requirement

## Recommendation for G32

Investigate the MatchingServer object initialization path in IDA to understand what NESYS initialization is actually required. This is likely a local object dependency, not a trust/certificate requirement.

## Classification

**LOCAL_OBJECT_INITIALIZATION_DEPENDENCY**
