"""patch_readcard.py - continuously watch the running game; whenever the
ACPP_ReadCardMain object exists (it appears transiently during card attempts),
patch it so EnterPressed can read the debug card:

  +0x594 u8  = 0  (permission gate: !byte(a1+1428) allows card read)
  +0x590 i32 = 0  (DebugNesicaSelectNo -> read card slot 0)

Offsets confirmed from IDA EnterPressed decompile (sub_142ADCE40):
  1428=0x594, 1424=0x590, 1464=0x5B8, 1456=0x5B0, 1216=0x4C0.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

PROCESS_ALL = 0x1F0FFF
MEM_COMMIT = 0x1000
RW_PROT = (0x04, 0x08, 0x40, 0x80)


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]


k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wt.BOOL
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]


def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    n = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n))
    if not ok or n.value != size:
        return None
    return buf.raw


def write_byte(h, addr, val):
    b = ctypes.c_byte(val)
    n = ctypes.c_size_t(0)
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(b), 1, ctypes.byref(n))


def write_i32(h, addr, val):
    b = ctypes.c_int32(val)
    n = ctypes.c_size_t(0)
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(b), 4, ctypes.byref(n))


def pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
                         capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def find_object(h):
    addr = 0
    while True:
        if addr <= 0 or addr > 0x7FFFFFFFFFFF:
            break
        mbi = MBI()
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in RW_PROT:
            size = int(mbi.RegionSize)
            data = read_mem(h, addr, size)
            if data:
                n = len(data)
                # window to inspect +0x4C0..+0x5B8 for each 8-aligned candidate
                for i in range(0, n - 0x5BC, 8):
                    if data[i + 0x4C0] > 40:      # readCardMode small enum
                        continue
                    if data[i + 0x594] > 1:       # gate byte is a bool
                        continue
                    # readCardMode in {19,20} is ReadCardExec/PremissionOfflineNesys
                    mode = data[i + 0x4C0]
                    if mode not in (19, 20):
                        continue
                    return addr + i
        nxt = addr + int(mbi.RegionSize)
        if nxt <= addr:
            break
        addr = nxt
    return None


def main():
    print("[PATCH] watching for ACPP_ReadCardMain...")
    patched = set()
    last = 0
    while True:
        p = pid()
        if not p:
            print("[PATCH] game exited")
            break
        h = k32.OpenProcess(PROCESS_ALL, False, p)
        if not h:
            time.sleep(0.5)
            continue
        try:
            base = find_object(h)
            if base:
                cur594 = read_mem(h, base + 0x594, 1)
                cur590 = read_mem(h, base + 0x590, 4)
                if base not in patched:
                    if cur594 is not None and cur594[0] != 0:
                        write_byte(h, base + 0x594, 0)
                    if cur590 is not None and int.from_bytes(cur590, "little") < 0:
                        write_i32(h, base + 0x590, 0)
                    patched.add(base)
                now = time.time()
                if now - last > 2:
                    print("[PATCH] obj 0x%016X +0x594=%s(->%s) +0x590=%d(->0)" % (
                        base,
                        cur594[0] if cur594 else "?",
                        "0" if cur594 and cur594[0] != 0 else "ok",
                        int.from_bytes(cur590, "little") if cur590 else -99))
                    last = now
        finally:
            k32.CloseHandle(h)
        time.sleep(0.15)


if __name__ == "__main__":
    main()
