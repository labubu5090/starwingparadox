"""Tests for app.capture – raw capture mode."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from app.capture import (
    REDACTED,
    _hash_bytes,
    _unique_filename,
    capture_request_response,
    disable_capture,
    enable_capture,
    get_capture_dir,
    is_capture_enabled,
    redact_cabinet_id,
    redact_headers,
)


@pytest.fixture(autouse=True)
def _reset_capture():
    """Reset capture state before and after each test."""
    disable_capture()
    yield
    disable_capture()


@pytest.fixture
def tmp_capture_dir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestCaptureDisabledByDefault:
    def test_is_capture_enabled_returns_false(self):
        assert is_capture_enabled() is False

    def test_get_capture_dir_returns_none(self):
        assert get_capture_dir() is None

    def test_capture_request_response_returns_none(self):
        result = capture_request_response(
            correlation_id="abc",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert result is None


class TestEnableDisable:
    def test_enable_sets_enabled(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        assert is_capture_enabled() is True
        assert get_capture_dir() == tmp_capture_dir

    def test_disable_clears_enabled(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        disable_capture()
        assert is_capture_enabled() is False

    def test_enable_creates_directory(self):
        d = Path(tempfile.mkdtemp()) / "sub" / "dir"
        try:
            enable_capture(d)
            assert d.exists()
        finally:
            shutil.rmtree(d.parent, ignore_errors=True)

    def test_enable_default_dir_from_env(self, monkeypatch, tmp_capture_dir):
        monkeypatch.setenv("STARWING_CAPTURE_DIR", str(tmp_capture_dir))
        enable_capture()
        assert get_capture_dir() == tmp_capture_dir


class TestFilenameUniqueness:
    def test_unique_filenames_are_distinct(self):
        names = {_unique_filename("cap", "meta.json") for _ in range(100)}
        assert len(names) == 100

    def test_filename_contains_prefix(self):
        name = _unique_filename("req", "bin")
        assert name.startswith("req_")

    def test_filename_contains_extension(self):
        name = _unique_filename("cap", "meta.json")
        assert name.endswith(".meta.json")


class TestRedactSecrets:
    def test_redact_authorization(self):
        headers = {"Authorization": "Bearer tok123", "Content-Type": "application/json"}
        result = redact_headers(headers)
        assert result["Authorization"] == REDACTED
        assert result["Content-Type"] == "application/json"

    def test_redact_cookie(self):
        headers = {"Cookie": "session=abc"}
        result = redact_headers(headers)
        assert result["Cookie"] == REDACTED

    def test_redact_x_galaxy_api_id(self):
        headers = {"x-galaxy-api-id": "real_id"}
        result = redact_headers(headers)
        assert result["x-galaxy-api-id"] == REDACTED

    def test_redact_token(self):
        headers = {"X-Token": "secret123"}
        result = redact_headers(headers)
        assert result["X-Token"] == REDACTED

    def test_redact_password(self):
        headers = {"password": "hunter2"}
        result = redact_headers(headers)
        assert result["password"] == REDACTED

    def test_no_redact_safe_headers(self):
        headers = {"Accept": "application/json", "X-Request-ID": "abc"}
        result = redact_headers(headers)
        assert result == headers

    def test_redact_cabinet_id(self):
        text = "cabinet 12345678901234 at location"
        result = redact_cabinet_id(text)
        assert "12345678901234" not in result
        assert REDACTED in result

    def test_no_redact_short_numbers(self):
        text = "port 4001 and id 123"
        result = redact_cabinet_id(text)
        assert result == text


class TestCorrelationIdGeneration:
    def test_capture_writes_correlation_id(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="test-corr-123",
            endpoint="/player/login",
            client_ip="192.168.1.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"",
            response_body=b"",
            response_status=200,
        )
        assert path is not None
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["correlation_id"] == "test-corr-123"


class TestMetadataSidecarFormat:
    def test_metadata_has_required_fields(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="cid-1",
            endpoint="/test",
            client_ip="10.0.0.1",
            cabinet_id="999888777666",
            request_headers={"Content-Type": "application/json"},
            request_body=b'{"key":"val"}',
            response_body=b'{"ok":true}',
            response_status=200,
            protobuf_message_type="Ping",
        )
        assert path is not None
        meta = json.loads(path.read_text(encoding="utf-8"))
        assert meta["capture_ts"]
        assert meta["correlation_id"] == "cid-1"
        assert meta["endpoint"] == "/test"
        assert meta["client_ip"] == "10.0.0.1"
        assert meta["cabinet_id_redacted"] != "999888777666"
        assert meta["request_body_length"] == 13
        assert meta["request_body_sha256"] == _hash_bytes(b'{"key":"val"}')
        assert meta["response_status"] == 200
        assert meta["response_body_length"] == 11
        assert meta["response_body_sha256"] == _hash_bytes(b'{"ok":true}')
        assert meta["protobuf_message_type"] == "Ping"

    def test_metadata_json_is_valid(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        path = capture_request_response(
            correlation_id="cid-2",
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


class TestNoOverwrite:
    def test_concurrent_captures_do_not_overwrite(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        paths = []
        for _ in range(5):
            p = capture_request_response(
                correlation_id="same",
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


class TestRawBytesControlled:
    def test_no_raw_files_when_disabled(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        capture_request_response(
            correlation_id="cid",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"request data",
            response_body=b"response data",
            response_status=200,
            include_raw_request=False,
            include_raw_response=False,
        )
        bin_files = list(tmp_capture_dir.glob("*.bin"))
        assert len(bin_files) == 0

    def test_raw_files_when_enabled(self, tmp_capture_dir):
        enable_capture(tmp_capture_dir)
        capture_request_response(
            correlation_id="cid",
            endpoint="/test",
            client_ip="127.0.0.1",
            cabinet_id=None,
            request_headers={},
            request_body=b"request data",
            response_body=b"response data",
            response_status=200,
            include_raw_request=True,
            include_raw_response=True,
        )
        req_files = list(tmp_capture_dir.glob("*.req.bin"))
        resp_files = list(tmp_capture_dir.glob("*.resp.bin"))
        assert len(req_files) == 1
        assert len(resp_files) == 1
        assert req_files[0].read_bytes() == b"request data"
        assert resp_files[0].read_bytes() == b"response data"


class TestRetentionWarning:
    def test_enable_logs_warning(self, tmp_capture_dir, caplog):
        import logging

        with caplog.at_level(logging.WARNING, logger="app.capture"):
            enable_capture(tmp_capture_dir)
        assert "Capture ENABLED" in caplog.text

    def test_disable_logs_warning(self, tmp_capture_dir, caplog):
        import logging

        enable_capture(tmp_capture_dir)
        with caplog.at_level(logging.WARNING, logger="app.capture"):
            disable_capture()
        assert "Capture DISABLED" in caplog.text
