"""inspect_readcard.py - scan for the ACPP_ReadCardMain object (anchor = the
DebugNesicaSelectNo int at object+0x590, normally -1) and print offsets of
interest, so we can find the live instance even at the InsertStart stage.

Offsets (from IDA EnterPressed decompile, sub_142ADCE40, a1 = ReadCardMain):
  +0x590 i32 DebugNesicaSelectNo   (line 58: v3 = *(a1+1424))
  +0x594 u8  userid/gate-flag      (line 56: !*(a1+1428) allows card read)
  +0x4C0 u8  readCardMode          (ReadCardExec=19, PremissionOfflineNesys=20)
  +0x5B0 TArray debug-card slots
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import subprocess
import sys

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


def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    n = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n))
    if not ok or n.value != size:
        return None
    return buf.raw


def pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
                         capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def scan():
    p = pid()
    print("game pid=%s" % p)
    if not p:
        return
    h = k32.OpenProcess(PROCESS_ALL, False, p)
    hits = []
    addr = 0
    while True:
        if addr <= 0 or addr > 0x7FFFFFFFFFFF:
            break
        mbi = MBI()
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in RW_PROT:
            data = read_mem(h, addr, int(mbi.RegionSize))
            if data:
                # anchor: i32 == -1 at +0x590, so 8-aligned search
                start = 0
                n = len(data)
                while start + 0x5C0 <= n:
                    i = data.find(b"\xff\xff\xff\xff", start)
                    if i < 0:
                        break
                    base = addr + i - 0x590
                    if base < addr:
                        start = i + 1
                        continue
                    sel = int.from_bytes(data[i:i+4], "little")  # +0x590
                    mode = data[i + 0x4C0 - 0x590] if n > i + 0x4C0 - 0x590 else None  # +0x4C0
                    b594 = data[i + 0x594 - 0x590] if n > i + 0x594 - 0x590 else None  # +0x594
                    hits.append((base, sel, mode, b594))
                    start = i + 1
        nxt = addr + int(mbi.RegionSize)
        if nxt <= addr:
            break
        addr = nxt
        if len(hits) > 200:
            break

    # filter: mode is a small enum (<40) if present
    print("raw -1@+0x590 hits: %d" % len(hits))
    kept = []
    for base, sel, mode, b594 in hits:
        if mode is None or mode > 40:
            continue
        kept.append((base, sel, mode, b594))
    seen = set()
    uniq = []
    for k in kept:
        if k[0] not in seen:
            seen.add(k[0])
            uniq.append(k)
    print("candidates (mode<=40): %d" % len(uniq))
    for base, sel, mode, b594 in uniq:
        v590 = read_mem(h, base + 0x590, 4)
        v594 = read_mem(h, base + 0x594, 1)
        v4c0 = read_mem(h, base + 0x4C0, 1)
        print("  base=0x%016X +0x590=%s +0x594=%s +0x4C0=%s" % (
            base,
            int.from_bytes(v590, "little") if v590 else None,
            int.from_bytes(v594, "little") if v594 else None,
            int.from_bytes(v4c0, "little") if v4c0 else None))


if __name__ == "__main__":
    scan()
