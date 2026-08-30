"""Server status dashboard for Starwing Paradox private server.

Displays real-time server health, database stats, and active sessions.
"""

from __future__ import annotations

import json
import socket
import sys
import urllib.request
from typing import Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

SERVER_URL = "http://127.0.0.1:4001"

COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "accent": "#e94560",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0b0",
    "text_muted": "#606070",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "border": "#2a2a4a",
}


class StatCard(QFrame):
    """Single statistic card."""

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(title_label)

        self.value_label = QLabel("--")
        self.value_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(self.value_label)

        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 11px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(self.detail_label)

    def update_value(self, value: str, detail: str = "", color: str = "") -> None:
        self.value_label.setText(value)
        if detail:
            self.detail_label.setText(detail)
        if color:
            self.value_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    font-size: 28px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
                """
            )


class ServiceStatusRow(QFrame):
    """Single service status row."""

    def __init__(self, name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.service_name = name
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(44)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {COLORS['border']};
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        name_label = QLabel(self.service_name)
        name_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(name_label)

        layout.addStretch()

        self.status_label = QLabel("Unknown")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(self.status_label)

        self.detail_label = QLabel("")
        self.detail_label.setFixedWidth(200)
        self.detail_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(self.detail_label)

    def update_status(self, status: str, detail: str = "", color: str = "") -> None:
        self.status_label.setText(status)
        if detail:
            self.detail_label.setText(detail)
        if color:
            self.status_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
                """
            )


class DashboardWindow(QMainWindow):
    """Server status dashboard window."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

        # Auto-refresh every 3 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(3000)
        self._refresh()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Starwing Paradox - Server Dashboard")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
            """
        )

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Server Dashboard")
        title.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 28px;
                font-weight: bold;
            }}
            """
        )
        header.addWidget(title)
        header.addStretch()

        self._refresh_btn = QPushButton("Refresh Now")
        self._refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ff6b81;
            }}
            """
        )
        self._refresh_btn.clicked.connect(self._refresh)
        header.addWidget(self._refresh_btn)
        main_layout.addLayout(header)

        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        self._http_card = StatCard("HTTP Server (4001)")
        stats_layout.addWidget(self._http_card, 0, 0)

        self._tcp_card = StatCard("TCP Matching (6666)")
        stats_layout.addWidget(self._tcp_card, 0, 1)

        self._db_card = StatCard("Database")
        stats_layout.addWidget(self._db_card, 0, 2)

        self._profiles_card = StatCard("Profiles")
        stats_layout.addWidget(self._profiles_card, 1, 0)

        self._session_card = StatCard("Active Sessions")
        stats_layout.addWidget(self._session_card, 1, 1)

        self._uptime_card = StatCard("Last Check")
        stats_layout.addWidget(self._uptime_card, 1, 2)

        main_layout.addLayout(stats_layout)

        # Services section
        services_frame = QFrame()
        services_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            """
        )
        services_layout = QVBoxLayout(services_frame)
        services_layout.setContentsMargins(16, 12, 16, 12)
        services_layout.setSpacing(0)

        services_title = QLabel("Service Status")
        services_title.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            """
        )
        services_layout.addWidget(services_title)

        self._http_service = ServiceStatusRow("HTTP API (port 4001)")
        self._tcp_service = ServiceStatusRow("TCP Matching (port 6666)")
        self._db_service = ServiceStatusRow("SQLite Database")
        self._proxy_service = ServiceStatusRow("Reverse Proxy (port 80)")

        services_layout.addWidget(self._http_service)
        services_layout.addWidget(self._tcp_service)
        services_layout.addWidget(self._db_service)
        services_layout.addWidget(self._proxy_service)

        main_layout.addWidget(services_frame)
        main_layout.addStretch()

    def _refresh(self) -> None:
        """Refresh all status indicators."""
        import time

        now = time.strftime("%H:%M:%S")

        http_ok = False
        tcp_ok = False
        db_ok = False
        http_detail = ""
        tcp_detail = ""
        db_detail = ""
        profile_count = 0
        active_sessions = 0

        # Check HTTP
        try:
            req = urllib.request.Request(f"{SERVER_URL}/health", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                http_ok = resp.status == 200
                db_ok = data.get("status") == "healthy"
                http_detail = f"Status {resp.status}"
                db_detail = data.get("database", "unknown")
        except Exception as e:
            http_detail = str(e)[:30]

        # Check TCP
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            start = time.time()
            result = sock.connect_ex(("127.0.0.1", 6666))
            elapsed = (time.time() - start) * 1000
            tcp_ok = result == 0
            tcp_detail = f"{elapsed:.0f}ms" if tcp_ok else "Connection refused"
            sock.close()
        except Exception as e:
            tcp_detail = str(e)[:30]

        # Check profiles
        try:
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/list",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=b"{}",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    profiles = data.get("profiles", [])
                    profile_count = len(profiles)
                    active_sessions = sum(
                        1 for p in profiles if p.get("session_active", False)
                    )
        except Exception:
            pass

        # Update cards
        self._http_card.update_value(
            "Online" if http_ok else "Offline",
            http_detail,
            COLORS["success"] if http_ok else COLORS["error"],
        )
        self._tcp_card.update_value(
            "Online" if tcp_ok else "Offline",
            tcp_detail,
            COLORS["success"] if tcp_ok else COLORS["error"],
        )
        self._db_card.update_value(
            "Connected" if db_ok else "Error",
            db_detail,
            COLORS["success"] if db_ok else COLORS["error"],
        )
        self._profiles_card.update_value(
            str(profile_count), "total profiles", COLORS["text_primary"]
        )
        self._session_card.update_value(
            str(active_sessions),
            "active",
            COLORS["success"] if active_sessions > 0 else COLORS["text_muted"],
        )
        self._uptime_card.update_value(now, "auto-refresh 3s", COLORS["text_secondary"])

        # Update service rows
        self._http_service.update_status(
            "Healthy" if http_ok else "Down",
            http_detail,
            COLORS["success"] if http_ok else COLORS["error"],
        )
        self._tcp_service.update_status(
            "Listening" if tcp_ok else "Down",
            tcp_detail,
            COLORS["success"] if tcp_ok else COLORS["error"],
        )
        self._db_service.update_status(
            "Connected" if db_ok else "Error",
            db_detail,
            COLORS["success"] if db_ok else COLORS["error"],
        )
        self._proxy_service.update_status(
            "Active" if http_ok else "Unknown",
            "Port 80",
            COLORS["text_muted"],
        )


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.WindowText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Base, QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Text, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Button, QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ButtonText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS["text_primary"]))
    app.setPalette(palette)

    window = DashboardWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
