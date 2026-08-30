"""Foreground window detection for Starwing process guard."""
import ctypes
import ctypes.wintypes as wt

try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

user32 = ctypes.windll.user32

STARWING_PROCESS = "AcrGame-Win64-Shipping.exe"


def get_foreground_pid() -> int | None:
    hwnd = user32.GetForegroundWindow()
    if hwnd == 0:
        return None
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def is_starwing_foreground() -> bool:
    if not _PSUTIL_AVAILABLE:
        return False
    pid = get_foreground_pid()
    if pid is None:
        return False
    try:
        proc = psutil.Process(pid)
        return proc.name() == STARWING_PROCESS
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def get_starwing_pid() -> int | None:
    if not _PSUTIL_AVAILABLE:
        return None
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == STARWING_PROCESS:
            return proc.info["pid"]
    return None
