"""Tests for app.logging_config – structured logging configuration."""

import json
import logging

from app.logging_config import (
    REDACTED_FIELDS,
    HumanFormatter,
    JSONFormatter,
    _redact,
    request_id_var,
    setup_logging,
)


class TestRedact:
    def test_redact_dict_with_secret(self):
        data = {"password": "hunter2", "name": "alice"}
        result = _redact(data)
        assert result["password"] == "***"
        assert result["name"] == "alice"

    def test_redact_nested_dict(self):
        data = {"outer": {"token": "abc123", "safe": "ok"}}
        result = _redact(data)
        assert result["outer"]["token"] == "***"
        assert result["outer"]["safe"] == "ok"

    def test_redact_list(self):
        data = [{"password": "p1"}, {"name": "n1"}]
        result = _redact(data)
        assert result[0]["password"] == "***"
        assert result[1]["name"] == "n1"

    def test_redact_passthrough(self):
        assert _redact("hello") == "hello"
        assert _redact(42) == 42
        assert _redact(None) is None

    def test_redact_cookie(self):
        assert _redact({"cookie": "session=abc"}) == {"cookie": "***"}

    def test_redact_authorization(self):
        assert _redact({"authorization": "Bearer xyz"}) == {"authorization": "***"}

    def test_redact_x_galaxy_api_id(self):
        assert _redact({"x-galaxy-api-id": "id123"}) == {"x-galaxy-api-id": "***"}

    def test_case_insensitive_redaction(self):
        assert _redact({"Password": "p"}) == {"Password": "***"}
        assert _redact({"TOKEN": "t"}) == {"TOKEN": "***"}

    def test_redacted_fields_set(self):
        expected = {"password", "token", "secret", "authorization", "cookie", "x-galaxy-api-id"}
        assert expected == REDACTED_FIELDS


class TestRequestIdVar:
    def test_default_value(self):
        token = request_id_var.set("test-id")
        try:
            assert request_id_var.get() == "test-id"
        finally:
            request_id_var.reset(token)

    def test_set_and_get(self):
        token = request_id_var.set("abc-123")
        try:
            assert request_id_var.get() == "abc-123"
        finally:
            request_id_var.reset(token)


class TestJSONFormatter:
    def test_format_returns_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"
        assert parsed["msg"] == "test message"
        assert "ts" in parsed

    def test_format_with_request_id(self):
        formatter = JSONFormatter()
        token = request_id_var.set("req-42")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="msg",
                args=(),
                exc_info=None,
            )
            result = formatter.format(record)
            parsed = json.loads(result)
            assert parsed["request_id"] == "req-42"
        finally:
            request_id_var.reset(token)


class TestHumanFormatter:
    def test_format_contains_request_id(self):
        formatter = HumanFormatter(
            fmt=HumanFormatter.FORMAT,
            datefmt=HumanFormatter.DATE_FORMAT,
        )
        token = request_id_var.set("hum-id")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="test",
                args=(),
                exc_info=None,
            )
            result = formatter.format(record)
            assert "hum-id" in result
        finally:
            request_id_var.reset(token)


class TestSetupLogging:
    def test_setup_human_format(self):
        setup_logging(level="DEBUG", json_format=False)
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_setup_json_format(self):
        setup_logging(level="WARNING", json_format=True)
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_removes_existing_handlers(self):
        root = logging.getLogger()
        len(root.handlers)
        setup_logging(level="INFO", json_format=False)
        assert len(root.handlers) == 1
