"""Windows joystick API reader using winmm."""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass

try:
    _winmm = ctypes.windll.winmm
except OSError:
    _winmm = None


class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wXpos", wintypes.UINT),
        ("wYpos", wintypes.UINT),
        ("wZpos", wintypes.UINT),
        ("wRpos", wintypes.UINT),
        ("wUpos", wintypes.UINT),
        ("wVpos", wintypes.UINT),
        ("wButtons", wintypes.UINT),
        ("dwButtons", wintypes.DWORD),
        ("dwPOV", wintypes.DWORD),
        ("dwX1", wintypes.DWORD),
        ("dwY1", wintypes.DWORD),
        ("dwZ1", wintypes.DWORD),
        ("dwR1", wintypes.DWORD),
        ("dwU1", wintypes.DWORD),
        ("dwV1", wintypes.DWORD),
        ("dwX2", wintypes.DWORD),
        ("dwY2", wintypes.DWORD),
        ("dwZ2", wintypes.DWORD),
        ("dwR2", wintypes.DWORD),
        ("dwU2", wintypes.DWORD),
        ("dwV2", wintypes.DWORD),
        ("dwPOVNumber", wintypes.DWORD),
        ("dwReserved1", wintypes.DWORD),
        ("dwReserved2", wintypes.DWORD),
    ]


JOY_RETURNALL = 0xFF
JOY_RETURNX = 0x01
JOY_RETURNY = 0x02
JOY_RETURNZ = 0x04
JOY_RETURNR = 0x08
JOY_RETURNU = 0x10
JOY_RETURNV = 0x20
JOY_RETURNBUTTONS = 0x40
JOY_RETURNPOV = 0x80
CENTERED = 32767
POV_CENTERED = 0xFFFFFFFF
AXIS_MIN = 0
AXIS_MAX = 65535


@dataclass
class JoystickState:
    x: int = CENTERED
    y: int = CENTERED
    z: int = CENTERED
    r: int = CENTERED
    u: int = CENTERED
    v: int = CENTERED
    buttons: int = 0
    pov: int = POV_CENTERED
    valid: bool = False


def get_device_count() -> int:
    if _winmm is None:
        return 0
    return _winmm.joyGetNumDevs()


def read_joystick(device_id: int = 0) -> JoystickState:
    if _winmm is None:
        return JoystickState()
    info = JOYINFOEX()
    info.dwSize = ctypes.sizeof(JOYINFOEX)
    info.dwFlags = JOY_RETURNALL
    rc = _winmm.joyGetPosEx(device_id, ctypes.byref(info))
    if rc != 0:
        return JoystickState()
    return JoystickState(
        x=info.wXpos,
        y=info.wYpos,
        z=info.wZpos,
        r=info.wRpos,
        u=info.wUpos,
        v=info.wVpos,
        buttons=info.dwButtons,
        pov=info.dwPOV,
        valid=True,
    )


def normalize_axis(value: int) -> float:
    """Normalize 0-65535 to -1.0 to 1.0 with center at 0.0."""
    return (value - CENTERED) / (AXIS_MAX - CENTERED)


def is_button_pressed(buttons: int, bit: int) -> bool:
    return bool(buttons & (1 << bit))


def enumerate_devices() -> list[dict]:
    """Return list of available joystick devices."""
    count = get_device_count()
    devices = []
    for i in range(count):
        state = read_joystick(i)
        if state.valid:
            devices.append({"id": i, "name": f"Joystick {i}", "state": state})
    return devices
