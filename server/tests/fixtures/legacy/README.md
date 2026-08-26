# Legacy Regression Fixtures

## Purpose

These fixtures encode the **proven behavior** of the original Starwing Paradox JavaScript server (`legacy-js/js/starwing.js`). They serve as the ground truth for regression testing the Python reimplementation.

## Provenance Types

Every fixture MUST declare one of three provenance types:

### LEGACY_SOURCE_DERIVED

Fixtures constructed by reading the legacy JavaScript source code and computing the exact response the legacy server would produce. These fixtures include:
- Source file path and line range as evidence
- The exact JSON response body (as a string, preserving whitespace)
- Response headers as produced by the legacy code

**Confidence level**: HIGH — derived from source code analysis.

### LEGACY_RUNTIME_CAPTURE

Fixtures captured from a running instance of the legacy server (via mitmproxy, tcpdump, or request logging). These include:
- Capture timestamp
- Network capture file reference
- Request and response as wire-format data

**Confidence level**: HIGHEST — empirical evidence from running system.

### SYNTHETIC_SCHEMA

Fixtures constructed from documentation, API notes, or inferred from protobuf definitions. These include:
- Schema source references
- Best-guess request/response structures

**Confidence level**: LOW — may not match actual legacy behavior.

## Fixture Structure

Each fixture is a JSON file with the following top-level structure:

```json
{
  "fixture_id": "unique-kebab-case-id",
  "provenance": "LEGACY_SOURCE_DERIVED",
  "source": {
    "file": "legacy-js/js/starwing.js",
    "line_start": 407,
    "line_end": 426,
    "description": "POST /version handler"
  },
  "endpoint": "/version",
  "method": "POST",
  "request": {
    "headers": {},
    "body": {}
  },
  "response": {
    "status": 200,
    "headers": {
      "content-type": "application/json",
      "x-galaxy-api": "*/*"
    },
    "body": "{ ... }"
  },
  "deterministic_fields": ["client_version", "data_version", "stage_ids"],
  "dynamic_fields": ["x-galaxy-api-id"],
  "database_requirements": [],
  "notes": ""
}
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `fixture_id` | Yes | Unique identifier (kebab-case) |
| `provenance` | Yes | One of: `LEGACY_SOURCE_DERIVED`, `LEGACY_RUNTIME_CAPTURE`, `SYNTHETIC_SCHEMA` |
| `source` | Yes | Evidence reference (file + line range) |
| `endpoint` | Yes | HTTP endpoint path |
| `method` | Yes | HTTP method |
| `request` | Yes | Request headers and body |
| `response` | Yes | Expected response (status, headers, body as string) |
| `deterministic_fields` | Yes | Fields with fixed values |
| `dynamic_fields` | Yes | Fields that vary per request (e.g., echoed headers) |
| `database_requirements` | Yes | Database state required for this fixture |
| `notes` | No | Additional context |

## Metadata Requirements

1. **Uniqueness**: Each `fixture_id` must be unique within the fixture set.
2. **Hash integrity**: The `response.body` string must match the SHA-256 hash stored in `manifest.json`.
3. **Provenance chain**: Every fixture must have a traceable source (file + lines for SOURCE_DERIVED, capture file for RUNTIME_CAPTURE).
4. **No synthetic placeholders**: Fixtures labeled `LEGACY_SOURCE_DERIVED` must not contain fabricated values.

## Directory Organization

```
legacy/
├── http/          # HTTP endpoint fixtures (JSON)
├── tcp/           # TCP/protobuf wire captures (binary + JSON metadata)
├── protobuf/      # Protobuf schema fixtures
└── database/      # Database seed data for fixture execution
```
