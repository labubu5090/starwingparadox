# Phase 2A.0 Initial Baseline

## 1. Phase Status

**PHASE 2A.0 PRE-CABINET RELIABILITY GATE** - In Progress

## 2. Initial Git Baseline

| Item | Value |
|------|-------|
| HEAD | `6f78da3` |
| Commit message | `chore: clean PostgreSQL refs, add concurrency and backup tests` |
| Working tree | Clean |

## 3. Exact Initial Test Result

| Metric | Count |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 821 |
| Tests failed | 1 |
| Tests skipped | 1 |
| Tests xfailed | 0 |
| Warnings | 201 |
| Duration | ~10s |

## 4. Flaky TCP Test

| Item | Value |
|------|-------|
| Test name | `test_ping_handler_returns_framed_response` |
| File | `tests/legacy_regression/test_tcp_legacy.py:356` |
| Class | `TestResponseFraming` |
| Reproduction rate | ~30% when run with full suite |
| Passes alone | 100% |

## 5. Remaining Skipped Test

| Item | Value |
|------|-------|
| Test name | `test_unknown_message_type_raw_mode` |
| File | `tests/unit/test_codec_edge_cases.py:156` |
| Skip reason | `Generated protobuf loaded; raw mode not active` |
| Classification | `OPTIONAL_EXTERNAL_TOOL` |

## 6. Quality Gate Status

| Gate | Status |
|------|--------|
| Ruff | PASS (0 errors) |
| Mypy | PASS (0 errors in 64 files) |
| Full suite | FAIL (1 flaky TCP test) |
