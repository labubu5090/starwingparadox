"""Response comparison harness for Starwing Paradox.

Compares legacy JavaScript server responses with Python server responses.
Supports saved fixtures with explicit provenance so the legacy server does
not need to be running.

Usage:
    python scripts/compare_responses.py --fixture-dir fixtures/legacy --python-url http://localhost:4001
    python scripts/compare_responses.py --load response.json
    python scripts/compare_responses.py --compare a.json b.json
"""

from __future__ import annotations

import argparse
import enum
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Comparison classification
# ---------------------------------------------------------------------------


class ComparisonResult(str, enum.Enum):
    EXACT_BYTE_MATCH = "EXACT_BYTE_MATCH"
    SEMANTIC_PROTO_MATCH = "SEMANTIC_PROTO_MATCH"
    HEADER_MISMATCH = "HEADER_MISMATCH"
    STATUS_MISMATCH = "STATUS_MISMATCH"
    BODY_MISMATCH = "BODY_MISMATCH"
    SIDE_EFFECT_MISMATCH = "SIDE_EFFECT_MISMATCH"
    CANNOT_COMPARE = "CANNOT_COMPARE"
    CAPTURE_REQUIRED = "CAPTURE_REQUIRED"


class Provenance(str, enum.Enum):
    LEGACY_REFERENCE = "LEGACY_REFERENCE"
    SYNTHETIC = "SYNTHETIC"
    CABINET_CAPTURE = "CABINET_CAPTURE"
    OFFICIAL_CAPTURE = "OFFICIAL_CAPTURE"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ResponseSnapshot:
    """A captured response for offline comparison."""

    name: str
    method: str = "POST"
    path: str = "/"
    status_code: int = 200
    content_type: str = "application/octet-stream"
    headers: dict[str, str] = field(default_factory=dict)
    body_bytes: bytes = b""
    provenance: Provenance = Provenance.SYNTHETIC
    timestamp: float = field(default_factory=time.time)
    note: str = ""

    @property
    def body_sha256(self) -> str:
        return hashlib.sha256(self.body_bytes).hexdigest()

    @property
    def body_length(self) -> int:
        return len(self.body_bytes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "headers": self.headers,
            "body_hex": self.body_bytes.hex(),
            "body_sha256": self.body_sha256,
            "body_length": self.body_length,
            "provenance": self.provenance.value,
            "timestamp": self.timestamp,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResponseSnapshot:
        body_hex = data.get("body_hex", "")
        return cls(
            name=data["name"],
            method=data.get("method", "POST"),
            path=data.get("path", "/"),
            status_code=data.get("status_code", 200),
            content_type=data.get("content_type", "application/octet-stream"),
            headers=data.get("headers", {}),
            body_bytes=bytes.fromhex(body_hex) if body_hex else b"",
            provenance=Provenance(data.get("provenance", "SYNTHETIC")),
            timestamp=data.get("timestamp", 0.0),
            note=data.get("note", ""),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path) -> ResponseSnapshot:
        data = json.loads(path.read_text())
        return cls.from_dict(data)


@dataclass
class ComparisonDetail:
    """Detailed result of comparing two snapshots."""

    result: ComparisonResult
    fields_matched: list[str] = field(default_factory=list)
    fields_differed: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Protobuf helpers (best-effort; no protobuf dependency required)
# ---------------------------------------------------------------------------


def try_decode_protobuf(body: bytes) -> tuple[dict[str, Any], str | None]:
    """Attempt to decode body as a simple protobuf message.

    Returns (parsed_dict, error_or_None).  If the body is JSON, it is
    returned directly.  If protobuf decoding fails, an empty dict and
    an error string are returned.
    """
    if not body:
        return {}, None

    # Try JSON first
    try:
        return json.loads(body), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    # Attempt a minimal protobuf varint/string decoder for field inspection.
    # This does NOT require the protobuf library.
    try:
        return _decode_raw_varints(body), None
    except Exception as exc:
        return {}, f"protobuf decode failed: {exc}"


def _decode_raw_varints(data: bytes) -> dict[str, Any]:
    """Decode a protobuf message into {field_number: value} without schema."""
    fields: dict[str, Any] = {}
    pos = 0
    field_num = 0
    while pos < len(data):
        # Read varint for tag
        tag, pos = _read_varint(data, pos)
        if pos > len(data):
            break
        field_num = tag >> 3
        wire_type = tag & 0x07

        if wire_type == 0:  # varint
            value, pos = _read_varint(data, pos)
            fields[str(field_num)] = value
        elif wire_type == 1:  # 64-bit
            if pos + 8 > len(data):
                break
            value = int.from_bytes(data[pos : pos + 8], "little")
            fields[str(field_num)] = value
            pos += 8
        elif wire_type == 2:  # length-delimited (string / bytes / sub-message)
            length, pos = _read_varint(data, pos)
            if pos + length > len(data):
                break
            chunk = data[pos : pos + length]
            pos += length
            try:
                fields[str(field_num)] = chunk.decode("utf-8")
            except UnicodeDecodeError:
                fields[str(field_num)] = chunk.hex()
        elif wire_type == 5:  # 32-bit
            if pos + 4 > len(data):
                break
            value = int.from_bytes(data[pos : pos + 4], "little")
            fields[str(field_num)] = value
            pos += 4
        else:
            # Unknown wire type – stop parsing
            break
    return fields


def _read_varint(data: bytes, pos: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if byte < 0x80:
            return result, pos
        shift += 7
    return result, pos


# ---------------------------------------------------------------------------
# Comparison engine
# ---------------------------------------------------------------------------

COMPARABLE_HEADERS = [
    "content-type",
    "x-request-id",
    "x-server-version",
    "cache-control",
]


def compare_snapshots(
    legacy: ResponseSnapshot,
    python: ResponseSnapshot,
    *,
    skip_side_effects: bool = False,
) -> ComparisonDetail:
    """Compare two ResponseSnapshots and return a ClassificationDetail."""

    detail = ComparisonDetail(result=ComparisonResult.EXACT_BYTE_MATCH)

    # --- Status code ---
    if legacy.status_code != python.status_code:
        detail.result = ComparisonResult.STATUS_MISMATCH
        detail.fields_differed.append("status_code")
        detail.messages.append(f"status {legacy.status_code} != {python.status_code}")
        return detail
    detail.fields_matched.append("status_code")

    # --- Content-Type ---
    if legacy.content_type != python.content_type:
        detail.result = ComparisonResult.HEADER_MISMATCH
        detail.fields_differed.append("content_type")
        detail.messages.append(f"content-type {legacy.content_type!r} != {python.content_type!r}")
        return detail
    detail.fields_matched.append("content_type")

    # --- Selected headers ---
    for hdr in COMPARABLE_HEADERS:
        lv = legacy.headers.get(hdr, "")
        pv = python.headers.get(hdr, "")
        if lv and pv and lv != pv:
            detail.result = ComparisonResult.HEADER_MISMATCH
            detail.fields_differed.append(f"header:{hdr}")
            detail.messages.append(f"header {hdr}: {lv!r} != {pv!r}")
    if detail.result == ComparisonResult.EXACT_BYTE_MATCH:
        detail.fields_matched.append("headers")

    # --- If headers mismatched, stop (body comparison is irrelevant) ---
    if detail.result == ComparisonResult.HEADER_MISMATCH:
        return detail

    # --- Raw body length ---
    if legacy.body_length != python.body_length:
        detail.result = ComparisonResult.BODY_MISMATCH
        detail.fields_differed.append("body_length")
        detail.messages.append(f"body length {legacy.body_length} != {python.body_length}")
    else:
        detail.fields_matched.append("body_length")

    # --- Raw body SHA-256 ---
    if legacy.body_sha256 != python.body_sha256:
        if detail.result == ComparisonResult.EXACT_BYTE_MATCH:
            detail.result = ComparisonResult.BODY_MISMATCH
        detail.fields_differed.append("body_sha256")
        detail.messages.append(f"sha256 {legacy.body_sha256} != {python.body_sha256}")
    else:
        detail.fields_matched.append("body_sha256")

    # --- If bodies match at byte level, done ---
    if (
        detail.result == ComparisonResult.EXACT_BYTE_MATCH
        and legacy.body_sha256 == python.body_sha256
    ):
        return detail

    # --- Try semantic protobuf comparison ---
    legacy_decoded, l_err = try_decode_protobuf(legacy.body_bytes)
    python_decoded, p_err = try_decode_protobuf(python.body_bytes)

    if not l_err and not p_err and legacy_decoded == python_decoded:
        detail.result = ComparisonResult.SEMANTIC_PROTO_MATCH
        detail.messages.append("decoded protobuf fields match semantically")
        return detail

    if l_err or p_err:
        detail.messages.append(f"decode info: legacy={l_err}, python={p_err}")

    return detail


def compare_with_live(
    legacy_url: str,
    python_url: str,
    path: str,
    body: dict[str, Any] | None = None,
    method: str = "POST",
    extra_headers: dict[str, str] | None = None,
) -> ComparisonDetail:
    """Send the same request to both servers and compare responses."""
    try:
        import httpx
    except ImportError:
        return ComparisonDetail(
            result=ComparisonResult.CANNOT_COMPARE,
            messages=["httpx is required for live comparison: pip install httpx"],
        )

    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    payloads = json.dumps(body or {}).encode()

    def _fetch(base: str) -> ResponseSnapshot | None:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.request(method, f"{base}{path}", content=payloads, headers=headers)
                return ResponseSnapshot(
                    name=f"live_{base}",
                    method=method,
                    path=path,
                    status_code=resp.status_code,
                    content_type=resp.headers.get("content-type", ""),
                    headers=dict(resp.headers),
                    body_bytes=resp.content,
                )
        except Exception:
            return None

    legacy_snap = _fetch(legacy_url)
    python_snap = _fetch(python_url)

    if legacy_snap is None or python_snap is None:
        return ComparisonDetail(
            result=ComparisonResult.CANNOT_COMPARE,
            messages=["failed to reach one or both servers"],
        )

    return compare_snapshots(legacy_snap, python_snap)


# ---------------------------------------------------------------------------
# Fixture directory helpers
# ---------------------------------------------------------------------------


def load_fixtures_from_dir(fixture_dir: Path) -> list[ResponseSnapshot]:
    """Load all .json fixture files from a directory."""
    snapshots = []
    for p in sorted(fixture_dir.glob("*.json")):
        try:
            snapshots.append(ResponseSnapshot.load(p))
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"  Warning: skipping {p.name}: {exc}", file=sys.stderr)
    return snapshots


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

COMPARISON_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "version",
        "method": "POST",
        "path": "/version",
        "body": {},
        "description": "Version endpoint returns client_version, data_version, stage_ids",
    },
    {
        "name": "resource",
        "method": "POST",
        "path": "/resource",
        "body": {},
        "description": "Resource endpoint returns game resource JSON",
    },
    {
        "name": "matching_server",
        "method": "POST",
        "path": "/matching/server",
        "body": {},
        "headers": {"x-galaxy-real-ip": "127.0.0.1"},
        "description": "Matching server returns matcher address",
    },
    {
        "name": "match_id_generate",
        "method": "POST",
        "path": "/matching/match_id/generate",
        "body": {},
        "description": "Match ID generation",
    },
    {
        "name": "player_profile_load",
        "method": "POST",
        "path": "/player/profile/load",
        "body": {"nesys_id": "TESTNESYS00001"},
        "description": "Player profile load",
    },
    {
        "name": "player_login",
        "method": "POST",
        "path": "/player/login",
        "body": {"player_id": "10010"},
        "description": "Player login",
    },
    {
        "name": "ranking_national",
        "method": "POST",
        "path": "/ranking/national",
        "body": {},
        "description": "National ranking",
    },
    {
        "name": "battle_record_2on2",
        "method": "POST",
        "path": "/battle/record_2on2",
        "body": {
            "match_id": "41772",
            "player_id": "10010",
            "stage_id": "20001",
            "battle_result": "win",
            "battle_time": "143",
            "play_time": "143",
        },
        "description": "Battle result recording",
    },
]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare Python server responses against legacy JavaScript responses"
    )
    sub = parser.add_subparsers(dest="command")

    # --- compare sub-command (two saved snapshots) ---
    cmp = sub.add_parser("compare", help="Compare two saved snapshots")
    cmp.add_argument("left", help="Path to the first snapshot JSON")
    cmp.add_argument("right", help="Path to the second snapshot JSON")

    # --- load sub-command (print a snapshot) ---
    load = sub.add_parser("load", help="Load and print a snapshot")
    load.add_argument("path", help="Path to snapshot JSON")

    # --- live sub-command (live comparison) ---
    live = sub.add_parser("live", help="Compare live servers")
    live.add_argument("--legacy-url", default="http://localhost:4001")
    live.add_argument("--python-url", default="http://localhost:8000")
    live.add_argument("--scenario", help="Run a named scenario")
    live.add_argument("--list", action="store_true", help="List scenarios")

    # --- fixture sub-command (compare fixture dir against live python) ---
    fix = sub.add_parser("fixtures", help="Compare fixture directory against Python server")
    fix.add_argument("--fixture-dir", required=True, help="Directory of legacy snapshots")
    fix.add_argument("--python-url", default="http://localhost:8000")
    fix.add_argument("--output", help="Write results to JSON file")

    # --- generate-submission ---
    gen = sub.add_parser("generate-snapshot", help="Capture a live snapshot and save it")
    gen.add_argument("--url", required=True, help="Server URL")
    gen.add_argument("--name", required=True, help="Snapshot name")
    gen.add_argument("--path", dest="req_path", default="/", help="Request path")
    gen.add_argument("--method", default="POST")
    gen.add_argument("--body", default="{}", help="JSON body string")
    gen.add_argument("--output", required=True, help="Output file path")
    gen.add_argument("--provenance", default="SYNTHETIC", choices=[p.value for p in Provenance])

    return parser


def cmd_compare(args: argparse.Namespace) -> int:
    left = ResponseSnapshot.load(Path(args.left))
    right = ResponseSnapshot.load(Path(args.right))
    detail = compare_snapshots(left, right)
    _print_detail(detail)
    return (
        0
        if detail.result
        in (
            ComparisonResult.EXACT_BYTE_MATCH,
            ComparisonResult.SEMANTIC_PROTO_MATCH,
        )
        else 1
    )


def cmd_load(args: argparse.Namespace) -> int:
    snap = ResponseSnapshot.load(Path(args.path))
    print(json.dumps(snap.to_dict(), indent=2))
    return 0


def cmd_live(args: argparse.Namespace) -> int:
    if args.list:
        print("Available comparison scenarios:")
        for s in COMPARISON_SCENARIOS:
            print(f"  {s['name']:25s} {s['description']}")
        return 0

    scenarios = COMPARISON_SCENARIOS
    if args.scenario:
        scenarios = [s for s in COMPARISON_SCENARIOS if s["name"] == args.scenario]
        if not scenarios:
            print(f"Error: unknown scenario '{args.scenario}'", file=sys.stderr)
            return 1

    failures = 0
    for scenario in scenarios:
        print(f"  {scenario['name']}... ", end="", flush=True)
        detail = compare_with_live(
            args.legacy_url,
            args.python_url,
            scenario["path"],
            body=scenario.get("body"),
            method=scenario.get("method", "POST"),
            extra_headers=scenario.get("headers"),
        )
        print(detail.result.value)
        if detail.result not in (
            ComparisonResult.EXACT_BYTE_MATCH,
            ComparisonResult.SEMANTIC_PROTO_MATCH,
        ):
            failures += 1
            for msg in detail.messages:
                print(f"    {msg}")
    return 1 if failures else 0


def cmd_fixtures(args: argparse.Namespace) -> int:
    fixture_dir = Path(args.fixture_dir)
    if not fixture_dir.is_dir():
        print(f"Error: {fixture_dir} is not a directory", file=sys.stderr)
        return 1

    snapshots = load_fixtures_from_dir(fixture_dir)
    if not snapshots:
        print("No fixtures found.")
        return 0

    try:
        import httpx
    except ImportError:
        print("Error: httpx required for live comparison", file=sys.stderr)
        return 1

    results: list[dict[str, Any]] = []
    for snap in snapshots:
        print(f"  {snap.name}... ", end="", flush=True)
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.request(
                    snap.method,
                    f"{args.python_url}{snap.path}",
                    content=snap.body_bytes,
                    headers={"Content-Type": snap.content_type},
                )
                live = ResponseSnapshot(
                    name=snap.name,
                    method=snap.method,
                    path=snap.path,
                    status_code=resp.status_code,
                    content_type=resp.headers.get("content-type", ""),
                    headers=dict(resp.headers),
                    body_bytes=resp.content,
                )
        except Exception as exc:
            print(f"ERROR ({exc})")
            results.append({"name": snap.name, "result": "CANNOT_COMPARE", "error": str(exc)})
            continue

        detail = compare_snapshots(snap, live)
        print(detail.result.value)
        results.append(
            {
                "name": snap.name,
                "result": detail.result.value,
                "messages": detail.messages,
                "legacy_sha256": snap.body_sha256,
                "python_sha256": live.body_sha256,
            }
        )

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2))
        print(f"\nResults written to {args.output}")

    failures = sum(
        1 for r in results if r["result"] not in ("EXACT_BYTE_MATCH", "SEMANTIC_PROTO_MATCH")
    )
    return 1 if failures else 0


def cmd_generate_snapshot(args: argparse.Namespace) -> int:
    import httpx

    body_bytes = args.body.encode()
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.request(
                args.method,
                f"{args.url}{args.req_path}",
                content=body_bytes,
                headers={"Content-Type": "application/json"},
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    snap = ResponseSnapshot(
        name=args.name,
        method=args.method,
        path=args.req_path,
        status_code=resp.status_code,
        content_type=resp.headers.get("content-type", ""),
        headers=dict(resp.headers),
        body_bytes=resp.content,
        provenance=Provenance(args.provenance),
    )
    snap.save(Path(args.output))
    print(f"Saved snapshot to {args.output}")
    print(f"  sha256:  {snap.body_sha256}")
    print(f"  length:  {snap.body_length}")
    return 0


def _print_detail(detail: ComparisonDetail) -> None:
    print(f"Result: {detail.result.value}")
    if detail.fields_matched:
        print(f"  Matched: {', '.join(detail.fields_matched)}")
    if detail.fields_differed:
        print(f"  Differed: {', '.join(detail.fields_differed)}")
    for msg in detail.messages:
        print(f"  {msg}")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    dispatch = {
        "compare": cmd_compare,
        "load": cmd_load,
        "live": cmd_live,
        "fixtures": cmd_fixtures,
        "generate-snapshot": cmd_generate_snapshot,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
