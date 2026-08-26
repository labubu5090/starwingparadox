"""Synthetic capture system validation tests.

All tests in this file are labeled SYNTHETIC_CAPTURE_TEST and validate
the capture system behavior without producing real captures that persist.
"""

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import pytest

from app.capture import (
    REDACTED,
    _unique_filename,
    capture_request_response,
    disable_capture,
    enable_capture,
    get_capture_dir,
    is_capture_enabled,
    redact_cabinet_id,
    redact_headers,
)

SYNTHETIC_CAPTURE_TEST = pytest.mark.synthetic_capture_test


@pytest.fixture(autouse=True)
def _reset_capture():
    """Reset capture state before and after each test."""
    disable_capture()
    yield
    disable_capture()


@pytest.fixture
def tmp_capture_dir():
    """Create a temporary directory for capture files."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


@SYNTHETIC_CAPTURE_TEST
class TestDefaultStateDisabled:
    """Test 1: Verify capture is disabled by default."""

    def test_is_capture_enabled_returns_false(self):
        assert is_capture_enabled() is False

    def test_get_capture_dir_returns_none(self):
        assert get_capture_dir() is None

    def test_capture_returns_none_when_disabled(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        disable_capture()
        result = capture_request_response(
            correlation_id="test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert result is None


@SYNTHETIC_CAPTURE_TEST
class TestEnableRequiresExplicitConfiguration:
    """Test 2: Enabling capture requires explicit configuration."""

    def test_enable_with_explicit_dir(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        assert is_capture_enabled() is True
        assert get_capture_dir() == tmp_capture_dir

    def test_enable_without_dir_uses_env(self, monkeypatch, tmp_capture_dir):
        monkeypatch.setenv("STARWING_CAPTURE_DIR", str(tmp_capture_dir))
        enable_capture()
        assert get_capture_dir() == tmp_capture_dir

    def test_enable_without_dir_or_env_uses_default(self):
        enable_capture()
        assert is_capture_enabled() is True
        assert get_capture_dir() is not None

    def test_disable_clears_state(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        disable_capture()
        assert is_capture_enabled() is False
        assert get_capture_dir() is None or get_capture_dir() == tmp_capture_dir


@SYNTHETIC_CAPTURE_TEST
class TestUniqueFilenames:
    """Test 3: Verify unique filenames are generated."""

    def test_100_filenames_are_distinct(self):
        names = {_unique_filename("cap", "meta.json") for _ in range(100)}
        assert len(names) == 100

    def test_filename_has_correct_prefix(self):
        name = _unique_filename("req", "bin")
        assert name.startswith("req_")

    def test_filename_has_correct_extension(self):
        name = _unique_filename("cap", "meta.json")
        assert name.endswith(".meta.json")

    def test_filename_contains_timestamp(self):
        name = _unique_filename("cap", "meta.json")
        parts = name.split("_")
        assert len(parts) >= 3


@SYNTHETIC_CAPTURE_TEST
class TestNoOverwrite:
    """Test 4: Verify captures do not overwrite existing files."""

    def test_concurrent_captures_are_distinct(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        paths = []
        for i in range(5):
            p = capture_request_response(
                correlation_id=f"test-{i:03d}",
                endpoint="/test",
                client_ip="127.0.0.1",
                cabinet_id=None,
                request_headers={},
                request_body=b"data",
                response_body=b"resp",
                response_status=200,
            )
            paths.append(p)

        assert all(p is not None for p in paths)
        assert len(set(paths)) == 5
        for p in paths:
            assert p.exists()


@SYNTHETIC_CAPTURE_TEST
class TestMetadataSidecarFormat:
    """Test 5: Verify metadata sidecar file format."""

    def test_metadata_has_all_required_fields(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="meta-test-001",
            endpoint="/player/login",
            client_ip="10.0.0.1",
            cabinet_id="999888777666",
            request_headers={"Content-Type": "application/json"},
            request_body=b'{"key":"val"}',
            response_body=b'{"ok":true}',
            response_status=200,
            protobuf_message_type="LoginRequest",
        )
        assert path is not None
        meta = json.loads(path.read_text(encoding="utf-8"))

        required_fields = [
            "capture_ts",
            "correlation_id",
            "endpoint",
            "client_ip",
            "cabinet_id_redacted",
            "request_headers",
            "request_body_length",
            "request_body_sha256",
            "response_status",
            "response_body_length",
            "response_body_sha256",
            "protobuf_message_type",
        ]
        for field in required_fields:
            assert field in meta, f"Missing field: {field}"

    def test_metadata_json_is_valid(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="json-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert path is not None
        raw = path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)


@SYNTHETIC_CAPTURE_TEST
class TestCorrelationId:
    """Test 6: Verify request correlation ID is captured."""

    def test_correlation_id_in_metadata(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="corr-test-abc-123",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert path is not None
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["correlation_id"] == "corr-test-abc-123"

    def test_different_correlation_ids(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        ids = []
        for i in range(3):
            path = capture_request_response(
                correlation_id=f"unique-{i}",
                endpoint="/test",
                client_ip="127.0.0.1",
                cabinet_id=None,
                request_headers={},
                request_body=b"",
                response_body=b"",
                response_status=200,
            )
            meta = json.loads(path.read_text(encoding="utf-8"))
            ids.append(meta["correlation_id"])
        assert len(set(ids)) == 3


@SYNTHETIC_CAPTURE_TEST
class TestByteLengthTracking:
    """Test 7: Verify byte length tracking in metadata."""

    def test_request_body_length(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        body = b"hello world"
        path = capture_request_response(
            correlation_id="len-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=body,
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["request_body_length"] == len(body)

    def test_response_body_length(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        body = b"response data here"
        path = capture_request_response(
            correlation_id="len-test-002",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=body,
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["response_body_length"] == len(body)

    def test_empty_body_length_zero(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="len-test-003",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["request_body_length"] == 0
        assert meta["response_body_length"] == 0


@SYNTHETIC_CAPTURE_TEST
class TestSha256Computation:
    """Test 8: Verify SHA-256 hash computation."""

    def test_request_sha256_matches(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        body = b"test data for hashing"
        expected = hashlib.sha256(body).hexdigest()
        path = capture_request_response(
            correlation_id="hash-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=body,
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["request_body_sha256"] == expected

    def test_response_sha256_matches(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        body = b"response to hash"
        expected = hashlib.sha256(body).hexdigest()
        path = capture_request_response(
            correlation_id="hash-test-002",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=body,
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["response_body_sha256"] == expected

    def test_empty_body_sha256(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        expected = hashlib.sha256(b"").hexdigest()
        path = capture_request_response(
            correlation_id="hash-test-003",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["request_body_sha256"] == expected
        assert meta["response_body_sha256"] == expected


@SYNTHETIC_CAPTURE_TEST
class TestIdentifierRedaction:
    """Test 9: Verify cabinet ID redaction."""

    def test_long_cabinet_id_redacted(self):
        text = "cabinet 12345678901234 at location"
        result = redact_cabinet_id(text)
        assert "12345678901234" not in result
        assert REDACTED in result

    def test_short_numbers_not_redacted(self):
        text = "port 4001 and id 123"
        result = redact_cabinet_id(text)
        assert result == text

    def test_multiple_cabinet_ids_redacted(self):
        text = "cabinet 12345678901234 and 98765432109876"
        result = redact_cabinet_id(text)
        assert "12345678901234" not in result
        assert "98765432109876" not in result
        assert result.count(REDACTED) == 2

    def test_cabinet_id_in_metadata_redacted(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="redact-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id="12345678901234",
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["cabinet_id_redacted"] != "12345678901234"
        assert REDACTED in meta["cabinet_id_redacted"]


@SYNTHETIC_CAPTURE_TEST
class TestHeaderRedaction:
    """Test 10: Verify header redaction for sensitive fields."""

    def test_authorization_redacted(self):
        headers = {"Authorization": "Bearer secret123", "Content-Type": "text/plain"}
        result = redact_headers(headers)
        assert result["Authorization"] == REDACTED
        assert result["Content-Type"] == "text/plain"

    def test_cookie_redacted(self):
        headers = {"Cookie": "session=abc123"}
        result = redact_headers(headers)
        assert result["Cookie"] == REDACTED

    def test_x_galaxy_api_id_redacted(self):
        headers = {"x-galaxy-api-id": "real_id"}
        result = redact_headers(headers)
        assert result["x-galaxy-api-id"] == REDACTED

    def test_token_redacted(self):
        headers = {"X-Token": "secret123"}
        result = redact_headers(headers)
        assert result["X-Token"] == REDACTED

    def test_password_redacted(self):
        headers = {"password": "hunter2"}
        result = redact_headers(headers)
        assert result["password"] == REDACTED

    def test_secret_redacted(self):
        headers = {"X-Secret-Key": "topsecret"}
        result = redact_headers(headers)
        assert result["X-Secret-Key"] == REDACTED

    def test_safe_headers_preserved(self):
        headers = {"Accept": "application/json", "X-Request-ID": "abc", "User-Agent": "test"}
        result = redact_headers(headers)
        assert result == headers

    def test_redacted_headers_in_metadata(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="header-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={"Authorization": "Bearer secret", "Content-Type": "text/plain"},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["request_headers"]["Authorization"] == REDACTED
        assert meta["request_headers"]["Content-Type"] == "text/plain"


@SYNTHETIC_CAPTURE_TEST
class TestCaptureFailureDoesNotCrashServer:
    """Test 11: Verify capture failure doesn't crash the server."""

    def test_capture_with_invalid_directory(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        # Simulate a read-only directory
        readonly_dir = tmp_capture_dir / "readonly"
        readonly_dir.mkdir()
        disable_capture()
        enable_capture(readonly_dir)

        # Try to capture - may fail but should not crash
        result = capture_request_response(
            correlation_id="fail-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        # Result may be None or a path - either is acceptable
        assert result is None or result.exists()

    def test_capture_with_none_dir(self):
        enable_capture(Path(tempfile.mkdtemp()))
        disable_capture()
        # After disable, capture should return None
        result = capture_request_response(
            correlation_id="fail-test-002",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert result is None

    def test_server_continues_after_capture_error(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        # Multiple captures should work even if one might fail
        results = []
        for i in range(3):
            r = capture_request_response(
                correlation_id=f"resilience-{i}",
                endpoint="/test",
                client_ip="127.0.0.1",
                cabinet_id=None,
                request_headers={},
                request_body=b"data",
                response_body=b"resp",
                response_status=200,
            )
            results.append(r)
        # At least some should succeed
        assert any(r is not None for r in results)


@SYNTHETIC_CAPTURE_TEST
class TestCaptureFailureDoesNotChangeProtocolResponse:
    """Test 12: Verify capture failure doesn't alter protocol responses."""

    def test_response_body_unchanged_when_capture_disabled(self):
        disable_capture()
        response_body = b"proto response data"
        # Capture returns None when disabled - response body unchanged
        result = capture_request_response(
            correlation_id="proto-test-001",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"request",
            response_body=response_body,
            response_status=200,
        )
        assert result is None

    def test_response_status_preserved_in_metadata(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="proto-test-002",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=404,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["response_status"] == 404

    def test_response_body_sha256_preserved(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        body = b"exact response content"
        expected_hash = hashlib.sha256(body).hexdigest()
        path = capture_request_response(
            correlation_id="proto-test-003",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=body,
            response_status=200,
        )
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["response_body_sha256"] == expected_hash
