"""Unit tests for database safety guard logic.

Tests that the safety rules encoded in the SQLite configuration
and Python configuration would prevent dangerous operations. These tests
validate the safety logic WITHOUT requiring a real database connection.

Safety rules extracted from:
- server/app/config.py
- server/app/dependencies.py
"""

from __future__ import annotations

from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Safety rule constants
# ---------------------------------------------------------------------------

FORBIDDEN_DATABASE_NAMES = {"postgres", "template0", "template1"}

DATABASE_NAME_SUFFIX = "_test"

PRODUCTION_LOOKING_PATTERNS = [
    "paradox",
    "starwing_prod",
    "production",
    "staging",
    "master",
    "main",
    "live",
    "real",
]

REMOTE_HOST_PATTERNS = [
    r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",  # IP addresses
    r"\.",  # Any dot means likely a hostname, not localhost
]

SUPPORTED_DRIVERS = {
    "sqlite+aiosqlite",
    "sqlite",
}

SUPPORTED_DRIVER_PREFIXES = ("sqlite",)

FORBIDDEN_SCHEMES = {
    "postgresql",
    "postgresql+psycopg",
    "postgresql+asyncpg",
    "postgresql+psycopg2",
    "postgresql+pg8000",
    "mysql",
    "mssql",
    "oracle",
}


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_database_name(name: str) -> tuple[bool, str]:
    """Validate database name against safety rules.

    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Database name must not be empty"

    if name in FORBIDDEN_DATABASE_NAMES:
        return False, f"Refusing to operate on forbidden database: {name}"

    for pattern in PRODUCTION_LOOKING_PATTERNS:
        name_without_suffix = (
            name[: -len(DATABASE_NAME_SUFFIX)] if name.endswith(DATABASE_NAME_SUFFIX) else name
        )
        if pattern in name_without_suffix.lower():
            return False, f"Database name looks production-like: {name}"

    return True, ""


def validate_database_url(url: str) -> tuple[bool, str]:
    """Validate database URL against safety rules.

    SQLite is the only supported backend.

    Returns:
        (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "DATABASE_URL must not be empty"

    try:
        parsed = urlparse(url)
    except Exception:
        return False, f"Cannot parse database URL: {url}"

    scheme = parsed.scheme.lower()

    # Reject non-SQLite schemes
    if scheme in FORBIDDEN_SCHEMES:
        return False, f"PostgreSQL is not supported. Only SQLite is allowed. Got: {scheme}://"

    if not any(scheme.startswith(p) for p in SUPPORTED_DRIVER_PREFIXES):
        return False, f"Unsupported database driver: {scheme}"

    # SQLite URLs: check for network hosts
    if scheme.startswith("sqlite"):
        if parsed.hostname and parsed.hostname not in ("", "localhost"):
            return False, f"SQLite database must be local. Got host: {parsed.hostname}"
        return True, ""

    return False, f"Unsupported database driver: {scheme}"


def validate_host(host: str, approved_remotes: list[str] | None = None) -> tuple[bool, str]:
    """Validate database host against safety rules.

    For SQLite, this checks that no remote host is specified.

    Returns:
        (is_valid, error_message)
    """
    if not host or not host.strip():
        return False, "Host must not be empty"

    # localhost and 127.0.0.1 are always allowed
    if host.lower() in ("localhost", "127.0.0.1", "::1", ""):
        return True, ""

    # For SQLite, any non-localhost host is rejected
    return False, f"SQLite database must be local. Got host: {host}"


def is_test_database(name: str) -> bool:
    """Check if a database name looks like a test database."""
    return name.endswith(DATABASE_NAME_SUFFIX)


def validate_test_database_url(url: str) -> tuple[bool, str]:
    """Validate that a test database URL is safe.

    Returns:
        (is_valid, error_message)
    """
    is_valid, msg = validate_database_url(url)
    if not is_valid:
        return False, msg

    parsed = urlparse(url)
    if parsed.scheme.startswith("sqlite"):
        return True, ""

    db_name = parsed.path.lstrip("/")
    if not db_name:
        return False, "Missing database name in URL path"

    if not is_test_database(db_name):
        return False, f"Test database must end with '_test': {db_name}"

    return validate_database_name(db_name)


def validate_no_remote_host(url: str) -> tuple[bool, str]:
    """Validate that a URL does not point to a remote host."""
    parsed = urlparse(url)
    if parsed.hostname and parsed.hostname not in ("", "localhost", "127.0.0.1", "::1"):
        return False, f"Remote host not allowed: {parsed.hostname}"
    return True, ""


def validate_unc_path(path: str) -> tuple[bool, str]:
    """Validate that a path is not a UNC path."""
    if path.startswith("\\\\") or path.startswith("//"):
        return False, f"UNC paths are not allowed: {path}"
    return True, ""


def validate_no_network_share(path: str) -> tuple[bool, str]:
    """Validate that a path is not on a network share."""
    if "\\\\" in path or "//" in path:
        return False, f"Network share paths are not allowed: {path}"
    return True, ""


# ---------------------------------------------------------------------------
# PostgreSQL rejection tests
# ---------------------------------------------------------------------------


class TestPostgreSQLRejection:
    """Verify PostgreSQL URLs are rejected."""

    def test_postgresql_psycopg_rejected(self):
        """postgresql+psycopg must be rejected."""
        valid, msg = validate_database_url("postgresql+psycopg://u:p@localhost:5432/db_test")
        assert not valid
        assert "SQLite" in msg or "not supported" in msg.lower()

    def test_postgresql_asyncpg_rejected(self):
        """postgresql+asyncpg must be rejected."""
        valid, msg = validate_database_url("postgresql+asyncpg://u:p@localhost:5432/db_test")
        assert not valid

    def test_postgresql_plain_rejected(self):
        """postgresql (plain) must be rejected."""
        valid, msg = validate_database_url("postgresql://u:p@localhost:5432/db_test")
        assert not valid

    def test_mysql_rejected(self):
        """mysql must be rejected."""
        valid, msg = validate_database_url("mysql://u:p@localhost:3306/db_test")
        assert not valid

    def test_mssql_rejected(self):
        """mssql must be rejected."""
        valid, msg = validate_database_url("mssql://u:p@localhost:1433/db_test")
        assert not valid


# ---------------------------------------------------------------------------
# SQLite acceptance tests
# ---------------------------------------------------------------------------


class TestSQLiteAcceptance:
    """Verify SQLite URLs are accepted."""

    def test_sqlite_aiosqlite_accepted(self):
        """sqlite+aiosqlite is accepted."""
        valid, _ = validate_database_url("sqlite+aiosqlite:///./data/test.db")
        assert valid

    def test_sqlite_plain_accepted(self):
        """sqlite (plain) is accepted."""
        valid, _ = validate_database_url("sqlite:///./data/test.db")
        assert valid

    def test_sqlite_memory_accepted(self):
        """sqlite+aiosqlite:///:memory: is accepted."""
        valid, _ = validate_database_url("sqlite+aiosqlite:///:memory:")
        assert valid

    def test_sqlite_network_host_rejected(self):
        """SQLite with remote host is rejected."""
        valid, msg = validate_database_url("sqlite+aiosqlite://remote-host/data/test.db")
        assert not valid
        assert "local" in msg.lower() or "host" in msg.lower()


# ---------------------------------------------------------------------------
# URL validation tests
# ---------------------------------------------------------------------------


class TestURLValidation:
    """Test URL validation logic."""

    def test_empty_url_rejected(self):
        """Empty URL should be rejected."""
        valid, msg = validate_database_url("")
        assert not valid

    def test_none_like_url_rejected(self):
        """Whitespace-only URL should be rejected."""
        valid, msg = validate_database_url("   ")
        assert not valid

    def test_valid_sqlite_url(self):
        """Valid SQLite URL should pass."""
        valid, _ = validate_database_url("sqlite+aiosqlite:///./data/test.db")
        assert valid

    def test_unsupported_driver_rejected(self):
        """Unsupported driver should be rejected."""
        valid, msg = validate_database_url("oracle://u:p@host/db")
        assert not valid


# ---------------------------------------------------------------------------
# Host validation tests
# ---------------------------------------------------------------------------


class TestHostValidation:
    """Test host validation logic."""

    def test_localhost_accepted(self):
        """localhost is always accepted."""
        valid, _ = validate_host("localhost")
        assert valid

    def test_127_0_0_1_accepted(self):
        """127.0.0.1 is always accepted."""
        valid, _ = validate_host("127.0.0.1")
        assert valid

    def test_empty_rejected(self):
        """Empty host is rejected."""
        valid, _ = validate_host("")
        assert not valid

    def test_remote_rejected(self):
        """Remote host is rejected for SQLite."""
        valid, msg = validate_host("remote.server.com")
        assert not valid


# ---------------------------------------------------------------------------
# UNC path tests
# ---------------------------------------------------------------------------


class TestUNCPathValidation:
    """Test UNC path rejection."""

    def test_unc_path_rejected(self):
        """UNC paths must be rejected."""
        valid, msg = validate_unc_path("\\\\server\\share\\db")
        assert not valid

    def test_forward_slash_unc_rejected(self):
        """Forward-slash UNC paths must be rejected."""
        valid, msg = validate_unc_path("//server/share/db")
        assert not valid

    def test_local_path_accepted(self):
        """Local paths must be accepted."""
        valid, _ = validate_unc_path("C:\\data\\test.db")
        assert valid


# ---------------------------------------------------------------------------
# Test database URL tests
# ---------------------------------------------------------------------------


class TestTestDatabaseURL:
    """Test database URL validation."""

    def test_valid_test_url(self):
        """Valid test URL should pass."""
        valid, _ = validate_test_database_url("sqlite+aiosqlite:///./data/test.db")
        assert valid

    def test_postgresql_test_url_rejected(self):
        """PostgreSQL test URL should be rejected."""
        valid, _ = validate_test_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/starwing_test"
        )
        assert not valid
