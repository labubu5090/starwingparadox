# TCP Flaky Test Root Cause

## 1. Test Identification

| Item | Value |
|------|-------|
| Test name | `test_ping_handler_returns_framed_response` |
| File | `tests/legacy_regression/test_tcp_legacy.py:356` |
| Class | `TestResponseFraming` |

## 2. Reproduction

```bash
# Fails ~30% when run with full suite:
python -m pytest tests/ -ra --tb=short -q

# Passes 100% when run alone:
python -m pytest tests/legacy_regression/test_tcp_legacy.py::TestResponseFraming::test_ping_handler_returns_framed_response -v
```

## 3. Root Cause

The test used `asyncio.get_event_loop().run_until_complete(...)` to run a coroutine synchronously.

**Problem**: `asyncio.get_event_loop()` returns the current event loop or creates a new one. When run with the full test suite, pytest-asyncio manages event loops per test. The call to `asyncio.get_event_loop()` in a synchronous test could:

1. Return an event loop that was previously used by an async test
2. Conflict with pytest-asyncio's loop management
3. In Python 3.10+, emit deprecation warnings when no current loop exists
4. Create race conditions with global module state (`_shutdown_event`)

The test passes in isolation because `asyncio.get_event_loop()` creates a fresh loop. When run after async tests, the loop state is unpredictable.

## 4. Fix

Replace `asyncio.get_event_loop().run_until_complete(...)` with an explicit fresh event loop:

```python
loop = asyncio.new_event_loop()
try:
    result = loop.run_until_complete(_handle_ping(1, 0x66, "Ping", payload))
finally:
    loop.close()
```

This is deterministic because:
- `asyncio.new_event_loop()` always creates a fresh, isolated loop
- The loop is explicitly closed in a `finally` block
- No global event loop state is affected
- No conflict with pytest-asyncio's loop management

## 5. Stress Test Result

| Metric | Result |
|--------|--------|
| Individual runs (100) | 100/100 passed |
| Module runs (50) | 50/50 passed |
| Full suite runs (3) | 3/3 passed |
| Pending-task warnings | 0 |
| Unclosed socket warnings | 0 |
