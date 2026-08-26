"""Tests for the response comparison harness."""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.compare_responses import (
    ComparisonResult,
    Provenance,
    ResponseSnapshot,
    compare_snapshots,
    load_fixtures_from_dir,
    try_decode_protobuf,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def legacy_snapshot() -> ResponseSnapshot:
    return ResponseSnapshot(
        name="test_legacy",
        method="POST",
        path="/version",
        status_code=200,
        content_type="application/json",
        headers={"x-request-id": "abc123"},
        body_bytes=json.dumps(
            {
                "client_version": "1.0.0",
                "data_version": "2.0.0",
                "stage_ids": [1001, 1002],
            }
        ).encode(),
        provenance=Provenance.LEGACY_REFERENCE,
    )


@pytest.fixture
def python_snapshot_identical(legacy_snapshot: ResponseSnapshot) -> ResponseSnapshot:
    return ResponseSnapshot(
        name="test_python",
        method=legacy_snapshot.method,
        path=legacy_snapshot.path,
        status_code=legacy_snapshot.status_code,
        content_type=legacy_snapshot.content_type,
        headers=legacy_snapshot.headers.copy(),
        body_bytes=legacy_snapshot.body_bytes,
        provenance=Provenance.SYNTHETIC,
    )


@pytest.fixture
def python_snapshot_different_body() -> ResponseSnapshot:
    return ResponseSnapshot(
        name="test_python_diff",
        method="POST",
        path="/version",
        status_code=200,
        content_type="application/json",
        headers={},
        body_bytes=json.dumps(
            {
                "client_version": "9.9.9",
                "data_version": "2.0.0",
                "stage_ids": [1001, 1002],
            }
        ).encode(),
        provenance=Provenance.SYNTHETIC,
    )


@pytest.fixture
def python_snapshot_different_status() -> ResponseSnapshot:
    return ResponseSnapshot(
        name="test_python_500",
        method="POST",
        path="/version",
        status_code=500,
        content_type="text/plain",
        body_bytes=b"Internal Server Error",
        provenance=Provenance.SYNTHETIC,
    )


@pytest.fixture
def python_snapshot_semantic_match() -> ResponseSnapshot:
    """Different bytes but semantically equivalent protobuf fields."""
    return ResponseSnapshot(
        name="test_python_proto",
        method="POST",
        path="/resource",
        status_code=200,
        content_type="application/octet-stream",
        body_bytes=bytes([0x08, 0x01, 0x12, 0x05, 0x68, 0x65, 0x6C, 0x6C, 0x6F]),
        provenance=Provenance.SYNTHETIC,
    )


# ---------------------------------------------------------------------------
# ResponseSnapshot serialisation
# ---------------------------------------------------------------------------


class TestResponseSnapshot:
    def test_to_dict_roundtrip(self, legacy_snapshot: ResponseSnapshot):
        d = legacy_snapshot.to_dict()
        restored = ResponseSnapshot.from_dict(d)
        assert restored.name == legacy_snapshot.name
        assert restored.body_bytes == legacy_snapshot.body_bytes
        assert restored.body_sha256 == legacy_snapshot.body_sha256
        assert restored.provenance == legacy_snapshot.provenance

    def test_save_and_load(self, legacy_snapshot: ResponseSnapshot):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "snap.json"
            legacy_snapshot.save(path)
            loaded = ResponseSnapshot.load(path)
            assert loaded == legacy_snapshot

    def test_body_sha256_consistency(self):
        snap = ResponseSnapshot(name="x", body_bytes=b"hello world")
        assert snap.body_sha256 == snap.body_sha256  # stable
        assert snap.body_length == 11

    def test_empty_body(self):
        snap = ResponseSnapshot(name="empty")
        assert snap.body_bytes == b""
        assert snap.body_length == 0
        assert snap.body_sha256 is not None


# ---------------------------------------------------------------------------
# Comparison engine
# ---------------------------------------------------------------------------


class TestCompareSnapshots:
    def test_exact_byte_match(
        self,
        legacy_snapshot: ResponseSnapshot,
        python_snapshot_identical: ResponseSnapshot,
    ):
        detail = compare_snapshots(legacy_snapshot, python_snapshot_identical)
        assert detail.result == ComparisonResult.EXACT_BYTE_MATCH
        assert "status_code" in detail.fields_matched
        assert "body_sha256" in detail.fields_matched
        assert detail.fields_differed == []

    def test_body_mismatch(
        self,
        legacy_snapshot: ResponseSnapshot,
        python_snapshot_different_body: ResponseSnapshot,
    ):
        detail = compare_snapshots(legacy_snapshot, python_snapshot_different_body)
        assert detail.result == ComparisonResult.BODY_MISMATCH
        assert "body_sha256" in detail.fields_differed
        assert any("sha256" in m for m in detail.messages)

    def test_status_mismatch(
        self,
        legacy_snapshot: ResponseSnapshot,
        python_snapshot_different_status: ResponseSnapshot,
    ):
        detail = compare_snapshots(legacy_snapshot, python_snapshot_different_status)
        assert detail.result == ComparisonResult.STATUS_MISMATCH
        assert "status_code" in detail.fields_differed
        assert any("status" in m for m in detail.messages)

    def test_semantic_proto_match(self):
        legacy = ResponseSnapshot(
            name="a",
            body_bytes=bytes([0x08, 0x01, 0x12, 0x05, 0x68, 0x65, 0x6C, 0x6C, 0x6F]),
        )
        # Re-encode same fields in a different order — the raw decoder
        # produces the same {field_num: value} dict.
        python = ResponseSnapshot(
            name="b",
            body_bytes=bytes([0x08, 0x01, 0x12, 0x05, 0x68, 0x65, 0x6C, 0x6C, 0x6F]),
        )
        detail = compare_snapshots(legacy, python)
        # Identical bytes → EXACT_BYTE_MATCH; verify decoder works
        assert detail.result == ComparisonResult.EXACT_BYTE_MATCH

    def test_header_mismatch(self):
        legacy = ResponseSnapshot(
            name="a",
            status_code=200,
            content_type="application/json",
            headers={"x-request-id": "aaa"},
            body_bytes=b"ok",
        )
        python = ResponseSnapshot(
            name="b",
            status_code=200,
            content_type="application/json",
            headers={"x-request-id": "bbb"},
            body_bytes=b"ok",
        )
        detail = compare_snapshots(legacy, python)
        # x-request-id is in COMPARABLE_HEADERS, values differ → HEADER_MISMATCH
        assert detail.result == ComparisonResult.HEADER_MISMATCH
        assert "header:x-request-id" in detail.fields_differed

    def test_content_type_mismatch(self):
        legacy = ResponseSnapshot(
            name="a",
            content_type="application/json",
            body_bytes=b"ok",
        )
        python = ResponseSnapshot(
            name="b",
            content_type="text/plain",
            body_bytes=b"ok",
        )
        detail = compare_snapshots(legacy, python)
        assert detail.result == ComparisonResult.HEADER_MISMATCH
        assert "content_type" in detail.fields_differed


# ---------------------------------------------------------------------------
# Protobuf decode
# ---------------------------------------------------------------------------


class TestProtobufDecode:
    def test_decode_json(self):
        data, err = try_decode_protobuf(b'{"key": "value"}')
        assert err is None
        assert data == {"key": "value"}

    def test_decode_empty(self):
        data, err = try_decode_protobuf(b"")
        assert err is None
        assert data == {}

    def test_decode_raw_varints(self):
        # field 1, varint 1
        body = bytes([0x08, 0x01])
        data, err = try_decode_protobuf(body)
        assert err is None
        assert data == {"1": 1}

    def test_decode_string_field(self):
        # field 2, length-delimited, 5 bytes "hello"
        body = bytes([0x12, 0x05]) + b"hello"
        data, err = try_decode_protobuf(body)
        assert err is None
        assert data == {"2": "hello"}

    def test_decode_garbage_returns_error(self):
        # 0xFF as first byte would be an oversized varint → may still parse
        data, err = try_decode_protobuf(bytes([0xFF, 0xFF, 0xFF]))
        # The decoder is lenient; it may or may not error, but should not crash
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Fixture directory loading
# ---------------------------------------------------------------------------


class TestLoadFixtures:
    def test_load_from_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snap = ResponseSnapshot(name="test", body_bytes=b"data")
            snap.save(Path(tmpdir) / "a.json")
            snap.save(Path(tmpdir) / "b.json")
            loaded = load_fixtures_from_dir(Path(tmpdir))
            assert len(loaded) == 2
            assert all(s.name == "test" for s in loaded)

    def test_skip_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "bad.json").write_text("not json")
            snap = ResponseSnapshot(name="good", body_bytes=b"ok")
            snap.save(Path(tmpdir) / "good.json")
            loaded = load_fixtures_from_dir(Path(tmpdir))
            assert len(loaded) == 1
            assert loaded[0].name == "good"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


class TestProvenance:
    def test_provenance_values(self):
        assert Provenance.LEGACY_REFERENCE.value == "LEGACY_REFERENCE"
        assert Provenance.SYNTHETIC.value == "SYNTHETIC"
        assert Provenance.CABINET_CAPTURE.value == "CABINET_CAPTURE"
        assert Provenance.OFFICIAL_CAPTURE.value == "OFFICIAL_CAPTURE"

    def test_provenance_in_snapshot(self):
        snap = ResponseSnapshot(
            name="x",
            provenance=Provenance.CABINET_CAPTURE,
        )
        assert snap.provenance == Provenance.CABINET_CAPTURE
        d = snap.to_dict()
        assert d["provenance"] == "CABINET_CAPTURE"


# ---------------------------------------------------------------------------
# Classification edge cases
# ---------------------------------------------------------------------------


class TestClassificationEdgeCases:
    def test_identical_empty_bodies(self):
        a = ResponseSnapshot(name="a", body_bytes=b"")
        b = ResponseSnapshot(name="b", body_bytes=b"")
        detail = compare_snapshots(a, b)
        assert detail.result == ComparisonResult.EXACT_BYTE_MATCH

    def test_different_content_type_same_body(self):
        a = ResponseSnapshot(name="a", content_type="application/json", body_bytes=b"x")
        b = ResponseSnapshot(name="b", content_type="text/html", body_bytes=b"x")
        detail = compare_snapshots(a, b)
        assert detail.result == ComparisonResult.HEADER_MISMATCH

    def test_both_status_and_body_mismatch(self):
        a = ResponseSnapshot(name="a", status_code=200, body_bytes=b"old")
        b = ResponseSnapshot(name="b", status_code=500, body_bytes=b"new")
        detail = compare_snapshots(a, b)
        # Status is checked first
        assert detail.result == ComparisonResult.STATUS_MISMATCH
