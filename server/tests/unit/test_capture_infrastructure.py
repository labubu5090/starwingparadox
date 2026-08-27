"""Tests for Phase 2A capture infrastructure."""

from __future__ import annotations

import pytest

from app.capture import (
    PROVENANCE_REAL_CABINET,
    CaptureConfig,
    CaptureSession,
    HTTPCapture,
    TCPCapture,
    compute_sha256,
    redact_identifier,
)


class TestCaptureConfig:
    """Test capture configuration."""

    def test_default_config(self):
        config = CaptureConfig()
        assert config.enabled is False
        assert config.raw_enabled is False
        assert config.redact_identifiers is True

    def test_from_env_disabled(self, monkeypatch):
        monkeypatch.delenv("CAPTURE_ENABLED", raising=False)
        config = CaptureConfig.from_env()
        assert config.enabled is False

    def test_from_env_enabled(self, monkeypatch):
        monkeypatch.setenv("CAPTURE_ENABLED", "true")
        config = CaptureConfig.from_env()
        assert config.enabled is True


class TestHTTPCapture:
    """Test HTTP capture dataclass."""

    def test_creation(self):
        cap = HTTPCapture(
            method="POST",
            path="/player/profile",
            response_status=200,
        )
        assert cap.capture_id
        assert cap.method == "POST"
        assert cap.response_status == 200
        assert cap.provenance == PROVENANCE_REAL_CABINET

    def test_defaults(self):
        cap = HTTPCapture()
        assert cap.session_id == ""
        assert cap.request_byte_length == 0
        assert cap.database_effect == "NO_DATABASE_EFFECT"


class TestTCPCapture:
    """Test TCP capture dataclass."""

    def test_creation(self):
        cap = TCPCapture(
            message_type=0x66,
            declared_length=10,
            received_length=10,
        )
        assert cap.capture_id
        assert cap.message_type == 0x66
        assert cap.declared_length == 10


class TestCaptureSession:
    """Test capture session management."""

    def test_session_start_creates_directories(self, tmp_path):
        config = CaptureConfig(
            enabled=True,
            capture_dir=str(tmp_path / "captures"),
        )
        session = CaptureSession("test_session", config)
        session_dir = session.start()

        assert session_dir.exists()
        assert (session_dir / "http").is_dir()
        assert (session_dir / "tcp").is_dir()
        assert (session_dir / "raw").is_dir()
        assert (session_dir / "session_metadata.json").exists()

    def test_session_disabled_raises(self):
        config = CaptureConfig(enabled=False)
        session = CaptureSession("test", config)
        with pytest.raises(RuntimeError, match="disabled"):
            session.start()

    def test_session_stop_returns_summary(self, tmp_path):
        config = CaptureConfig(
            enabled=True,
            capture_dir=str(tmp_path / "captures"),
        )
        session = CaptureSession("test_stop", config)
        session.start()
        session.record_http(HTTPCapture(method="GET", path="/health"))
        session.record_tcp(TCPCapture(message_type=0x66))

        summary = session.stop()
        assert summary["http_captures"] == 1
        assert summary["tcp_captures"] == 1
        assert summary["stopped_at"] is not None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_compute_sha256(self):
        result = compute_sha256(b"hello world")
        assert len(result) == 64
        assert result == compute_sha256(b"hello world")

    def test_redact_identifier(self):
        result = redact_identifier("1234567890", visible_chars=3)
        assert result.startswith("123")
        assert result.endswith("890")
        assert "***" in result

    def test_redact_short_identifier(self):
        result = redact_identifier("ab", visible_chars=3)
        assert result == "**"
