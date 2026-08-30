"""Environment validation for the Starwing local launcher.

Verifies all prerequisites before launching the server stack or game.
"""
from __future__ import annotations

import json
import socket
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\KAHO\Pictures\Starwing")
GAME_ROOT = Path(r"X:\StarwingParadox")
GAME_EXE = GAME_ROOT / r"WindowsNoEditor\AcrGame.exe"
GAME_SHIPPING_EXE = GAME_ROOT / r"WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
DEFAULT_GAME_INI = GAME_ROOT / r"WindowsNoEditor\AcrGame\Config\DefaultGame.ini"
OPEN_KEY_PATH = Path(r"D:\Saved\ACRSaved\SaveData\OpenKey.json")
D_DRIVE_PATH = Path(r"D:")
SERVER_DB = PROJECT_ROOT / "server" / "data" / "starwing.db"
CONTROLLER_MAPPER_DIR = PROJECT_ROOT / "tools" / "controller_mapper"
CONTROLLER_CONFIG = PROJECT_ROOT / "tools" / "config" / "controller_mapping.json"
PYTHON_EXE = Path(r"C:\Users\KAHO\AppData\Local\Programs\Python\Python310\python.exe")

HTTP_PORT = 80
APP_PORT = 4001
TCP_PORT = 6666

# Protected file hashes (SHA-256) for integrity verification.
# Populated on first run; None means "skip check".
PROTECTED_HASHES: dict[str, str | None] = {}


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    critical: bool = True


@dataclass
class EnvironmentState:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(c.ok for c in self.checks if c.critical)

    @property
    def failures(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.ok and c.critical]


def _port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(("127.0.0.1", port)) != 0
    except OSError:
        return False


def _port_owned_by_us(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            return result == 0
    except OSError:
        return False


def check_project_root() -> CheckResult:
    ok = PROJECT_ROOT.is_dir()
    return CheckResult("Project Root", ok, str(PROJECT_ROOT), critical=True)


def check_game_root() -> CheckResult:
    ok = GAME_ROOT.is_dir()
    return CheckResult("Game Root", ok, str(GAME_ROOT), critical=True)


def check_d_drive() -> CheckResult:
    ok = D_DRIVE_PATH.is_dir()
    if not ok:
        return CheckResult("D Drive", False, "Not mounted - run subst D: \"X:\\StarwingParadox\\D DRIVE CONTENTS\"", critical=True)
    return CheckResult("D Drive", True, str(D_DRIVE_PATH), critical=True)


def check_open_key() -> CheckResult:
    if not OPEN_KEY_PATH.is_file():
        return CheckResult("OpenKey", False, f"Not found: {OPEN_KEY_PATH}", critical=True)
    try:
        data = json.loads(OPEN_KEY_PATH.read_text(encoding="utf-8"))
        is_open = data.get("IsOpen", 0)
        return CheckResult("OpenKey", True, f"IsOpen={is_open}", critical=True)
    except (OSError, ValueError) as exc:
        return CheckResult("OpenKey", False, str(exc), critical=True)


def check_default_game_ini() -> CheckResult:
    if not DEFAULT_GAME_INI.is_file():
        return CheckResult("Game Config", False, f"Not found: {DEFAULT_GAME_INI}", critical=True)
    try:
        content = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        has_matching = "127.0.0.1:6666" in content
        return CheckResult(
            "Game Config",
            has_matching,
            "DefaultMatchingServerAddress=127.0.0.1:6666" if has_matching else "Matching address not set",
            critical=True,
        )
    except (OSError, ValueError) as exc:
        return CheckResult("Game Config", False, str(exc), critical=True)


def check_port_http() -> CheckResult:
    available = _port_available(HTTP_PORT)
    detail = "Available" if available else "Pre-existing service detected"
    return CheckResult("HTTP Proxy :80", True, detail, critical=False)


def check_port_app() -> CheckResult:
    available = _port_available(APP_PORT)
    detail = "Available" if available else "Pre-existing service detected"
    return CheckResult("Python HTTP :4001", True, detail, critical=False)


def check_port_tcp() -> CheckResult:
    available = _port_available(TCP_PORT)
    detail = "Available" if available else "Pre-existing service detected"
    return CheckResult("TCP Matching :6666", True, detail, critical=False)


def check_python_env() -> CheckResult:
    ok = PYTHON_EXE.is_file()
    return CheckResult("Python Environment", ok, str(PYTHON_EXE), critical=True)


def check_controller_mapper() -> CheckResult:
    ok = CONTROLLER_MAPPER_DIR.is_dir() and CONTROLLER_CONFIG.is_file()
    return CheckResult("Controller Mapper", ok, str(CONTROLLER_MAPPER_DIR), critical=False)


def check_db_migration() -> CheckResult:
    ok = SERVER_DB.is_file()
    if not ok:
        return CheckResult("Database", False, "starwing.db not found", critical=True)
    return CheckResult("Database", True, str(SERVER_DB), critical=True)


def check_game_exe() -> CheckResult:
    ok = GAME_EXE.is_file()
    return CheckResult("Game Executable", ok, str(GAME_EXE), critical=True)


def run_all_checks() -> EnvironmentState:
    state = EnvironmentState()
    state.checks = [
        check_project_root(),
        check_game_root(),
        check_d_drive(),
        check_open_key(),
        check_default_game_ini(),
        check_port_http(),
        check_port_app(),
        check_port_tcp(),
        check_python_env(),
        check_controller_mapper(),
        check_db_migration(),
        check_game_exe(),
    ]
    return state
