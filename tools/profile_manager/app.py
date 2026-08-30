"""Local profile manager GUI for Starwing Paradox private server.

This is an operator-owned profile manager entirely separate from NESYS,
NESiCA identity, vendor certificates, production matching, production
entitlement, and payment systems.
"""

from __future__ import annotations

import sys
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QBrush, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

SERVER_URL = "http://127.0.0.1:4001"

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


class CardTapOverlay(QWidget):
    """Full-screen overlay shown during local card-tap animation."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._opacity = 0.0
        self._visible = False

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._visible:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)
        painter.setBrush(QBrush(QColor(0, 212, 255, 60)))
        painter.setPen(QPen(QColor(0, 212, 255, 180), 3))
        painter.drawRoundedRect(self.rect().adjusted(10, 10, -10, -10), 16, 16)
        painter.end()

    def start_glow(self) -> None:
        self._visible = True
        self._opacity = 0.0
        self._anim = QPropertyAnimation(self, b"opacity_val")
        self._anim.setDuration(800)
        self._anim.setStartValue(0.0)
        self._anim.setKeyValueAt(0.5, 1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim.finished.connect(self._on_done)
        self._anim.start()
        self.show()
        self.update()

    def _on_done(self) -> None:
        self._visible = False
        self.hide()
        self.update()

    def get_opacity_val(self) -> float:  # noqa: ANN101
        return self._opacity

    def set_opacity_val(self, val: float) -> None:  # noqa: ANN101
        self._opacity = val
        self.update()

    opacity_val = property(get_opacity_val, set_opacity_val)


class ProfileCard(QFrame):
    """Card-style profile display widget."""

    profile_selected = pyqtSignal(int)
    profile_deleted = pyqtSignal(int)

    def __init__(self, profile: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.profile_id = profile["id"]
        self.profile_data = profile
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedSize(280, 180)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_card_hover']};
                border-color: {COLORS['accent']};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        name_label = QLabel(self.profile_data["display_name"])
        name_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(name_label)

        uuid_short = self.profile_data["profile_uuid"][:8] + "..."
        uuid_label = QLabel(f"ID: {uuid_short}")
        uuid_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 11px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(uuid_label)

        status_layout = QHBoxLayout()

        session_active = self.profile_data.get("session_active", False)
        session_text = "ACTIVE" if session_active else "Idle"
        session_color = COLORS["success"] if session_active else COLORS["text_secondary"]
        session_label = QLabel(session_text)
        session_label.setStyleSheet(
            f"""
            QLabel {{
                color: {session_color};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            """
        )
        status_layout.addWidget(session_label)
        status_layout.addStretch()

        tutorial_completed = self.profile_data.get("tutorial_completed", False)
        tutorial_text = "Tutorial Done" if tutorial_completed else "Tutorial Pending"
        tutorial_color = COLORS["success"] if tutorial_completed else COLORS["warning"]
        tutorial_label = QLabel(tutorial_text)
        tutorial_label.setStyleSheet(
            f"""
            QLabel {{
                color: {tutorial_color};
                font-size: 11px;
                background: transparent;
                border: none;
            }}
            """
        )
        status_layout.addWidget(tutorial_label)
        layout.addLayout(status_layout)

        created = self.profile_data.get("created_at", "")
        if created:
            created = created[:10]
        created_label = QLabel(f"Created: {created}")
        created_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 10px;
                background: transparent;
                border: none;
            }}
            """
        )
        layout.addWidget(created_label)
        layout.addStretch()

        btn_layout = QHBoxLayout()

        select_btn = QPushButton("Select")
        select_btn.setFixedHeight(32)
        select_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_light']};
            }}
            """
        )
        select_btn.clicked.connect(lambda: self.profile_selected.emit(self.profile_id))
        btn_layout.addWidget(select_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedHeight(32)
        delete_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            """
        )
        delete_btn.clicked.connect(lambda: self.profile_deleted.emit(self.profile_id))
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)


class StatusWidget(QFrame):
    """Server status display widget."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(80)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(40)

        http_layout = QVBoxLayout()
        http_title = QLabel("HTTP Server")
        http_title.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 12px; background: transparent; border: none; }}"
        )
        http_layout.addWidget(http_title)
        self.http_status = QLabel("Checking...")
        self.http_status.setStyleSheet(
            f"QLabel {{ color: {COLORS['warning']}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}"
        )
        http_layout.addWidget(self.http_status)
        layout.addLayout(http_layout)

        tcp_layout = QVBoxLayout()
        tcp_title = QLabel("TCP Matching")
        tcp_title.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 12px; background: transparent; border: none; }}"
        )
        tcp_layout.addWidget(tcp_title)
        self.tcp_status = QLabel("Checking...")
        self.tcp_status.setStyleSheet(
            f"QLabel {{ color: {COLORS['warning']}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}"
        )
        tcp_layout.addWidget(self.tcp_status)
        layout.addLayout(tcp_layout)

        db_layout = QVBoxLayout()
        db_title = QLabel("Database")
        db_title.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 12px; background: transparent; border: none; }}"
        )
        db_layout.addWidget(db_title)
        self.db_status = QLabel("Checking...")
        self.db_status.setStyleSheet(
            f"QLabel {{ color: {COLORS['warning']}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}"
        )
        db_layout.addWidget(self.db_status)
        layout.addLayout(db_layout)

        layout.addStretch()

    def update_status(self, http_ok: bool, tcp_ok: bool, db_ok: bool) -> None:
        self.http_status.setText("Online" if http_ok else "Offline")
        c = COLORS["success"] if http_ok else COLORS["error"]
        self.http_status.setStyleSheet(f"QLabel {{ color: {c}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}")

        self.tcp_status.setText("Online" if tcp_ok else "Offline")
        c = COLORS["success"] if tcp_ok else COLORS["error"]
        self.tcp_status.setStyleSheet(f"QLabel {{ color: {c}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}")

        self.db_status.setText("Connected" if db_ok else "Error")
        c = COLORS["success"] if db_ok else COLORS["error"]
        self.db_status.setStyleSheet(f"QLabel {{ color: {c}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}")


class CardTapStatusPanel(QFrame):
    """Panel shown after Tap Local Card with status labels."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(120)
        self.setVisible(False)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #0a1628;
                border: 2px solid {COLORS['card_tap_glow']};
                border-radius: 12px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(4)

        title = QLabel("LOCAL PROFILE ACTIVE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"QLabel {{ color: {COLORS['card_tap_glow']}; font-size: 18px; font-weight: bold; background: transparent; border: none; }}"
        )
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(30)

        offline_label = QLabel("OFFLINE / PRIVATE SERVER")
        offline_label.setStyleSheet(
            f"QLabel {{ color: {COLORS['success']}; font-size: 13px; font-weight: bold; background: transparent; border: none; }}"
        )
        row.addWidget(offline_label)
        row.addStretch()

        nesys_label = QLabel("NESYS AUTHENTICATED: NO")
        nesys_label.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; background: transparent; border: none; }}"
        )
        row.addWidget(nesys_label)
        layout.addLayout(row)

        self._profile_name_label = QLabel("")
        self._profile_name_label.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; background: transparent; border: none; }}"
        )
        layout.addWidget(self._profile_name_label)

        layout.addStretch()

    def show_profile(self, profile: dict) -> None:
        name = profile.get("display_name", "Unknown")
        uuid_short = profile.get("profile_uuid", "")[:8]
        self._profile_name_label.setText(f"Profile: {name} ({uuid_short}...)")
        self.setVisible(True)


class CreateProfileDialog(QFrame):
    """Inline dialog for creating a new profile."""

    profile_created = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(120)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['accent']};
                border-radius: 10px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("Create New Profile")
        title.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_primary']}; font-size: 16px; font-weight: bold; background: transparent; border: none; }}"
        )
        layout.addWidget(title)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter profile name...")
        self.name_input.setMaxLength(32)
        self.name_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border-color: {COLORS['accent']}; }}
            """
        )
        self.name_input.returnPressed.connect(self._on_create)
        input_layout.addWidget(self.name_input)

        create_btn = QPushButton("Create")
        create_btn.setFixedWidth(100)
        create_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['text_primary']};
                border: none; border-radius: 6px; padding: 8px 16px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #27ae60; }}
            """
        )
        create_btn.clicked.connect(self._on_create)
        input_layout.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(80)
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['text_muted']};
                color: {COLORS['text_primary']};
                border: none; border-radius: 6px; padding: 8px 12px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {COLORS['text_secondary']}; }}
            """
        )
        cancel_btn.clicked.connect(lambda: self.cancelled.emit())
        input_layout.addWidget(cancel_btn)

        layout.addLayout(input_layout)

    def _on_create(self) -> None:
        name = self.name_input.text().strip()
        if name:
            self.profile_created.emit(name)
            self.name_input.clear()


class ProfileManagerWindow(QMainWindow):
    """Main profile manager window with local card tap."""

    def __init__(self) -> None:
        super().__init__()
        self._profiles: list[dict] = []
        self._selected_profile_id: Optional[int] = None
        self._setup_ui()
        self._refresh_profiles()

        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start(5000)
        self._refresh_status()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Starwing Paradox - Profile Manager")
        self.setMinimumSize(960, 680)
        self.setStyleSheet(f"QMainWindow {{ background-color: {COLORS['bg_dark']}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title = QLabel("Profile Manager")
        title.setStyleSheet(
            f"QLabel {{ color: {COLORS['text_primary']}; font-size: 28px; font-weight: bold; }}"
        )
        header_layout.addWidget(title)
        header_layout.addStretch()
        subtitle = QLabel("Private Server - Local Profiles Only")
        subtitle.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 12px; }}")
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        self._status_widget = StatusWidget()
        main_layout.addWidget(self._status_widget)

        self._card_tap_status = CardTapStatusPanel()
        main_layout.addWidget(self._card_tap_status)

        action_layout = QHBoxLayout()

        new_btn = QPushButton("+ New Profile")
        new_btn.setFixedHeight(40)
        new_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text_primary']};
                border: none; border-radius: 8px; padding: 0 24px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['accent_light']}; }}
            """
        )
        new_btn.clicked.connect(self._show_create_dialog)
        action_layout.addWidget(new_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
                border: none; border-radius: 8px; padding: 0 20px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {COLORS['text_muted']}; }}
            """
        )
        refresh_btn.clicked.connect(self._refresh_profiles)
        action_layout.addWidget(refresh_btn)

        action_layout.addStretch()

        self._tap_btn = QPushButton("Tap Local Card")
        self._tap_btn.setFixedHeight(40)
        self._tap_btn.setMinimumWidth(160)
        self._tap_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['card_tap_glow']};
                color: {COLORS['bg_dark']};
                border: none; border-radius: 8px; padding: 0 20px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #33ddff; }}
            QPushButton:disabled {{ background-color: {COLORS['text_muted']}; color: {COLORS['bg_dark']}; }}
            """
        )
        self._tap_btn.clicked.connect(self._on_tap_local_card)
        action_layout.addWidget(self._tap_btn)

        end_session_btn = QPushButton("End Session")
        end_session_btn.setFixedHeight(40)
        end_session_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: {COLORS['text_primary']};
                border: none; border-radius: 8px; padding: 0 20px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #c0392b; }}
            """
        )
        end_session_btn.clicked.connect(self._on_end_session)
        action_layout.addWidget(end_session_btn)

        self._count_label = QLabel("0 profiles")
        self._count_label.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 13px; }}")
        action_layout.addWidget(self._count_label)

        main_layout.addLayout(action_layout)

        self._create_dialog = CreateProfileDialog()
        self._create_dialog.profile_created.connect(self._on_create_profile)
        self._create_dialog.cancelled.connect(self._hide_create_dialog)
        self._create_dialog.setVisible(False)
        main_layout.addWidget(self._create_dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea > QWidget > QWidget { background: transparent; }")

        self._profile_container = QWidget()
        self._profile_layout = QGridLayout(self._profile_container)
        self._profile_layout.setSpacing(16)
        self._profile_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self._profile_container)
        main_layout.addWidget(scroll)

        self._tap_overlay = CardTapOverlay(self)

    def _show_create_dialog(self) -> None:
        self._create_dialog.setVisible(True)
        self._create_dialog.name_input.setFocus()

    def _hide_create_dialog(self) -> None:
        self._create_dialog.setVisible(False)

    def _refresh_profiles(self) -> None:
        import json
        import urllib.request

        try:
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/list",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=b"{}",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    self._profiles = data.get("profiles", [])
                else:
                    self._profiles = []
        except Exception:
            self._profiles = []

        self._rebuild_profile_grid()

    def _rebuild_profile_grid(self) -> None:
        while self._profile_layout.count():
            item = self._profile_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        cols = 3
        for i, profile in enumerate(self._profiles):
            card = ProfileCard(profile)
            card.profile_selected.connect(self._on_profile_selected)
            card.profile_deleted.connect(self._on_profile_deleted)
            row = i // cols
            col = i % cols
            self._profile_layout.addWidget(card, row, col)

        self._count_label.setText(f"{len(self._profiles)} profiles")

    def _on_create_profile(self, name: str) -> None:
        import json
        import urllib.request

        try:
            body = json.dumps({"display_name": name}).encode()
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/create",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=body,
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    self._hide_create_dialog()
                    self._refresh_profiles()
                else:
                    QMessageBox.warning(self, "Error", data.get("message", "Failed to create profile"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create profile: {e}")

    def _on_profile_selected(self, profile_id: int) -> None:
        import json
        import urllib.request

        try:
            body = json.dumps({"profile_id": profile_id}).encode()
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/select",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=body,
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    self._selected_profile_id = profile_id
                    self._refresh_profiles()
                    QMessageBox.information(
                        self,
                        "Profile Selected",
                        f"Session started for {data.get('profile', {}).get('display_name', 'profile')}",
                    )
                else:
                    QMessageBox.warning(self, "Error", data.get("message", "Failed to select profile"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select profile: {e}")

    def _on_profile_deleted(self, profile_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this profile?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        import json
        import urllib.request

        try:
            body = json.dumps({"profile_id": profile_id}).encode()
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/delete",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=body,
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    if self._selected_profile_id == profile_id:
                        self._selected_profile_id = None
                        self._card_tap_status.setVisible(False)
                    self._refresh_profiles()
                else:
                    QMessageBox.warning(self, "Error", data.get("message", "Failed to delete profile"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete profile: {e}")

    def _on_tap_local_card(self) -> None:
        if self._selected_profile_id is None:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Select a local profile before tapping.",
            )
            return

        profile = None
        for p in self._profiles:
            if p["id"] == self._selected_profile_id:
                profile = p
                break

        if profile is None:
            QMessageBox.warning(self, "Error", "Selected profile not found.")
            return

        import json
        import urllib.request

        try:
            body = json.dumps({"profile_id": self._selected_profile_id}).encode()
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/select",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=body,
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("error", True):
                    QMessageBox.warning(self, "Error", data.get("message", "Session failed"))
                    return
                profile = data.get("profile", profile)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start session: {e}")
            return

        self._tap_overlay.setGeometry(self.rect())
        self._tap_overlay.start_glow()
        self._card_tap_status.show_profile(profile)
        self._refresh_profiles()

    def _on_end_session(self) -> None:
        import json
        import urllib.request

        try:
            req = urllib.request.Request(
                f"{SERVER_URL}/profile/local/end",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=b"{}",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if not data.get("error", True):
                    self._card_tap_status.setVisible(False)
                    self._selected_profile_id = None
                    self._refresh_profiles()
                else:
                    QMessageBox.warning(self, "Error", data.get("message", "No active session"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to end session: {e}")

    def _refresh_status(self) -> None:
        import json
        import socket
        import urllib.request

        http_ok = False
        tcp_ok = False
        db_ok = False

        try:
            req = urllib.request.Request(f"{SERVER_URL}/health", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                http_ok = resp.status == 200
                db_ok = data.get("status") == "healthy"
        except Exception:
            pass

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 6666))
            tcp_ok = result == 0
            sock.close()
        except Exception:
            pass

        self._status_widget.update_status(http_ok, tcp_ok, db_ok)


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
    palette.setColor(QPalette.BrightText, QColor(COLORS["accent"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS["text_primary"]))
    app.setPalette(palette)

    window = ProfileManagerWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
