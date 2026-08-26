# Response Comparison Guide

This tool compares legacy JavaScript server responses with Python server responses for the Starwing Paradox project. The legacy server does not need to be running — saved snapshots can be used offline.

## Quick Start

```bash
# Compare two saved snapshots
python scripts/compare_responses.py compare legacy_version.json python_version.json

# Compare live servers
python scripts/compare_responses.py live --legacy-url http://localhost:4001 --python-url http://localhost:8000

# List available test scenarios
python scripts/compare_responses.py live --list
```

## Snapshot Format

Each snapshot is a JSON file containing:

| Field          | Description                                |
|----------------|--------------------------------------------|
| `name`         | Identifier (e.g. `version_endpoint`)       |
| `method`       | HTTP method (usually `POST`)               |
| `path`         | Request path (e.g. `/version`)             |
| `status_code`  | HTTP status code                           |
| `content_type` | Content-Type header value                  |
| `headers`      | Response headers (object)                  |
| `body_hex`     | Raw response body as hex string            |
| `body_sha256`  | SHA-256 hash of body                       |
| `body_length`  | Byte length of body                        |
| `provenance`   | How this snapshot was obtained             |
| `timestamp`    | Unix timestamp when captured               |
| `note`         | Optional human note                        |

## Provenance Values

| Value               | Meaning                                      |
|---------------------|----------------------------------------------|
| `LEGACY_REFERENCE`  | Captured from the actual legacy JS server    |
| `SYNTHETIC`         | Manually constructed / synthetic data        |
| `CABINET_CAPTURE`   | Captured from game cabinet hardware          |
| `OFFICIAL_CAPTURE`  | Officially released response from developer  |

## Comparison Results

| Result                   | Meaning                                                    |
|--------------------------|------------------------------------------------------------|
| `EXACT_BYTE_MATCH`       | Bodies are byte-identical                                  |
| `SEMANTIC_PROTO_MATCH`   | Bodies differ in bytes but decoded protobuf fields match   |
| `HEADER_MISMATCH`        | Status matched but selected headers differ                 |
| `STATUS_MISMATCH`        | HTTP status codes differ                                   |
| `BODY_MISMATCH`          | Bodies differ and protobuf fields do not match             |
| `SIDE_EFFECT_MISMATCH`   | Side effects (DB writes, etc.) differ                      |
| `CANNOT_COMPARE`         | Comparison failed (missing dependency, server unreachable) |
| `CAPTURE_REQUIRED`       | No legacy reference exists; must capture one               |

## Capturing Snapshots

Capture a response from a live server and save it:

```bash
python scripts/compare_responses.py generate-snapshot \
    --url http://localhost:4001 \
    --name version_legacy \
    --path /version \
    --output fixtures/legacy/version_legacy.json \
    --provenance LEGACY_REFERENCE
```

## Comparing Two Snapshots

```bash
python scripts/compare_responses.py compare \
    fixtures/legacy/version_legacy.json \
    fixtures/python/version_python.json
```

Output:
```
Result: EXACT_BYTE_MATCH
  Matched: status_code, content_type, headers, body_length, body_sha256
```

## Comparing Fixtures Against Live Python Server

```bash
python scripts/compare_responses.py fixtures \
    --fixture-dir fixtures/legacy \
    --python-url http://localhost:8000 \
    --output results.json
```

This loads every `.json` file from `fixtures/legacy/`, sends the same request to the Python server, and compares the responses.

## Viewing a Snapshot

```bash
python scripts/compare_responses.py load fixtures/legacy/version_legacy.json
```

## Comparison Details

The tool compares in order:

1. **Status code** — if different → `STATUS_MISMATCH`
2. **Content-Type** — if different → `HEADER_MISMATCH`
3. **Selected headers** — `content-type`, `x-request-id`, `x-server-version`, `cache-control`
4. **Body length** — if different → `BODY_MISMATCH`
5. **Body SHA-256** — if different → `BODY_MISMATCH`
6. **Protobuf semantic** — if decoded fields match → `SEMANTIC_PROTO_MATCH`

## Integration with pytest

Use the comparison tool in integration tests:

```python
from scripts.compare_responses import (
    ResponseSnapshot,
    compare_snapshots,
    ComparisonResult,
)

def test_version_matches_legacy():
    legacy = ResponseSnapshot.load(Path("fixtures/legacy/version.json"))
    python = ResponseSnapshot.load(Path("fixtures/python/version.json"))
    detail = compare_snapshots(legacy, python)
    assert detail.result == ComparisonResult.EXACT_BYTE_MATCH
```

## Directory Structure

```
fixtures/
  legacy/
    version_legacy.json
    resource_legacy.json
    ...
  python/
    version_python.json
    resource_python.json
    ...
```
