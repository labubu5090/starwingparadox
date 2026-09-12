"""patch_readcard_foreground.py - find ACPP_ReadCardMain and patch it so
EnterPressed can read the debug card. Prints with flush so we see live results.

  object + 0x594 u8  = permission gate; set 0 -> !byte(a1+1428) true -> card read
  object + 0x590 i32 = DebugNesicaSelectNo; set valid slot (0)
  object + 0x4C0 u8  = readCardMode (19=ReadCardExec, 20=PremissionOfflineNesys)

Scans all 8-phase alignments, verifies mode is a small enum, and patches as soon
as a matching object is found. Re-scans continuously.
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
CHUNK = 0x400000


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


def log(*a):
    print(*a, flush=True)


def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    n = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n))
    if not ok or n.value != size:
        return None
    return buf.raw


def wr_u8(h, addr, v):
    b = ctypes.c_byte(v)
    n = ctypes.c_size_t(0)
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(b), 1, ctypes.byref(n))


def wr_i32(h, addr, v):
    b = ctypes.c_int32(v)
    n = ctypes.c_size_t(0)
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(b), 4, ctypes.byref(n))


def pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
                         capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def find_object(h):
    """Scan committed RW regions for an object where +0x4C0 is a small enum and
    +0x594 is 0/1 (the ReadCardMain gate byte). Returns base address or None."""
    addr = 0
    while True:
        if addr <= 0 or addr > 0x7FFFFFFFFFFF:
            break
        mbi = MBI()
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in RW_PROT:
            rsize = int(mbi.RegionSize)
            off = 0
            while off < rsize:
                cur = addr + off
                length = min(CHUNK, rsize - off)
                data = read_mem(h, cur, length)
                if data:
                    n = len(data)
                    for i in range(0, n - 0x600):  # every byte; detect base by 8-aligned only
                        if i & 7:  # object base 8-aligned
                            continue
                        mode = data[i + 0x4C0]
                        if mode > 40:
                            continue
                        gb = data[i + 0x594]
                        if gb > 1:
                            continue
                        # both plausible: candidate
                        return cur + i
                off += length
        nxt = addr + int(mbi.RegionSize)
        if nxt <= addr:
            break
        addr = nxt
    return None


def main():
    log("[PATCH] foreground watcher started")
    patched = set()
    while True:
        p = pid()
        if not p:
            log("[PATCH] game not running (waiting)")
            time.sleep(3)
            continue
        h = k32.OpenProcess(PROCESS_ALL, False, p)
        if not h:
            time.sleep(0.5)
            continue
        try:
            base = find_object(h)
            if base:
                if base not in patched:
                    c_t = read_mem(h, base + 0x4C0, 1)
                    c_gb = read_mem(h, base + 0x594, 1)
                    c_sel = read_mem(h, base + 0x590, 4)
                    log("[PATCH] object @0x%016X mode=%s gate=%s sel=%d" % (
                        base,
                        c_t[0] if c_t else "?",
                        c_gb[0] if c_gb else "?",
                        int.from_bytes(c_sel, "little") if c_sel else -99))
                    if c_gb and c_gb[0] != 0:
                        wr_u8(h, base + 0x594, 0)
                        log("[PATCH]   wrote +0x594 -> 0")
                    if c_sel and int.from_bytes(c_sel, "little") < 0:
                        wr_i32(h, base + 0x590, 0)
                        log("[PATCH]   wrote +0x590 -> 0")
                    patched.add(base)
                # verify
                v_gb = read_mem(h, base + 0x594, 1)
                v_sel = read_mem(h, base + 0x590, 4)
                log("[PATCH] verify gate=%s sel=%d" % (
                    v_gb[0] if v_gb else "?",
                    int.from_bytes(v_sel, "little") if v_sel else -99))
        finally:
            k32.CloseHandle(h)
        time.sleep(0.12)


if __name__ == "__main__":
    main()
