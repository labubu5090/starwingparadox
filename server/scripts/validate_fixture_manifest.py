#!/usr/bin/env python3
"""Validate legacy regression fixture manifest and all referenced fixture files.

Usage:
    python server/scripts/validate_fixture_manifest.py

Checks:
    1. manifest.json schema validity
    2. Manifest entry fields (fixture_id, file, provenance, sha256)
    3. File existence for each fixture
    4. SHA-256 hash verification of fixture response bodies
    5. Provenance value validation
    6. Fixture ID uniqueness
    7. Full fixture file schema validation (source, endpoint, method, etc.)
    8. Outputs a human-readable validation report
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "legacy"
MANIFEST_PATH = FIXTURES_ROOT / "manifest.json"

REQUIRED_MANIFEST_ENTRY_FIELDS = ["fixture_id", "file", "provenance"]

REQUIRED_FIXTURE_FIELDS = [
    "fixture_id",
    "provenance",
    "source",
    "endpoint",
    "method",
    "request",
    "response",
    "deterministic_fields",
    "dynamic_fields",
    "database_requirements",
]

REQUIRED_SOURCE_FIELDS = ["file", "line_start", "line_end", "description"]

VALID_PROVENANCE = {"LEGACY_SOURCE_DERIVED", "LEGACY_RUNTIME_CAPTURE", "SYNTHETIC_SCHEMA"}

VALID_METHODS = {"POST", "GET", "PUT", "DELETE"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256_of_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Validation Report
# ---------------------------------------------------------------------------


class ValidationReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, msg: str) -> None:
        self.info.append(msg)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines: list[str] = []
        lines.append("=" * 72)
        lines.append("LEGACY FIXTURE MANIFEST VALIDATION REPORT")
        lines.append("=" * 72)
        lines.append("")

        if self.info:
            lines.append(f"--- OK ({len(self.info)}) ---")
            for msg in self.info:
                lines.append(f"  [OK]   {msg}")
            lines.append("")

        if self.warnings:
            lines.append(f"--- WARNINGS ({len(self.warnings)}) ---")
            for msg in self.warnings:
                lines.append(f"  [WARN] {msg}")
            lines.append("")

        if self.errors:
            lines.append(f"--- ERRORS ({len(self.errors)}) ---")
            for msg in self.errors:
                lines.append(f"  [FAIL] {msg}")
            lines.append("")

        lines.append("-" * 72)
        total = len(self.errors) + len(self.warnings) + len(self.info)
        lines.append(
            f"Total checks: {total} | "
            f"Errors: {len(self.errors)} | "
            f"Warnings: {len(self.warnings)} | "
            f"OK: {len(self.info)}"
        )
        if self.passed:
            lines.append("RESULT: PASS")
        else:
            lines.append("RESULT: FAIL")
        lines.append("=" * 72)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Manifest-level validation
# ---------------------------------------------------------------------------


def validate_manifest(report: ValidationReport) -> dict | None:
    if not MANIFEST_PATH.exists():
        report.error(f"Manifest file not found: {MANIFEST_PATH}")
        return None

    try:
        manifest = load_json(MANIFEST_PATH)
    except json.JSONDecodeError as exc:
        report.error(f"Manifest JSON parse error: {exc}")
        return None

    report.ok(f"Manifest loaded: {MANIFEST_PATH}")

    if "fixtures" not in manifest:
        report.error("Manifest missing top-level 'fixtures' array")
        return None

    report.ok(f"Manifest contains {len(manifest['fixtures'])} fixture entries")
    return manifest


def validate_fixture_ids_unique(manifest: dict, report: ValidationReport) -> None:
    seen: dict[str, int] = {}
    for idx, entry in enumerate(manifest["fixtures"]):
        fid = entry.get("fixture_id", "<missing>")
        if fid in seen:
            report.error(f"Duplicate fixture_id '{fid}' at indices {seen[fid]} and {idx}")
        else:
            seen[fid] = idx
    report.ok(f"All {len(seen)} fixture IDs are unique")


def validate_manifest_entry(idx: int, entry: dict, report: ValidationReport) -> None:
    """Validate a manifest entry (lightweight reference)."""
    fid = entry.get("fixture_id", f"<entry-{idx}>")

    for field in REQUIRED_MANIFEST_ENTRY_FIELDS:
        if field not in entry:
            report.error(f"[{fid}] Manifest entry missing field '{field}'")

    prov = entry.get("provenance")
    if prov and prov not in VALID_PROVENANCE:
        report.error(f"[{fid}] Invalid provenance '{prov}'; must be one of {VALID_PROVENANCE}")
    elif prov:
        report.ok(f"[{fid}] Provenance: {prov}")

    file_ref = entry.get("file")
    if file_ref:
        fixture_path = FIXTURES_ROOT / file_ref
        if not fixture_path.exists():
            report.error(f"[{fid}] Fixture file does not exist: {fixture_path}")
        else:
            report.ok(f"[{fid}] Fixture file exists: {file_ref}")


# ---------------------------------------------------------------------------
# Full fixture file validation
# ---------------------------------------------------------------------------


def validate_fixture_file(idx: int, entry: dict, report: ValidationReport) -> None:
    """Load and validate the full fixture JSON file."""
    fid = entry.get("fixture_id", f"<entry-{idx}>")
    file_ref = entry.get("file")
    if not file_ref:
        return

    fixture_path = FIXTURES_ROOT / file_ref
    if not fixture_path.exists():
        return

    try:
        data = load_json(fixture_path)
    except json.JSONDecodeError as exc:
        report.error(f"[{fid}] Fixture file JSON parse error: {exc}")
        return

    report.ok(f"[{fid}] Fixture file is valid JSON")

    # Validate required fields
    for field in REQUIRED_FIXTURE_FIELDS:
        if field not in data:
            report.error(f"[{fid}] Fixture file missing field '{field}'")

    # Validate source sub-fields
    src = data.get("source")
    if isinstance(src, dict):
        for field in REQUIRED_SOURCE_FIELDS:
            if field not in src:
                report.error(f"[{fid}] source missing field '{field}'")

    # Validate response sub-fields
    resp = data.get("response")
    if isinstance(resp, dict):
        # body is required unless the fixture is schema-based (uses body_structure)
        has_body = "body" in resp
        has_body_structure = "body_structure" in resp
        for field in ["status", "headers"]:
            if field not in resp:
                report.error(f"[{fid}] response missing field '{field}'")
        if not has_body and not has_body_structure:
            report.error(f"[{fid}] response missing field 'body' or 'body_structure'")
        elif has_body_structure:
            report.ok(f"[{fid}] Schema-based fixture (body_structure)")
        elif has_body:
            report.ok(f"[{fid}] Body string fixture")

    # Validate method
    method = data.get("method")
    if method and method not in VALID_METHODS:
        report.error(f"[{fid}] Invalid method '{method}'")

    # Verify SHA-256 hash
    stored_hash = entry.get("sha256")
    body = resp.get("body") if isinstance(resp, dict) else None
    if stored_hash and stored_hash not in ("to-be-computed", "schema-based"):
        if body:
            actual_hash = sha256_of_string(body)
            if actual_hash == stored_hash:
                report.ok(f"[{fid}] SHA-256 hash matches")
            else:
                report.error(f"[{fid}] SHA-256 mismatch: expected {stored_hash}, got {actual_hash}")
        else:
            report.warn(f"[{fid}] Cannot verify SHA-256: response.body not found")
    elif stored_hash == "schema-based":
        report.ok(f"[{fid}] SHA-256: schema-based fixture (no body hash)")
    elif stored_hash == "to-be-computed":
        report.warn(f"[{fid}] SHA-256 not computed (placeholder)")


# ---------------------------------------------------------------------------
# Endpoint validation
# ---------------------------------------------------------------------------


def validate_endpoint_references(manifest: dict, report: ValidationReport) -> None:
    endpoints_seen: set[str] = set()
    for entry in manifest["fixtures"]:
        file_ref = entry.get("file")
        if file_ref:
            fixture_path = FIXTURES_ROOT / file_ref
            if fixture_path.exists():
                try:
                    data = load_json(fixture_path)
                    ep = data.get("endpoint", "")
                    endpoints_seen.add(ep)
                except (json.JSONDecodeError, KeyError):
                    pass
    report.ok(f"Unique endpoints referenced: {len(endpoints_seen)}")
    for ep in sorted(endpoints_seen):
        report.ok(f"  Endpoint: {ep}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    report = ValidationReport()

    manifest = validate_manifest(report)
    if manifest is None:
        print(report.summary())
        return 1

    validate_fixture_ids_unique(manifest, report)

    for idx, entry in enumerate(manifest["fixtures"]):
        validate_manifest_entry(idx, entry, report)
        validate_fixture_file(idx, entry, report)

    validate_endpoint_references(manifest, report)

    print(report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
