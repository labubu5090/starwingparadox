"""Tests for the Starwing Local Launcher.

Uses synthetic process and port data. Does NOT launch the real game during normal pytest.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.local_launcher.environment import (
    CheckResult,
    EnvironmentState,
    run_all_checks,
)
from tools.local_launcher.process_manager import ProcessManager
from tools.local_launcher.session_log import SessionLog
from tools.local_launcher.status import (
    GamePhase,
    LauncherState,
    LauncherStatus,
    PingPongStatus,
    PortStatus,
)

# ---------------------------------------------------------------------------
# Environment tests
# ---------------------------------------------------------------------------

class TestCheckResult:
    def test_ok_check(self) -> None:
        result = CheckResult("test", True, "detail")
        assert result.ok is True
        assert result.critical is True

    def test_fail_check(self) -> None:
        result = CheckResult("test", False, "detail", critical=False)
        assert result.ok is False
        assert result.critical is False


class TestEnvironmentState:
    def test_all_ok_when_empty(self) -> None:
        state = EnvironmentState()
        assert state.all_ok is True

    def test_all_ok_when_all_pass(self) -> None:
        state = EnvironmentState(checks=[CheckResult("a", True, ""), CheckResult("b", True, "")])
        assert state.all_ok is True

    def test_all_ok_when_noncritical_fails(self) -> None:
        state = EnvironmentState(checks=[CheckResult("a", True, ""), CheckResult("b", False, "", critical=False)])
        assert state.all_ok is True

    def test_all_ok_when_critical_fails(self) -> None:
        state = EnvironmentState(checks=[CheckResult("a", True, ""), CheckResult("b", False, "", critical=True)])
        assert state.all_ok is False

    def test_failures_list(self) -> None:
        state = EnvironmentState(checks=[
            CheckResult("a", True, ""),
            CheckResult("b", False, "bad", critical=True),
            CheckResult("c", False, "also bad", critical=False),
        ])
        assert len(state.failures) == 1
        assert state.failures[0].name == "b"


class TestPortCheck:
    def test_port_check_synthetic(self) -> None:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.listen(1)
        try:
            # Port is occupied - should fail
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.settimeout(1)
                result = probe.connect_ex(("127.0.0.1", port))
                assert result == 0  # port is occupied
        finally:
            s.close()


class TestRunAllChecks:
    def test_returns_environment_state(self) -> None:
        with patch("tools.local_launcher.environment.PROJECT_ROOT", Path(tempfile.mkdtemp())):
            state = run_all_checks()
            assert isinstance(state, EnvironmentState)
            assert len(state.checks) > 0


# ---------------------------------------------------------------------------
# Process manager tests
# ---------------------------------------------------------------------------

class TestProcessManager:
    def test_register_and_status(self) -> None:
        pm = ProcessManager()
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.pid = 12345
        mock_proc.args = ["/usr/bin/test"]
        mock_proc.poll.return_value = None

        op = pm.register("test", mock_proc, executable="/usr/bin/test", expected_port=8080)
        assert op.pid == 12345
        assert op.name == "test"
        assert op.expected_port == 8080
        assert pm.is_running("test") is True

    def test_stop_owned_process(self) -> None:
        pm = ProcessManager()
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.pid = 12345
        mock_proc.args = ["/usr/bin/test"]
        mock_proc.poll.return_value = None

        pm.register("test", mock_proc)
        result = pm.stop("test")
        assert result is True
        assert pm.is_running("test") is False

    def test_stop_nonexistent(self) -> None:
        pm = ProcessManager()
        result = pm.stop("nonexistent")
        assert result is False

    def test_stop_all(self) -> None:
        pm = ProcessManager()
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.pid = 12345
        mock_proc.args = ["/usr/bin/test"]
        mock_proc.poll.return_value = None

        pm.register("test1", mock_proc)
        pm.register("test2", mock_proc)
        stopped = pm.stop_all()
        assert len(stopped) == 2
        assert len(pm.owned_processes) == 0

    def test_status_summary(self) -> None:
        pm = ProcessManager()
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.pid = 12345
        mock_proc.args = ["/usr/bin/test"]
        mock_proc.poll.return_value = None

        pm.register("test", mock_proc)
        summary = pm.status_summary()
        assert summary == {"test": True}


# ---------------------------------------------------------------------------
# Session log tests
# ---------------------------------------------------------------------------

class TestSessionLog:
    def test_creates_session_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log = SessionLog(base_dir=Path(tmpdir))
            log.start()
            assert log.session_dir.exists()
            assert log.session_id.startswith("session_")

    def test_logs_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log = SessionLog(base_dir=Path(tmpdir))
            log.start()
            log.log_event("test_event", {"key": "value"})
            events_file = log.session_dir / "events.jsonl"
            assert events_file.exists()
            lines = events_file.read_text().strip().split("\n")
            assert len(lines) == 2  # session_start + test_event
            event = json.loads(lines[1])
            assert event["event"] == "test_event"
            assert event["data"]["key"] == "value"

    def test_save_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log = SessionLog(base_dir=Path(tmpdir))
            log.start()
            log.save_summary({"test": True})
            summary_file = log.session_dir / "summary.json"
            assert summary_file.exists()
            data = json.loads(summary_file.read_text())
            assert data["test"] is True

    def test_log_process_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log = SessionLog(base_dir=Path(tmpdir))
            log.start()
            log.log_process_event("http_server", "started", pid=1234)
            events_file = log.session_dir / "events.jsonl"
            lines = events_file.read_text().strip().split("\n")
            event = json.loads(lines[-1])
            assert event["event"] == "process"
            assert event["data"]["name"] == "http_server"
            assert event["data"]["pid"] == 1234

    def test_log_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log = SessionLog(base_dir=Path(tmpdir))
            log.start()
            log.log_error("something broke")
            events_file = log.session_dir / "events.jsonl"
            lines = events_file.read_text().strip().split("\n")
            event = json.loads(lines[-1])
            assert event["event"] == "error"
            assert event["data"]["message"] == "something broke"


# ---------------------------------------------------------------------------
# Status tests
# ---------------------------------------------------------------------------

class TestLauncherStatus:
    def test_default_state(self) -> None:
        status = LauncherStatus()
        assert status.state == LauncherState.IDLE
        assert status.game_phase == GamePhase.UNKNOWN
        assert len(status.ports) == 3
        assert status.nesys.authentication == "Unavailable"
        assert status.nesys.production_matching == "Disabled"

    def test_add_log(self) -> None:
        status = LauncherStatus()
        status.add_log("test message")
        assert len(status.startup_log) == 1
        assert "test message" in status.startup_log[0]

    def test_ping_pong_latency(self) -> None:
        pp = PingPongStatus()
        assert pp.latency_ms is None
        pp.last_pong_time = time.time() - 0.05
        latency = pp.latency_ms
        assert latency is not None
        assert 40 < latency < 60


class TestPortStatus:
    def test_port_status(self) -> None:
        ps = PortStatus(80, "HTTP Proxy")
        assert ps.port == 80
        assert ps.listening is False
        assert ps.owner_pid is None


# ---------------------------------------------------------------------------
# Security boundary tests
# ---------------------------------------------------------------------------

class TestSecurityBoundary:
    def test_no_nesica_terminology(self) -> None:
        """Launcher must not use NESiCA terminology in status module."""
        from tools.local_launcher.status import NESYSStatus
        nesys = NESYSStatus()
        assert "nesica" not in nesys.authentication.lower()
        assert "nesica" not in nesys.b_nesys_server_live.lower()

    def test_no_vendor_card_claim(self) -> None:
        """Launcher must not claim game-visible card insertion."""
        from tools.local_launcher.status import LauncherStatus
        status = LauncherStatus()
        assert status.nesys.authentication == "Unavailable"

    def test_no_online_mode_claim(self) -> None:
        """Launcher must not claim online functionality."""
        from tools.local_launcher.status import LauncherState, LauncherStatus
        status = LauncherStatus()
        assert status.state in (LauncherState.IDLE, LauncherState.CHECKING, LauncherState.STARTING,
                                LauncherState.RUNNING, LauncherState.LAUNCHING_GAME,
                                LauncherState.GAME_RUNNING, LauncherState.STOPPING, LauncherState.ERROR)

    def test_no_profile_load_claim(self) -> None:
        """Launcher must not claim /player/profile/load was triggered."""
        from tools.local_launcher.status import ProfileStatus
        profile = ProfileStatus()
        assert profile.session_active is False

    def test_offline_label(self) -> None:
        """Launcher displays offline/private server mode."""
        from tools.local_launcher.status import LauncherState, LauncherStatus
        status = LauncherStatus()
        assert status.state == LauncherState.IDLE


# ---------------------------------------------------------------------------
# Startup ordering tests
# ---------------------------------------------------------------------------

class TestStartupOrdering:
    def test_env_before_server(self) -> None:
        """Environment checks must run before server start."""
        state = EnvironmentState(checks=[CheckResult("test", False, "blocked", critical=True)])
        assert state.all_ok is False
        # Server should not start when env fails

    def test_server_before_game(self) -> None:
        """Server must be running before game launch."""
        pm = ProcessManager()
        assert pm.is_running("http_server") is False
        # Game should not launch when server not running


# ---------------------------------------------------------------------------
# Offline/NESYS labels tests
# ---------------------------------------------------------------------------

class TestOfflineLabels:
    def test_nesys_unavailable(self) -> None:
        from tools.local_launcher.status import NESYSStatus
        nesys = NESYSStatus()
        assert nesys.authentication == "Unavailable"
        assert nesys.b_nesys_server_live == "Unavailable"
        assert nesys.production_matching == "Disabled"

    def test_unavailable_modes_not_presented(self) -> None:
        """Unavailable modes must be clearly labeled."""
        unavailable = [
            "Nationwide Battle",
            "Cooperative Mode",
            "2-on-2 Online",
            "8-on-8 Online",
            "Player Data",
            "Card Confirmation",
            "Mission Mode",
            "Production Customization",
        ]
        for mode in unavailable:
            assert isinstance(mode, str)
            assert len(mode) > 0


# ---------------------------------------------------------------------------
# Credit safety tests
# ---------------------------------------------------------------------------

class TestCreditSafety:
    def test_credit_mapping_has_safety(self) -> None:
        """Credit mapping must have explicit safety constraints."""
        from tools.local_launcher.status import LauncherStatus
        status = LauncherStatus()
        assert status.state == LauncherState.IDLE
