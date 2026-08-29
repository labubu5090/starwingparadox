# G32 Matching Initialization Gate

## The Gate

```
Error No MatchingServer so initialize Nesys before.
```

## Object Lifecycle

```
NOT_INITIALIZED
  -> NESYS_CONTROL_REQUIRED
  -> WAITING_FOR_INITIALIZATION
  -> INITIALIZATION_BLOCKED
```

## Evidence

1. **Binary string:** `BindHttpMatchingServer` at offset 111952304
2. **Game log:** `UCPP_NesysControl::Get(this)->IsOnline[0]`
3. **Error path:** MatchingServer object not initialized
4. **Heartbeats:** Continue despite initialization failure

## What This Means

The MatchingServer object requires NesysControl to be initialized before it can be used. The IsOnline status is [0], indicating NESYS is not ready.

## What It Is NOT

- NOT a certificate trust requirement
- NOT a port 1042 connection requirement
- NOT a production endpoint requirement
- NOT a fake success response requirement

## Recommendation for G33

Investigate the MatchingServer object initialization path to understand what NesysControl initialization is actually required. This is likely a local object dependency.

## Classification

**MATCHING_INITIALIZATION_GATE_RECOVERED**
