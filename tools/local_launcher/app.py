"""Starwing Local Launcher - Unified GUI for offline play experience.

Follows project conventions: PyQt5, dark theme, Fusion style, urllib for HTTP.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .environment import (
    APP_PORT,
    GAME_EXE,
    HTTP_PORT,
    PROJECT_ROOT,
    TCP_PORT,
    EnvironmentState,
    run_all_checks,
)
from .process_manager import ProcessManager
from .session_log import SessionLog
from .status import (
    GamePhase,
    LauncherState,
    LauncherStatus,
)

SERVER_URL = "http://127.0.0.1:4001"
SERVER_SCRIPT = PROJECT_ROOT / "server" / "main.py"
PROXY_SCRIPT = PROJECT_ROOT / "tools" / "g30_proxy.py"
CONTROLLER_MAPPER_SCRIPT = PROJECT_ROOT / "tools" / "controller_mapper" / "app.py"

COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_card_active": "#0f3460",
    "bg_card_hover": "#1a2744",
    "accent": "#e94560",
    "accent_light": "#ff6b81",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0b0",
    "text_muted": "#606070",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "border": "#2a2a4a",
    "border_active": "#e94560",
    "card_tap_glow": "#00d4ff",
}


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------

class StatusCard(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusCard")
        self.setFrameShape(QFrame.StyledPanel)
        self._title = title
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            f"QFrame#StatusCard {{ background: {COLORS['bg_card']}; "
            f"border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 12px; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        layout.addWidget(self._title_label)

        self._value_label = QLabel("--")
        self._value_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: bold;")
        layout.addWidget(self._value_label)

        self._detail_label = QLabel("")
        self._detail_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        layout.addWidget(self._detail_label)

    def set_value(self, value: str, color: str = COLORS["text_primary"]) -> None:
        self._value_label.setText(value)
        self._value_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")

    def set_detail(self, detail: str) -> None:
        self._detail_label.setText(detail)


class ActionButton(QPushButton):
    def __init__(self, text: str, accent: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        if accent:
            self.setStyleSheet(
                f"QPushButton {{ background: {COLORS['accent']}; color: white; "
                f"border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 12px; }}"
                f"QPushButton:hover {{ background: {COLORS['accent_light']}; }}"
                f"QPushButton:disabled {{ background: {COLORS['text_muted']}; color: {COLORS['bg_dark']}; }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ background: {COLORS['bg_card']}; color: {COLORS['text_primary']}; "
                f"border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 8px 16px; font-size: 12px; }}"
                f"QPushButton:hover {{ background: {COLORS['bg_card_hover']}; border-color: {COLORS['accent']}; }}"
                f"QPushButton:disabled {{ background: {COLORS['bg_dark']}; color: {COLORS['text_muted']}; }}"
            )


class SectionHeader(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 13px; font-weight: bold; "
            f"padding: 8px 0px 4px 0px; border-bottom: 1px solid {COLORS['border']};"
        )


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class LauncherWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._status = LauncherStatus()
        self._processes = ProcessManager()
        self._session_log = SessionLog()
        self._env_state: EnvironmentState | None = None
        self._session_log.start()
        self._setup_ui()
        self._setup_timers()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Starwing Paradox - Local Launcher")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(f"QMainWindow {{ background: {COLORS['bg_dark']}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Left panel: status cards + buttons
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        # Status cards grid
        left_layout.addWidget(SectionHeader("Environment Status"))
        self._cards: dict[str, StatusCard] = {}
        card_grid = QGridLayout()
        card_grid.setSpacing(8)
        card_keys = [
            ("d_drive", "D Drive"),
            ("open_key", "OpenKey"),
            ("game_config", "Game Config"),
            ("http_proxy", "HTTP Proxy :80"),
            ("python_http", "Python HTTP :4001"),
            ("tcp_match", "TCP Matching :6666"),
            ("game_conn", "Game Connection"),
            ("ping_pong", "Ping/Pong"),
            ("controller", "Controller"),
            ("profile", "Selected Local Profile"),
            ("local_session", "Local Session"),
            ("nesys_auth", "NESYS Authentication"),
            ("prod_match", "Production Matching"),
        ]
        for i, (key, title) in enumerate(card_keys):
            card = StatusCard(title)
            self._cards[key] = card
            card_grid.addWidget(card, i // 3, i % 3)
        left_layout.addLayout(card_grid)

        # Mode display
        left_layout.addWidget(SectionHeader("Mode"))
        self._mode_label = QLabel("Offline / Private Server")
        self._mode_label.setStyleSheet(
            f"color: {COLORS['success']}; font-size: 16px; font-weight: bold; padding: 8px;"
        )
        left_layout.addWidget(self._mode_label)

        # NESYS/Production status
        self._nesys_label = QLabel("NESYS Authentication: Unavailable")
        self._nesys_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; padding: 4px;")
        left_layout.addWidget(self._nesys_label)
        self._prod_label = QLabel("Production Matching: Disabled")
        self._prod_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; padding: 4px;")
        left_layout.addWidget(self._prod_label)

        # Unavailable modes
        left_layout.addWidget(SectionHeader("Unavailable in Current Scope"))
        unavailable_text = (
            "Nationwide Battle, Cooperative Mode, 2-on-2 Online, 8-on-8 Online,\n"
            "Player Data, Card Confirmation, Mission Mode, Production Customization"
        )
        unavail_label = QLabel(unavailable_text)
        unavail_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; padding: 4px;")
        unavail_label.setWordWrap(True)
        left_layout.addWidget(unavail_label)

        left_layout.addStretch()
        left_scroll.setWidget(left_widget)
        main_layout.addWidget(left_scroll, stretch=3)

        # Right panel: buttons + log
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        # Action buttons
        right_layout.addWidget(SectionHeader("Actions"))
        btn_grid = QGridLayout()
        btn_grid.setSpacing(6)

        self._btn_check = ActionButton("Check Environment", accent=True)
        self._btn_check.clicked.connect(self._on_check_environment)
        btn_grid.addWidget(self._btn_check, 0, 0)

        self._btn_start = ActionButton("Start Server Stack", accent=True)
        self._btn_start.clicked.connect(self._on_start_server)
        btn_grid.addWidget(self._btn_start, 0, 1)

        self._btn_stop = ActionButton("Stop Server Stack")
        self._btn_stop.clicked.connect(self._on_stop_server)
        btn_grid.addWidget(self._btn_stop, 1, 0)

        self._btn_launch = ActionButton("Launch Game", accent=True)
        self._btn_launch.clicked.connect(self._on_launch_game)
        btn_grid.addWidget(self._btn_launch, 1, 1)

        self._btn_stop_game = ActionButton("Stop Game")
        self._btn_stop_game.clicked.connect(self._on_stop_game)
        btn_grid.addWidget(self._btn_stop_game, 2, 0)

        self._btn_stop_all = ActionButton("Emergency Stop", accent=True)
        self._btn_stop_all.setStyleSheet(
            f"QPushButton {{ background: {COLORS['error']}; color: white; "
            f"border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 12px; }}"
            f"QPushButton:hover {{ background: #c0392b; }}"
        )
        self._btn_stop_all.clicked.connect(self._on_emergency_stop)
        btn_grid.addWidget(self._btn_stop_all, 2, 1)

        right_layout.addLayout(btn_grid)

        # Profile buttons
        right_layout.addWidget(SectionHeader("Profile & Controller"))
        prof_btn_layout = QHBoxLayout()
        self._btn_profiles = ActionButton("Open Profile Manager")
        self._btn_profiles.clicked.connect(self._open_profile_manager)
        prof_btn_layout.addWidget(self._btn_profiles)
        self._btn_controller = ActionButton("Open Controller Mapper")
        self._btn_controller.clicked.connect(self._open_controller_mapper)
        prof_btn_layout.addWidget(self._btn_controller)
        right_layout.addLayout(prof_btn_layout)

        # Debug controls
        right_layout.addWidget(SectionHeader("Debug Controls"))
        debug_label = QLabel("Z: Debug Credit | S: Service Credit | X: Subtract Credit")
        debug_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; padding: 4px;")
        right_layout.addWidget(debug_label)

        # Log area
        right_layout.addWidget(SectionHeader("Startup Log"))
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setStyleSheet(
            f"QTextEdit {{ background: {COLORS['bg_card']}; color: {COLORS['text_secondary']}; "
            f"border: 1px solid {COLORS['border']}; border-radius: 6px; "
            f"font-family: Consolas, monospace; font-size: 11px; padding: 8px; }}"
        )
        right_layout.addWidget(self._log_text, stretch=1)

        main_layout.addWidget(right_widget, stretch=2)

        # Initialize default card states
        self._cards["nesys_auth"].set_value("Unavailable", COLORS["text_muted"])
        self._cards["prod_match"].set_value("Disabled", COLORS["text_muted"])
        self._cards["profile"].set_value("None Selected", COLORS["text_muted"])

    def _setup_timers(self) -> None:
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_status)
        self._refresh_timer.start(3000)

    def _add_log(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self._log_text.append(line)
        self._status.add_log(msg)
        self._session_log.log_event("gui", {"message": msg})

    # -----------------------------------------------------------------------
    # Environment checks
    # -----------------------------------------------------------------------

    def _on_check_environment(self) -> None:
        self._add_log("Running environment checks...")
        self._status.state = LauncherState.CHECKING
        self._env_state = run_all_checks()

        check_map = {
            "Project Root": "d_drive",
            "Game Root": "game_config",
            "D Drive": "d_drive",
            "OpenKey": "open_key",
            "Game Config": "game_config",
            "HTTP Proxy :80": "http_proxy",
            "Python HTTP :4001": "python_http",
            "TCP Matching :6666": "tcp_match",
            "Game Executable": "game_config",
        }

        for check in self._env_state.checks:
            card_key = check_map.get(check.name)
            if card_key and card_key in self._cards:
                card = self._cards[card_key]
                if check.ok:
                    card.set_value("OK", COLORS["success"])
                    card.set_detail(check.detail)
                else:
                    card.set_value("FAIL", COLORS["error"])
                    card.set_detail(check.detail)
            self._add_log(f"  {check.name}: {'OK' if check.ok else 'FAIL'} - {check.detail}")

        if self._env_state.all_ok:
            self._add_log("All environment checks passed.")
            self._status.state = LauncherState.IDLE
        else:
            failures = [c.name for c in self._env_state.failures]
            self._add_log(f"BLOCKED: {', '.join(failures)}")
            self._status.state = LauncherState.ERROR
            self._status.error_message = f"Environment checks failed: {', '.join(failures)}"

    # -----------------------------------------------------------------------
    # Server stack
    # -----------------------------------------------------------------------

    def _on_start_server(self) -> None:
        if self._env_state is None or not self._env_state.all_ok:
            self._add_log("Cannot start: environment checks not passed. Run Check Environment first.")
            return
        self._add_log("Starting server stack...")
        self._status.state = LauncherState.STARTING

        from .environment import _port_available

        # Start HTTP server only if port 4001 is free
        if _port_available(APP_PORT):
            try:
                proc = subprocess.Popen(
                    [str(PROJECT_ROOT / "server" / ".venv" / "Scripts" / "python.exe"), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "4001"],
                    cwd=str(PROJECT_ROOT / "server"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self._processes.register("http_server", proc, expected_port=APP_PORT)
                self._add_log(f"HTTP server started (PID {proc.pid})")
                self._session_log.log_server_event("http_server", "started", f"PID {proc.pid}")
            except (OSError, FileNotFoundError) as exc:
                self._add_log(f"Failed to start HTTP server: {exc}")
                self._session_log.log_error(f"HTTP server start failed: {exc}")
        else:
            self._add_log("HTTP server :4001 already running (pre-existing) — skipped")

        # Start proxy only if port 80 is free
        if _port_available(HTTP_PORT):
            try:
                proxy_log = self._session_log.session_dir / "proxy.log"
                proc = subprocess.Popen(
                    [str(PROJECT_ROOT / "server" / ".venv" / "Scripts" / "python.exe"), str(PROXY_SCRIPT)],
                    cwd=str(PROJECT_ROOT),
                    stdout=open(proxy_log, "w"),  # noqa: SIM115
                    stderr=subprocess.STDOUT,
                )
                self._processes.register("http_proxy", proc, expected_port=HTTP_PORT, log_path=str(proxy_log))
                self._add_log(f"HTTP proxy started (PID {proc.pid})")
                self._session_log.log_server_event("http_proxy", "started", f"PID {proc.pid}")
            except (OSError, FileNotFoundError) as exc:
                self._add_log(f"Failed to start HTTP proxy: {exc}")
        else:
            self._add_log("HTTP proxy :80 already running (pre-existing) — skipped")

        # TCP matching server — start only if port 6666 is free
        if _port_available(TCP_PORT):
            self._add_log("TCP matching server managed by HTTP server process")
        else:
            self._add_log("TCP matching :6666 already running (pre-existing) — skipped")

        self._status.state = LauncherState.RUNNING
        self._add_log("Server stack ready.")
        self._update_card("http_proxy", "Running", COLORS["success"])
        self._update_card("python_http", "Running", COLORS["success"])
        self._update_card("tcp_match", "Running", COLORS["success"])

    def _on_stop_server(self) -> None:
        self._add_log("Stopping server stack...")
        self._status.state = LauncherState.STOPPING
        stopped = self._processes.stop_all()
        for name in stopped:
            self._add_log(f"  Stopped: {name}")
            self._session_log.log_process_event(name, "stopped")
        self._status.state = LauncherState.IDLE

        from .environment import _port_available
        if _port_available(APP_PORT):
            self._update_card("python_http", "Running", COLORS["success"])
        else:
            self._update_card("python_http", "Stopped", COLORS["text_muted"])
        if _port_available(HTTP_PORT):
            self._update_card("http_proxy", "Running", COLORS["success"])
        else:
            self._update_card("http_proxy", "Stopped", COLORS["text_muted"])
        if _port_available(TCP_PORT):
            self._update_card("tcp_match", "Running", COLORS["success"])
        else:
            self._update_card("tcp_match", "Stopped", COLORS["text_muted"])
        self._add_log("Server stack stopped.")

    # -----------------------------------------------------------------------
    # Game launch
    # -----------------------------------------------------------------------

    def _on_launch_game(self) -> None:
        from .environment import _port_available
        if not self._processes.is_running("http_server") and _port_available(APP_PORT):
            self._add_log("Cannot launch game: HTTP server not running. Start Server Stack first.")
            return
        exe = str(GAME_EXE)
        if not os.path.isfile(exe):
            self._add_log(f"Game executable not found: {exe}")
            return
        self._add_log("Launching game...")
        self._status.state = LauncherState.LAUNCHING_GAME
        try:
            proc = subprocess.Popen([exe], cwd=str(GAME_EXE.parent))
            self._processes.register("game", proc, executable=exe)
            self._status.game_pid = proc.pid
            self._add_log(f"Game launched (PID {proc.pid})")
            self._session_log.log_game_event("launched", f"PID {proc.pid}")
            self._status.game_phase = GamePhase.LAUNCHING
            self._update_card("game_conn", "Launching", COLORS["warning"])
        except (OSError, FileNotFoundError) as exc:
            self._add_log(f"Failed to launch game: {exc}")
            self._session_log.log_error(f"Game launch failed: {exc}")

    def _on_stop_game(self) -> None:
        if self._processes.stop("game"):
            self._add_log("Game stopped.")
            self._status.game_phase = GamePhase.CLOSED
            self._status.game_pid = None
            self._update_card("game_conn", "Closed", COLORS["text_muted"])
            self._session_log.log_game_event("stopped")
        else:
            self._add_log("No game process to stop.")

    def _on_emergency_stop(self) -> None:
        reply = QMessageBox.question(
            self, "Emergency Stop",
            "Stop all launcher-owned processes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._add_log("EMERGENCY STOP initiated")
            self._session_log.log_event("emergency_stop")
            stopped = self._processes.stop_all()
            for name in stopped:
                self._add_log(f"  Stopped: {name}")
            self._status.state = LauncherState.IDLE
            self._status.game_phase = GamePhase.CLOSED
            self._add_log("Emergency stop complete.")

    # -----------------------------------------------------------------------
    # External tools
    # -----------------------------------------------------------------------

    def _open_profile_manager(self) -> None:
        pm_script = PROJECT_ROOT / "tools" / "profile_manager" / "app.py"
        if pm_script.is_file():
            subprocess.Popen([sys.executable, str(pm_script)])
            self._add_log("Profile Manager opened.")
        else:
            self._add_log("Profile Manager not found.")

    def _open_controller_mapper(self) -> None:
        if CONTROLLER_MAPPER_SCRIPT.is_file():
            subprocess.Popen([sys.executable, str(CONTROLLER_MAPPER_SCRIPT)])
            self._add_log("Controller Mapper opened.")
        else:
            self._add_log("Controller Mapper not found.")

    # -----------------------------------------------------------------------
    # Status refresh
    # -----------------------------------------------------------------------

    def _refresh_status(self) -> None:
        if self._status.state in (LauncherState.IDLE, LauncherState.RUNNING, LauncherState.GAME_RUNNING):
            self._refresh_ports()
            self._refresh_ping_pong()
            self._refresh_game_phase()

    def _refresh_ports(self) -> None:
        for ps in self._status.ports:
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex(("127.0.0.1", ps.port))
                s.close()
                ps.listening = result == 0
            except OSError:
                ps.listening = False

        for ps in self._status.ports:
            card_key = {80: "http_proxy", 4001: "python_http", 6666: "tcp_match"}.get(ps.port)
            if card_key and card_key in self._cards:
                if ps.listening:
                    self._update_card(card_key, "Listening", COLORS["success"])
                else:
                    self._update_card(card_key, "Not Listening", COLORS["error"])

    def _refresh_ping_pong(self) -> None:
        try:
            req = urllib.request.Request(f"{SERVER_URL}/matching/server", method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, data=b'{}', timeout=3) as resp:
                data = json.loads(resp.read())
                if "ip_addr" in data:
                    self._status.ping_pong.connected = True
                    self._update_card("ping_pong", "Connected", COLORS["success"])
                else:
                    self._status.ping_pong.connected = False
                    self._update_card("ping_pong", "No Response", COLORS["warning"])
        except (OSError, TimeoutError, ValueError):
            self._status.ping_pong.connected = False
            self._update_card("ping_pong", "Unreachable", COLORS["error"])

    def _refresh_game_phase(self) -> None:
        if self._processes.is_running("game"):
            self._status.game_phase = GamePhase.BATTLE
            self._update_card("game_conn", "Running", COLORS["success"])
        elif self._status.game_phase == GamePhase.BATTLE:
            self._status.game_phase = GamePhase.CLOSED
            self._update_card("game_conn", "Closed", COLORS["text_muted"])

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _update_card(self, key: str, value: str, color: str) -> None:
        if key in self._cards:
            self._cards[key].set_value(value, color)

    def closeEvent(self, event) -> None:
        owned = self._processes.owned_processes
        if owned:
            reply = QMessageBox.question(
                self, "Quit Launcher",
                f"Stop {len(owned)} launcher-owned process(es)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self._processes.stop_all()
        self._session_log.stop()
        event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.WindowText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Base, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Text, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Button, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ButtonText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.BrightText, QColor(COLORS["accent"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS["text_primary"]))
    app.setPalette(palette)

    window = LauncherWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
