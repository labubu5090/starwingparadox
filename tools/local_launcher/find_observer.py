"""find_observer.py - locate the UOnlineObserverWork object by scanning for the
7-byte flag tuple (LiveBits values) anywhere in memory, then validating it is a
plausible UObject (vtable pointer present).

LiveBits: WebServer:0 Nesys:1 Reception:1 Game:1 Testmode:1 GameConnect:1 HttpSuccess:0
Stored contiguously (order per Report format): bytes [0,1,1,1,1,1,0]
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import subprocess
import sys

PROCESS_ALL = 0x1F0FFF
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80


class MBI(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wt.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
    ]


k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.CloseHandle.argtypes = [wt.HANDLE]


def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    n = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n))
    if not ok or n.value != size:
        return None
    return buf.raw


def is_readable(h, addr):
    if not addr:
        return False
    mbi = MBI()
    n = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
    if not n or mbi.State != MEM_COMMIT:
        return False
    return True


def pid_of():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
        capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


PAT = bytes([0, 1, 1, 1, 1, 1, 0])
# also try with testmode/reception swapped per G45 gate order
PAT2 = bytes([0, 1, 1, 1, 1, 1, 0])


def scan():
    pid = pid_of()
    if pid is None:
        print("no game")
        return
    h = k32.OpenProcess(PROCESS_ALL, False, pid)
    if not h:
        print("OpenProcess fail", ctypes.get_last_error())
        return
    addr = 0
    hits = []
    try:
        while True:
            if addr <= 0 or addr > 0x7FFFFFFFFFFF:
                break
            mbi = MBI()
            n = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
            if not n:
                break
            if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in (
                PAGE_READWRITE, PAGE_WRITECOPY, PAGE_EXECUTE_READWRITE, PAGE_EXECUTE_WRITECOPY
            ):
                data = read_mem(h, addr, int(mbi.RegionSize))
                if data:
                    s = 0
                    while True:
                        i = data.find(PAT, s)
                        if i < 0:
                            break
                        st = addr + i
                        # validate uobject: readable qword pointer at st (vtable) OR at st-8
                        ok_vt = False
                        for vtp in (st, st - 8):
                            vt = int.from_bytes(read_mem(h, vtp, 8) or b"\x00" * 8, "little")
                            if vt and (vt >> 40) in (0x7, 0x0) and is_readable(h, vtp):
                                ok_vt = True
                                break
                        hits.append((st, vt if ok_vt else 0))
                        s = i + 1
                        if len(hits) > 60:
                            break
            nxt = addr + int(mbi.RegionSize)
            if nxt <= addr:
                break
            addr = nxt
            if len(hits) > 60:
                break
    finally:
        k32.CloseHandle(h)
    print("Found %d hits for 7-byte tuple [0,1,1,1,1,1,0]:" % len(hits))
    for st, vt in hits:
        print("  @0x%016X vtable=0x%016X" % (st, vt))
    # dump bytes around each hit for manual inspection
    h = k32.OpenProcess(PROCESS_ALL, False, pid)
    try:
        for st, vt in hits[:20]:
            base = st - 0x70 if st >= 0x70 else 0
            b = read_mem(h, base, 0x100)
            if b:
                printable = " ".join("%02X" % c for c in b)
                print("  --- dump from 0x%016X ---" % base)
                print("  " + printable)
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    scan()
