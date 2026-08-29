"""Quick winmm read test."""
import ctypes
from ctypes import wintypes
import time


class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
        ('wXpos', wintypes.UINT), ('wYpos', wintypes.UINT),
        ('wZpos', wintypes.UINT), ('wRpos', wintypes.UINT),
        ('wUpos', wintypes.UINT), ('wVpos', wintypes.UINT),
        ('wButtons', wintypes.UINT), ('dwButtons', wintypes.DWORD),
        ('dwPOV', wintypes.DWORD), ('dwX1', wintypes.DWORD),
        ('dwY1', wintypes.DWORD), ('dwZ1', wintypes.DWORD),
        ('dwR1', wintypes.DWORD), ('dwU1', wintypes.DWORD),
        ('dwV1', wintypes.DWORD), ('dwX2', wintypes.DWORD),
        ('dwY2', wintypes.DWORD), ('dwZ2', wintypes.DWORD),
        ('dwR2', wintypes.DWORD), ('dwU2', wintypes.DWORD),
        ('dwV2', wintypes.DWORD), ('dwPOVNumber', wintypes.DWORD),
        ('dwReserved1', wintypes.DWORD), ('dwReserved2', wintypes.DWORD),
    ]


winmm = ctypes.windll.winmm
num = winmm.joyGetNumDevs()
print(f'Number of joystick devices: {num}')

print('Reading device 0 for 5s - move sticks and press buttons NOW...')
start = time.time()
count = 0
prev_btns = 0
prev_x = 0
prev_y = 0
while time.time() - start < 5:
    info = JOYINFOEX()
    info.dwSize = ctypes.sizeof(JOYINFOEX)
    info.dwFlags = 0xFF
    rc = winmm.joyGetPosEx(0, ctypes.byref(info))
    if rc == 0:
        x, y = info.wXpos, info.wYpos
        btns = info.dwButtons
        if btns != prev_btns or abs(x - prev_x) > 500 or abs(y - prev_y) > 500:
            count += 1
            btn_list = [f'B{b}' for b in range(32) if btns & (1 << b)]
            print(f'  [{count}] X={x:5d} Y={y:5d} Buttons={btn_list or "none"}')
            prev_btns = btns
            prev_x = x
            prev_y = y
    time.sleep(0.005)
status = "LIVE EVENTS DETECTED" if count > 0 else "NO LIVE EVENTS"
print(f'Total input changes: {count}')
print(f'Status: {status}')
