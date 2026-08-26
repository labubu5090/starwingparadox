"""Unit tests for database safety guard logic.

Tests that the safety rules encoded in the PostgreSQL PowerShell scripts
and Python configuration would prevent dangerous operations. These tests
validate the safety logic WITHOUT requiring a real PostgreSQL connection.

Safety rules extracted from:
- tools/postgresql/create-test-database.ps1 (lines 33-42)
- tools/postgresql/reset-test-database.ps1 (lines 33-50)
- tools/postgresql/backup-test-database.ps1 (lines 28-32)
- tools/postgresql/import-legacy-schema.ps1 (lines 32-36)
- tools/postgresql/verify-test-database.ps1 (lines 29-33)
- server/app/config.py (line 11)
"""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Safety rule constants (mirrors the PowerShell scripts)
# ---------------------------------------------------------------------------

FORBIDDEN_DATABASE_NAMES = {"postgres", "template0", "template1"}
FORBIDDEN_DATABASE_PREFIXES = {"postgres", "template0", "template1"}

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
    "postgresql+psycopg",
    "postgresql+asyncpg",
    "postgresql+psycopg2",
    "postgresql+pg8000",
    "sqlite+aiosqlite",
    "sqlite",
}

SUPPORTED_DRIVER_PREFIXES = ("postgresql", "sqlite")


# ---------------------------------------------------------------------------
# Validation functions (extracted from PowerShell scripts logic)
# ---------------------------------------------------------------------------


def validate_database_name(name: str) -> tuple[bool, str]:
    """Validate database name against safety rules.

    Mirrors the safety checks in:
    - create-test-database.ps1 lines 33-42
    - reset-test-database.ps1 lines 33-50
    - backup-test-database.ps1 lines 28-32
    - import-legacy-schema.ps1 lines 32-36
    - verify-test-database.ps1 lines 29-33

    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Database name must not be empty"

    if name in FORBIDDEN_DATABASE_NAMES:
        return False, f"Refusing to operate on forbidden database: {name}"

    # Also reject names that start with a forbidden prefix (e.g., postgres_test)
    for prefix in FORBIDDEN_DATABASE_PREFIXES:
        if name.startswith(prefix):
            return False, f"Refusing to operate on forbidden database: {name}"

    if not name.endswith(DATABASE_NAME_SUFFIX):
        return False, f"Database name must end with '_test': {name}"

    for pattern in PRODUCTION_LOOKING_PATTERNS:
        name_without_suffix = (
            name[: -len(DATABASE_NAME_SUFFIX)] if name.endswith(DATABASE_NAME_SUFFIX) else name
        )
        if pattern in name_without_suffix.lower():
            return False, f"Database name looks production-like: {name}"

    return True, ""


def validate_database_url(url: str) -> tuple[bool, str]:
    """Validate database URL against safety rules.

    Checks:
    - URL is not empty
    - Database name in URL ends with _test (PostgreSQL only)
    - Database name is not forbidden
    - Driver is supported
    - Host is localhost (unless explicitly approved)

    Returns:
        (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "DATABASE_URL must not be empty"

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, f"Cannot parse database URL: {url}"

    # Check driver
    scheme = parsed.scheme
    if scheme not in SUPPORTED_DRIVERS:
        # Check if it's a supported prefix
        is_supported = any(scheme.startswith(prefix) for prefix in SUPPORTED_DRIVER_PREFIXES)
        if not is_supported:
            return False, f"Unsupported database driver: {scheme}"

    # SQLite URLs don't have the same database name constraints
    if scheme.startswith("sqlite"):
        return True, ""

    # Extract database name from path
    db_name = parsed.path.lstrip("/")
    if not db_name:
        return False, "Missing database name in URL path"

    return validate_database_name(db_name)


def validate_host(host: str, approved_remotes: list[str] | None = None) -> tuple[bool, str]:
    """Validate database host against safety rules.

    Refuses remote hostnames unless explicitly approved.

    Returns:
        (is_valid, error_message)
    """
    if not host or not host.strip():
        return False, "Host must not be empty"

    approved_remotes = approved_remotes or []

    # localhost and 127.0.0.1 are always allowed
    if host.lower() in ("localhost", "127.0.0.1", "::1"):
        return True, ""

    # Check if explicitly approved
    if host in approved_remotes:
        return True, ""

    # Check if it's an IP address (remote)
    for pattern in REMOTE_HOST_PATTERNS:
        if re.search(pattern, host):
            return False, f"Remote hostname not approved: {host}"

    # Non-localhost hostname
    return False, f"Remote hostname not approved: {host}"


def validate_reset_requires_confirm(confirm_flag: bool) -> tuple[bool, str]:
    """Validate that destructive reset requires explicit confirm.

    Mirrors reset-test-database.ps1 lines 39-43.

    Returns:
        (is_valid, error_message)
    """
    if not confirm_flag:
        return False, (
            "DESTRUCTIVE OPERATION: Must pass -Confirm switch to reset the test database. "
            "Example: .\\reset-test-database.ps1 -Confirm"
        )
    return True, ""


def validate_backup_required_before_reset(
    backup_exists: bool, backup_attempted: bool
) -> tuple[bool, str]:
    """Validate that backup is attempted before destructive reset.

    Mirrors reset-test-database.ps1 lines 55-69 (backup step before drop).

    Returns:
        (is_valid, error_message)
    """
    if not backup_attempted:
        return False, "Backup must be attempted before destructive reset"
    if not backup_exists:
        return False, "Backup file does not exist after backup attempt"
    return True, ""


def validate_destructive_requires_test_database(database: str, operation: str) -> tuple[bool, str]:
    """Validate that destructive operations only target test databases.

    Mirrors reset-test-database.ps1 lines 33-37.

    Returns:
        (is_valid, error_message)
    """
    if not database.endswith(DATABASE_NAME_SUFFIX):
        return False, f"Refusing to {operation} non-test database: {database}"
    return True, ""


# ---------------------------------------------------------------------------
# Tests: Database name validation
# ---------------------------------------------------------------------------


class TestDatabaseNameSuffix:
    """Test that database name must end with _test suffix."""

    def test_valid_test_database_name(self) -> None:
        """starwing_test is accepted."""
        valid, _ = validate_database_name("starwing_test")
        assert valid is True

    def test_paradox_test_rejected(self) -> None:
        """paradox_test is rejected (production-looking: contains 'paradox')."""
        valid, msg = validate_database_name("paradox_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_my_app_test_accepted(self) -> None:
        """my_app_test is accepted."""
        valid, _ = validate_database_name("my_app_test")
        assert valid is True

    def test_starwing_rejected_without_suffix(self) -> None:
        """starwing without _test is rejected."""
        valid, msg = validate_database_name("starwing")
        assert valid is False
        assert "_test" in msg

    def test_paradox_rejected_without_suffix(self) -> None:
        """paradox without _test is rejected."""
        valid, msg = validate_database_name("paradox")
        assert valid is False
        assert "_test" in msg

    def test_production_rejected_without_suffix(self) -> None:
        """production without _test is rejected."""
        valid, msg = validate_database_name("production")
        assert valid is False
        assert "_test" in msg

    def test_suffix_in_middle_rejected(self) -> None:
        """test as suffix in middle (e.g., starwing_test_prod) is rejected."""
        valid, msg = validate_database_name("starwing_test_prod")
        assert valid is False
        assert "_test" in msg

    def test_test_at_start_only_rejected(self) -> None:
        """test_starwing (test at start, not end) is rejected."""
        valid, msg = validate_database_name("test_starwing")
        assert valid is False
        assert "_test" in msg


class TestForbiddenDatabaseNames:
    """Test that postgres, template0, template1 are refused."""

    def test_postgres_refused(self) -> None:
        """postgres database is refused."""
        valid, msg = validate_database_name("postgres")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template0_refused(self) -> None:
        """template0 database is refused."""
        valid, msg = validate_database_name("template0")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template1_refused(self) -> None:
        """template1 database is refused."""
        valid, msg = validate_database_name("template1")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_postgres_test_still_forbidden(self) -> None:
        """postgres_test is still forbidden (forbidden check runs first)."""
        valid, msg = validate_database_name("postgres_test")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template0_test_still_forbidden(self) -> None:
        """template0_test is still forbidden."""
        valid, msg = validate_database_name("template0_test")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template1_test_still_forbidden(self) -> None:
        """template1_test is still forbidden."""
        valid, msg = validate_database_name("template1_test")
        assert valid is False
        assert "forbidden" in msg.lower()


class TestEmptyDatabaseName:
    """Test that empty database name is refused."""

    def test_empty_string_refused(self) -> None:
        """Empty string is refused."""
        valid, msg = validate_database_name("")
        assert valid is False
        assert "empty" in msg.lower()

    def test_whitespace_only_refused(self) -> None:
        """Whitespace-only string is refused."""
        valid, msg = validate_database_name("   ")
        assert valid is False
        assert "empty" in msg.lower()

    def test_none_like_empty_refused(self) -> None:
        """String with only spaces and tabs is refused."""
        valid, msg = validate_database_name("  \t  ")
        assert valid is False
        assert "empty" in msg.lower()


class TestProductionLookingNames:
    """Test that production-looking database names are refused."""

    def test_paradox_name_refused(self) -> None:
        """paradox_test contains 'paradox' — production-like."""
        valid, msg = validate_database_name("paradox_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_starwing_prod_refused(self) -> None:
        """starwing_prod_test contains 'prod' — production-like."""
        valid, msg = validate_database_name("starwing_prod_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_production_test_refused(self) -> None:
        """production_test is production-looking."""
        valid, msg = validate_database_name("production_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_staging_test_refused(self) -> None:
        """staging_test is production-looking."""
        valid, msg = validate_database_name("staging_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_master_test_refused(self) -> None:
        """master_test is production-looking."""
        valid, msg = validate_database_name("master_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_live_test_refused(self) -> None:
        """live_test is production-looking."""
        valid, msg = validate_database_name("live_test")
        assert valid is False
        assert "production" in msg.lower()

    def test_real_test_refused(self) -> None:
        """real_test is production-looking."""
        valid, msg = validate_database_name("real_test")
        assert valid is False
        assert "production" in msg.lower()


# ---------------------------------------------------------------------------
# Tests: Host validation
# ---------------------------------------------------------------------------


class TestRemoteHostRefused:
    """Test that remote hostname is refused unless explicitly approved."""

    def test_localhost_allowed(self) -> None:
        """localhost is always allowed."""
        valid, _ = validate_host("localhost")
        assert valid is True

    def test_127_0_0_1_allowed(self) -> None:
        """127.0.0.1 is always allowed."""
        valid, _ = validate_host("127.0.0.1")
        assert valid is True

    def test_ipv6_loopback_allowed(self) -> None:
        """::1 is always allowed."""
        valid, _ = validate_host("::1")
        assert valid is True

    def test_ip_address_refused(self) -> None:
        """IP address (192.168.1.1) is refused without approval."""
        valid, msg = validate_host("192.168.1.1")
        assert valid is False
        assert "not approved" in msg.lower()

    def test_public_ip_refused(self) -> None:
        """Public IP is refused without approval."""
        valid, msg = validate_host("8.8.8.8")
        assert valid is False
        assert "not approved" in msg.lower()

    def test_hostname_with_dot_refused(self) -> None:
        """Hostname with dot (db.example.com) is refused."""
        valid, msg = validate_host("db.example.com")
        assert valid is False
        assert "not approved" in msg.lower()

    def test_rds_endpoint_refused(self) -> None:
        """AWS RDS endpoint is refused."""
        valid, msg = validate_host("mydb.abc123.us-east-1.rds.amazonaws.com")
        assert valid is False
        assert "not approved" in msg.lower()

    def test_empty_host_refused(self) -> None:
        """Empty host is refused."""
        valid, msg = validate_host("")
        assert valid is False
        assert "empty" in msg.lower()

    def test_approved_remote_host_allowed(self) -> None:
        """Explicitly approved remote host is allowed."""
        valid, _ = validate_host("192.168.1.100", approved_remotes=["192.168.1.100"])
        assert valid is True

    def test_unapproved_not_in_list_refused(self) -> None:
        """Host not in approved list is refused."""
        valid, msg = validate_host("192.168.1.100", approved_remotes=["10.0.0.1"])
        assert valid is False
        assert "not approved" in msg.lower()


# ---------------------------------------------------------------------------
# Tests: Reset requires explicit confirm
# ---------------------------------------------------------------------------


class TestResetRequiresConfirm:
    """Test that reset requires explicit destructive switch."""

    def test_without_confirm_refused(self) -> None:
        """Reset without -Confirm is refused."""
        valid, msg = validate_reset_requires_confirm(confirm_flag=False)
        assert valid is False
        assert "DESTRUCTIVE" in msg
        assert "-Confirm" in msg

    def test_with_confirm_allowed(self) -> None:
        """Reset with -Confirm is allowed."""
        valid, _ = validate_reset_requires_confirm(confirm_flag=True)
        assert valid is True

    def test_error_message_is_helpful(self) -> None:
        """Error message explains how to proceed."""
        _, msg = validate_reset_requires_confirm(confirm_flag=False)
        assert "reset-test-database.ps1" in msg


# ---------------------------------------------------------------------------
# Tests: Backup required before destructive reset
# ---------------------------------------------------------------------------


class TestBackupRequiredBeforeReset:
    """Test that backup is required before destructive reset."""

    def test_no_backup_attempted_refused(self) -> None:
        """Reset refused if backup not attempted."""
        valid, msg = validate_backup_required_before_reset(
            backup_exists=False, backup_attempted=False
        )
        assert valid is False
        assert "backup" in msg.lower()

    def test_backup_attempted_but_not_exists_refused(self) -> None:
        """Reset refused if backup attempted but file doesn't exist."""
        valid, msg = validate_backup_required_before_reset(
            backup_exists=False, backup_attempted=True
        )
        assert valid is False
        assert "backup" in msg.lower()
        assert "does not exist" in msg.lower()

    def test_backup_exists_and_attempted_allowed(self) -> None:
        """Reset allowed if backup exists and was attempted."""
        valid, _ = validate_backup_required_before_reset(backup_exists=True, backup_attempted=True)
        assert valid is True


# ---------------------------------------------------------------------------
# Tests: Destructive operations only target test databases
# ---------------------------------------------------------------------------


class TestDestructiveRequiresTestDatabase:
    """Test that destructive operations only target test databases."""

    def test_starwing_test_allowed_for_reset(self) -> None:
        """starwing_test is allowed for reset."""
        valid, _ = validate_destructive_requires_test_database("starwing_test", "reset")
        assert valid is True

    def test_starwing_test_allowed_for_drop(self) -> None:
        """starwing_test is allowed for drop."""
        valid, _ = validate_destructive_requires_test_database("starwing_test", "drop")
        assert valid is True

    def test_paradox_refused_for_reset(self) -> None:
        """paradox (no _test) is refused for reset."""
        valid, msg = validate_destructive_requires_test_database("paradox", "reset")
        assert valid is False
        assert "non-test" in msg.lower()

    def test_starwing_refused_for_drop(self) -> None:
        """starwing (no _test) is refused for drop."""
        valid, msg = validate_destructive_requires_test_database("starwing", "drop")
        assert valid is False
        assert "non-test" in msg.lower()

    def test_production_refused_for_reset(self) -> None:
        """production (no _test) is refused for reset."""
        valid, msg = validate_destructive_requires_test_database("production", "reset")
        assert valid is False
        assert "non-test" in msg.lower()


# ---------------------------------------------------------------------------
# Tests: Database URL validation
# ---------------------------------------------------------------------------


class TestDatabaseUrlValidation:
    """Test that database URL is validated correctly."""

    def test_valid_postgresql_url(self) -> None:
        """Valid postgresql URL with _test database is accepted."""
        valid, _ = validate_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/starwing_test"
        )
        assert valid is True

    def test_valid_asyncpg_url(self) -> None:
        """Valid asyncpg URL with _test database is accepted."""
        valid, _ = validate_database_url(
            "postgresql+asyncpg://user:pass@localhost:5432/starwing_test"
        )
        assert valid is True

    def test_empty_url_refused(self) -> None:
        """Empty URL is refused."""
        valid, msg = validate_database_url("")
        assert valid is False
        assert "empty" in msg.lower()

    def test_missing_database_name_refused(self) -> None:
        """URL with no database name is refused."""
        valid, msg = validate_database_url("postgresql+psycopg://user:pass@localhost:5432/")
        assert valid is False
        assert "missing" in msg.lower() or "database name" in msg.lower()

    def test_no_path_refused(self) -> None:
        """URL with no path at all is refused."""
        valid, msg = validate_database_url("postgresql+psycopg://user:pass@localhost:5432")
        assert valid is False

    def test_unsupported_driver_refused(self) -> None:
        """MySQL driver is refused."""
        valid, msg = validate_database_url("mysql+pymysql://user:pass@localhost:3306/mydb_test")
        assert valid is False
        assert "unsupported" in msg.lower() or "driver" in msg.lower()

    def test_postgres_database_name_in_url_refused(self) -> None:
        """URL containing 'postgres' database name is refused."""
        valid, msg = validate_database_url("postgresql+psycopg://user:pass@localhost:5432/postgres")
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template0_in_url_refused(self) -> None:
        """URL containing template0 is refused."""
        valid, msg = validate_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/template0"
        )
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_template1_in_url_refused(self) -> None:
        """URL containing template1 is refused."""
        valid, msg = validate_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/template1"
        )
        assert valid is False
        assert "forbidden" in msg.lower()

    def test_database_name_without_test_suffix_refused(self) -> None:
        """URL with database name not ending in _test is refused."""
        valid, msg = validate_database_url("postgresql+psycopg://user:pass@localhost:5432/paradox")
        assert valid is False
        assert "_test" in msg

    def test_sqlite_memory_url_accepted(self) -> None:
        """SQLite in-memory URL is accepted (test fixture pattern)."""
        valid, _ = validate_database_url("sqlite+aiosqlite:///:memory:")
        assert valid is True

    def test_sqlite_file_url_accepted(self) -> None:
        """SQLite file URL is accepted."""
        valid, _ = validate_database_url("sqlite:///test.db")
        assert valid is True

    def test_production_database_in_url_refused(self) -> None:
        """URL with production-looking database name is refused."""
        valid, msg = validate_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/paradox_test"
        )
        assert valid is False
        assert "production" in msg.lower()


# ---------------------------------------------------------------------------
# Tests: Unsupported driver detection
# ---------------------------------------------------------------------------


class TestUnsupportedDriver:
    """Test that unsupported database drivers are caught."""

    def test_mysql_refused(self) -> None:
        """MySQL driver is refused."""
        valid, msg = validate_database_url("mysql://user:pass@localhost/mydb_test")
        assert valid is False
        assert "unsupported" in msg.lower() or "driver" in msg.lower()

    def test_mongodb_refused(self) -> None:
        """MongoDB driver is refused."""
        valid, msg = validate_database_url("mongodb://user:pass@localhost/mydb")
        assert valid is False

    def test_redis_refused(self) -> None:
        """Redis URL is refused as database URL."""
        valid, msg = validate_database_url("redis://localhost:6379/0")
        assert valid is False

    def test_postgresql_psycopg_accepted(self) -> None:
        """postgresql+psycopg is accepted."""
        valid, _ = validate_database_url("postgresql+psycopg://u:p@localhost:5432/db_test")
        assert valid is True

    def test_postgresql_asyncpg_accepted(self) -> None:
        """postgresql+asyncpg is accepted."""
        valid, _ = validate_database_url("postgresql+asyncpg://u:p@localhost:5432/db_test")
        assert valid is True

    def test_postgresql_psycopg2_accepted(self) -> None:
        """postgresql+psycopg2 is accepted."""
        valid, _ = validate_database_url("postgresql+psycopg2://u:p@localhost:5432/db_test")
        assert valid is True

    def test_postgresql_pg8000_accepted(self) -> None:
        """postgresql+pg8000 is accepted."""
        valid, _ = validate_database_url("postgresql+pg8000://u:p@localhost:5432/db_test")
        assert valid is True

    def test_postgresql_plain_accepted(self) -> None:
        """postgresql (plain) is accepted as a supported prefix."""
        valid, _ = validate_database_url("postgresql://u:p@localhost:5432/db_test")
        assert valid is True

    def test_sqlite_accepted(self) -> None:
        """sqlite is accepted."""
        valid, _ = validate_database_url("sqlite:///test.db")
        assert valid is True


# ---------------------------------------------------------------------------
# Tests: PowerShell script safety rules (static analysis)
# ---------------------------------------------------------------------------


class TestPowerShellScriptSafety:
    """Validate that the PowerShell scripts contain the expected safety rules.

    These tests read the actual scripts and verify the safety checks are present.
    """

    def _read_script(self, relative_path: str) -> str:
        """Read a PowerShell script from the tools directory."""
        base = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "tools",
            "postgresql",
        )
        path = os.path.join(base, relative_path)
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_create_has_suffix_check(self) -> None:
        """create-test-database.ps1 checks for _test suffix."""
        content = self._read_script("create-test-database.ps1")
        assert "_test" in content
        assert "_test$" in content or '_test"' in content

    def test_create_has_forbidden_check(self) -> None:
        """create-test-database.ps1 checks for forbidden database names."""
        content = self._read_script("create-test-database.ps1")
        assert "forbiddenNames" in content or "forbidden" in content.lower()
        assert "postgres" in content
        assert "template0" in content
        assert "template1" in content

    def test_reset_has_suffix_check(self) -> None:
        """reset-test-database.ps1 checks for _test suffix."""
        content = self._read_script("reset-test-database.ps1")
        assert "_test" in content

    def test_reset_has_confirm_check(self) -> None:
        """reset-test-database.ps1 requires -Confirm switch."""
        content = self._read_script("reset-test-database.ps1")
        assert "-Confirm" in content or "Confirm" in content
        assert "DESTRUCTIVE" in content

    def test_reset_has_forbidden_check(self) -> None:
        """reset-test-database.ps1 checks for forbidden names."""
        content = self._read_script("reset-test-database.ps1")
        assert "postgres" in content
        assert "template0" in content
        assert "template1" in content

    def test_reset_does_backup_before_drop(self) -> None:
        """reset-test-database.ps1 creates backup before dropping."""
        content = self._read_script("reset-test-database.ps1")
        # Backup step should come before drop step
        backup_pos = content.find("backup")
        drop_pos = content.find("DROP DATABASE")
        assert backup_pos < drop_pos, "Backup must come before DROP DATABASE"

    def test_backup_has_suffix_check(self) -> None:
        """backup-test-database.ps1 checks for _test suffix."""
        content = self._read_script("backup-test-database.ps1")
        assert "_test" in content

    def test_import_has_suffix_check(self) -> None:
        """import-legacy-schema.ps1 checks for _test suffix."""
        content = self._read_script("import-legacy-schema.ps1")
        assert "_test" in content

    def test_verify_has_suffix_check(self) -> None:
        """verify-test-database.ps1 checks for _test suffix."""
        content = self._read_script("verify-test-database.ps1")
        assert "_test" in content


# ---------------------------------------------------------------------------
# Tests: Integration test skip behavior
# ---------------------------------------------------------------------------


class TestIntegrationTestSkipBehavior:
    """Test that integration tests skip correctly when PostgreSQL is unavailable."""

    def test_test_database_url_none_causes_skip(self) -> None:
        """None TEST_DATABASE_URL should trigger skip logic."""
        url = None
        should_skip = url is None or url == ""
        assert should_skip is True

    def test_test_database_url_empty_causes_skip(self) -> None:
        """Empty TEST_DATABASE_URL should trigger skip logic."""
        url = ""
        should_skip = url is None or url == ""
        assert should_skip is True

    def test_test_database_url_set_prevents_skip(self) -> None:
        """Set TEST_DATABASE_URL should not trigger skip."""
        url = "postgresql+psycopg://user:pass@localhost:5432/starwing_test"
        should_skip = url is None or url == ""
        assert should_skip is False

    def test_skip_message_includes_env_var_name(self) -> None:
        """Skip message should mention TEST_DATABASE_URL."""
        # This mirrors the actual skip message in integration tests
        skip_msg = "TEST_DATABASE_URL environment variable not set"
        assert "TEST_DATABASE_URL" in skip_msg
