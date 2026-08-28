"""Unit tests for application configuration."""

from app.config import Settings


class TestSettings:
    """Test Settings loading from environment variables."""

    def test_default_settings(self):
        """Settings can be instantiated with defaults."""
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.app_env == "development"
        assert settings.app_host == "0.0.0.0"
        assert settings.app_port == 4001
        assert settings.pb_port == 6666
        assert settings.log_level == "INFO"
        assert settings.version_main == 70571
        assert settings.version_data == 70571

    def test_custom_port(self):
        """Settings respects custom port."""
        settings = Settings(
            app_port=8080,
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.app_port == 8080

    def test_production_env(self):
        """Settings can be set to production."""
        settings = Settings(
            app_env="production",
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.app_env == "production"

    def test_legacy_compatibility_mode_default(self):
        """Legacy compatibility mode defaults to True."""
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.legacy_compatibility_mode is True

    def test_private_server_compatibility_mode_default(self):
        """Private-server compatibility mode defaults to False (disabled by default)."""
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.private_server_compatibility_mode is False

    def test_private_server_compatibility_mode_explicit_enable(self):
        """Private-server compatibility mode can be enabled explicitly."""
        settings = Settings(
            private_server_compatibility_mode=True,
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.private_server_compatibility_mode is True

    def test_database_url_stored(self):
        """Database URL is stored correctly."""
        url = "postgresql+psycopg://user:pass@host:5432/db"
        settings = Settings(
            database_url=url,
            redis_url="redis://localhost:6379/0",
        )
        assert settings.database_url == url

    def test_redis_url_stored(self):
        """Redis URL is stored correctly."""
        url = "redis://redis-host:6380/2"
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url=url,
        )
        assert settings.redis_url == url

    def test_protocol_logging_defaults(self):
        """Protocol logging defaults are set."""
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
        )
        assert settings.protocol_raw_logging is False
        assert settings.protocol_hash_logging is True

    def test_matcher_hostname(self):
        """Matcher hostname is stored."""
        settings = Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
            matcher_hostname="myserver.example.com",
        )
        assert settings.matcher_hostname == "myserver.example.com"
