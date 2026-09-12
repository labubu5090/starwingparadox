"""patch_online_gate.py - find the UOnlineObserverWork online-gate struct in the
running game's memory and force the failing gate flags to 1 so the game goes
online and the card can be used.

No exe patching. Only runtime writes to the live process.

LiveBits order (byte offsets in the observer struct, from G38/G45):
  +0x63 WebServer    (currently 0 -> failing)
  +0x64 Nesys        (1)
  +0x65 Testmode     (1)
  +0x66 Reception    (1)
  +0x67 Game         (1)
  +0x68 GameConnect  (currently 0 -> failing)
  +0x69 HttpSuccess  (currently 0 -> failing)

We search for the 7-byte signature [0,1,1,1,1,0,0] at +0x63..+0x69 and set
the three failing bytes to 1. Because the game may re-drive HttpSuccess back
to 0 on HTTP events, we re-apply periodically.
"""
from __future__ import annotations

import ctypes
import os
import re
import subprocess
import sys
import time

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

class SZ(ctypes.Structure):
    _fields_ = [("maximum", ctypes.c_size_t), ("length", ctypes.c_size_t)]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80

k32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
k32.OpenProcess.restype = ctypes.c_void_p
k32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.CloseHandle.argtypes = [ctypes.c_void_p]
k32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]


def open_game(pid):
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        raise OSError("OpenProcess failed %d" % ctypes.get_last_error())
    return h


def regions(h):
    addr = 0
    while True:
        if addr <= 0 or addr > 0x7FFFFFFFFFFF:
            break
        mbi = MEMORY_BASIC_INFORMATION()
        n = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if not n:
            break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in (
            PAGE_READWRITE, PAGE_WRITECOPY, PAGE_EXECUTE_READWRITE, PAGE_EXECUTE_WRITECOPY
        ):
            yield addr, mbi.RegionSize
        nxt = addr + int(mbi.RegionSize)
        if nxt <= addr:
            break
        addr = nxt


def read_mem(h, addr, length):
    buf = ctypes.create_string_buffer(length)
    got = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, length, ctypes.byref(got))
    if not ok:
        return None
    return buf.raw[:got.value]


def write_byte(h, addr, val):
    b = ctypes.c_byte(val)
    got = ctypes.c_size_t(0)
    return k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(b), 1, ctypes.byref(got))


SYM = bytes([0, 1, 1, 1, 1, 1, 0])  # +0x63..+0x69 live values (WebServer=0 failing, GameConnect now 1, HttpSuccess=0 failing)
OFF_OFFSET = 0x63


def find_gates(h):
    results = []
    for base, size in regions(h):
        data = read_mem(h, base, size)
        if not data or len(data) < OFF_OFFSET + 7:
            continue
        start = 0
        while True:
            i = data.find(SYM, start)
            if i < 0:
                break
            addr = base + i - OFF_OFFSET  # start of struct
            results.append(addr)
            start = i + 1
    return results


LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"


def pid_of():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
        capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def main():
    pid = pid_of()
    if pid is None:
        print("[PATCH] no game running")
        return
    print("[PATCH] game pid=%d" % pid)

    last_log_pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    patched = set()
    h = open_game(pid)
    try:
        deadline = time.time() + 240
        while time.time() < deadline:
            if pid_of() != pid:
                print("[PATCH] game exited")
                break
            gates = find_gates(h)
            if gates:
                for g in gates:
                    if g not in patched:
                        if write_byte(h, g + 0x63, 1):
                            write_byte(h, g + 0x68, 1)
                            write_byte(h, g + 0x69, 1)
                            patched.add(g)
                            print("[PATCH] gate @0x%016X set WebServer/GameConnect/HttpSuccess=1" % g)
                        else:
                            print("[PATCH] write failed @0x%016X err=%d" % (g, ctypes.get_last_error()))
                if gates:
                    print("[PATCH] live gates=%d patched=%d" % (len(gates), len(patched)))
            else:
                print("[PATCH] no gate signature found yet...")

            try:
                with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_log_pos)
                    new = f.read().splitlines()
                    last_log_pos = f.tell()
            except (OSError, ValueError):
                new = []
            for ln in new:
                if "LiveBits" in ln:
                    print("[LOG] " + ln.strip())
                if "ReadCardMain::EnterPressed" in ln and "NESiCA_ID" in ln and "NESiCA_ID[]" not in ln.replace("&#",""):
                    print("[PATCH] CARD ID POPULATED -> " + ln.strip())
            time.sleep(1.0)
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    main()
