"""Safe keyboard output via Win32 SendInput. Only sends approved keys."""
import ctypes
import ctypes.wintypes as wt
import time

user32 = ctypes.windll.user32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

VK_MAP = {
    "W": 0x57,
    "A": 0x41,
    "D": 0x44,
    "Space": 0x20,
    "Shift": 0xA0,
    "Q": 0x51,
    "E": 0x45,
    "LCtrl": 0xA2,
    "F": 0x46,
    "Enter": 0x0D,
    "Z": 0x5A,
}

MOUSE_VK = {
    "LMB": None,
    "RMB": None,
    "MMB": None,
}


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wt.WORD),
        ("wScan", wt.WORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wt.LONG),
        ("dy", wt.LONG),
        ("mouseData", wt.DWORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("union", INPUT_UNION)]


def _send_key(vk: int, up: bool) -> None:
    scan = user32.MapVirtualKeyW(vk, 0)
    flags = KEYEVENTF_SCANCODE
    if up:
        flags |= KEYEVENTF_KEYUP
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def _send_mouse_button(down: bool, flag: int) -> None:
    flags = 0
    if not down:
        flags = 0x0002
    inp = INPUT()
    inp.type = 0
    inp.union.mi.dwFlags = flag | flags
    inp.union.mi.mouseData = 0
    inp.union.mi.time = 0
    inp.union.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


MOUSE_DOWN_FLAG = {
    "LMB": 0x0002,
    "RMB": 0x0008,
    "MMB": 0x0020,
}


class KeyboardOutput:
    def __init__(self):
        self._held_keys: set[str] = set()
        self._last_release_all = 0.0

    def press(self, key: str) -> bool:
        if key in MOUSE_VK:
            return self._press_mouse(key, True)
        vk = VK_MAP.get(key)
        if vk is None:
            return False
        if key not in self._held_keys:
            _send_key(vk, up=False)
            self._held_keys.add(key)
        return True

    def release(self, key: str) -> bool:
        if key in MOUSE_VK:
            return self._press_mouse(key, False)
        vk = VK_MAP.get(key)
        if vk is None:
            return False
        if key in self._held_keys:
            _send_key(vk, up=True)
            self._held_keys.discard(key)
        return True

    def tap(self, key: str, duration: float = 0.05) -> bool:
        if self.press(key):
            time.sleep(duration)
            self.release(key)
            return True
        return False

    def release_all(self) -> None:
        now = time.time()
        if now - self._last_release_all < 0.05:
            return
        self._last_release_all = now
        for key in list(self._held_keys):
            self.release(key)

    def _press_mouse(self, key: str, down: bool) -> bool:
        flag = MOUSE_DOWN_FLAG.get(key)
        if flag is None:
            return False
        _send_mouse_button(down, flag)
        return True

    @property
    def held(self) -> list[str]:
        return list(self._held_keys)
