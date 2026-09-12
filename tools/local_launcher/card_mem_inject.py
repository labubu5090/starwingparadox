"""card_mem_inject.py - runtime memory injector for the Starwing card screen.

No exe patching. Locates the ACPP_ReadCardMain instance in the running game's
memory and sets `DebugNesicaSelectNo` (object offset +0x590, init -1) to a
valid slot index (>= 0) so the game reads its OWN resident debug-card table
(at offset +0x5B0, 48-byte slots) and populates NESiCA_ID.

Signature (from IDA, Shipping exe):
  [+0x4C0] u8 readCardMode           (small enum)
  [+0x4C1] u8 prev readCardMode       (small enum)
  [+0x590] i32 DebugNesicaSelectNo    (-1 normally)
  [+0x5B0] TArray<slot,48B> : [0]=slot-array ptr, [+0x5B8]=count, [+0x5BC]=capacity

Usage:
  python card_mem_inject.py scan [--pid PID] [--show N]
  python card_mem_inject.py set --slot N [--index ADDR] [--pid PID]
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import sys

# ---- Win32 ----
PROCESS_ALL = 0x1F0FFF
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_TERMINATE = 0x0001
# minimal rights needed to read/write the game's object memory
PROCESS_RW = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION

MEM_COMMIT = 0x1000
MEM_MAPPED = 0x40000
MEM_PRIVATE = 0x20000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80

READABLE = PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
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
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wt.BOOL
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.CloseHandle.argtypes = [wt.HANDLE]


def _enable_debug_privilege() -> bool:
    """Best-effort SeDebugPrivilege enable (needed when the game runs elevated)."""
    try:
        from ctypes import wintypes
        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

        class LUID(ctypes.Structure):
            _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", ctypes.c_long)]

        class LUID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]

        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", wintypes.DWORD),
                        ("Privileges", LUID_AND_ATTRIBUTES * 1)]

        SE_PRIVILEGE_ENABLED = 0x00000002
        TOKEN_ADJUST_PRIVILEGES = 0x0020
        TOKEN_QUERY = 0x0008
        SE_DEBUG_NAME = "SeDebugPrivilege"

        advapi32.OpenProcessToken.argtypes = [wt.HANDLE, wintypes.DWORD, ctypes.POINTER(wt.HANDLE)]
        advapi32.LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]
        advapi32.AdjustTokenPrivileges.argtypes = [
            wt.HANDLE, wintypes.BOOL, ctypes.POINTER(TOKEN_PRIVILEGES), wintypes.DWORD,
            ctypes.POINTER(TOKEN_PRIVILEGES), ctypes.POINTER(wintypes.DWORD)]

        h = wt.HANDLE()
        if not advapi32.OpenProcessToken(k32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(h)):
            return False
        try:
            luid = LUID()
            if not advapi32.LookupPrivilegeValueW(None, SE_DEBUG_NAME, ctypes.byref(luid)):
                return False
            tp = TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Privileges[0].Luid = luid
            tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
            return bool(advapi32.AdjustTokenPrivileges(h, False, ctypes.byref(tp), 0, None, None))
        finally:
            k32.CloseHandle(h)
    except Exception:
        return False


def find_game_pid() -> int | None:
    import subprocess
    # prefer the actual shipped executable name
    for name in ("AcrGame-Win64-Shipping", "AcrGame-Win64", "AcrGame"):
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"(Get-Process | Where-Object {{$_.Name -eq '{name}'}} | Select-Object -First 1 -ExpandProperty Id)"],
            capture_output=True, text=True, timeout=30)
        s = out.stdout.strip()
        if s.isdigit():
            return int(s)
    return None


def open_game(pid: int | None = None) -> int:
    if pid is None:
        pid = find_game_pid()
        if pid is None:
            sys.exit("No AcrGame process found. Launch the game first.")
    _enable_debug_privilege()
    # first try minimal rights (most reliable), then full access
    for rights, label in ((PROCESS_RW, "RW"), (PROCESS_ALL, "ALL")):
        h = k32.OpenProcess(rights, False, pid)
        if h:
            return h
    err = ctypes.get_last_error()
    sys.exit(f"OpenProcess failed for PID {pid} (last error 0x{err:X} / {err}). "
             f"Run this tool elevated if the game runs as administrator.")


def read_mem(h, addr, size) -> bytes | None:
    buf = ctypes.create_string_buffer(size)
    n = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n))
    if not ok or n.value != size:
        return None
    return buf.raw


def read_u32(h, addr) -> int | None:
    b = read_mem(h, addr, 4)
    return int.from_bytes(b, "little") if b else None


def read_u64(h, addr) -> int | None:
    b = read_mem(h, addr, 8)
    return int.from_bytes(b, "little") if b else None


def is_readable_ptr(h, addr) -> bool:
    if addr == 0:
        return False
    mbi = MEMORY_BASIC_INFORMATION()
    n = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
    if not n:
        return False
    if mbi.State != MEM_COMMIT:
        return False
    prot = mbi.Protect & 0xFF
    if prot in (PAGE_GUARD, PAGE_NOACCESS):
        return False
    return True


def candidate_ok(h, addr) -> dict | None:
    mode = read_mem(h, addr + 0x4C0, 1)
    if mode is None or mode[0] > 40:
        return None
    prev = read_mem(h, addr + 0x4C1, 1)
    if prev is None or prev[0] > 40:
        return None
    sel = read_u32(h, addr + 0x590)
    if sel is None:
        return None
    if sel != -1 and not (0 <= sel <= 65536):
        return None
    tptr = read_u64(h, addr + 0x5B0)
    if tptr is None or not is_readable_ptr(h, tptr):
        return None
    count_b = read_mem(h, addr + 0x5B0 + 8, 8)
    if count_b is None:
        return None
    count = int.from_bytes(count_b[:4], "little")
    cap = int.from_bytes(count_b[4:], "little")
    if not (0 < count <= 1_000_000) or cap < count:
        return None
    # sanity: first slot readable
    if not is_readable_ptr(h, tptr):
        return None
    return {
        "addr": addr,
        "mode": mode[0],
        "prevMode": prev[0],
        "sel": sel,
        "tablePtr": tptr,
        "count": count,
        "cap": cap,
    }


def regions(h):
    base = ctypes.c_void_p(0)
    while True:
        addr = base.value
        if addr is None or addr <= 0 or addr > 0x7FFFFFFFFFFF:
            break
        mbi = MEMORY_BASIC_INFORMATION()
        n = k32.VirtualQueryEx(h, base, ctypes.byref(mbi), ctypes.sizeof(mbi))
        if not n:
            break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in (PAGE_READWRITE, PAGE_WRITECOPY,
                                                                PAGE_EXECUTE_READWRITE, PAGE_EXECUTE_WRITECOPY):
            yield addr, mbi.RegionSize
        nxt = addr + int(mbi.RegionSize)
        if nxt <= addr:
            break
        base = ctypes.c_void_p(nxt)


def scan(pid, show=20):
    h = open_game(pid)
    found = []
    try:
        for base, size in regions(h):
            # read the page, scan for candidate offsets
            chunk = 0x100000
            off = 0
            while off < size:
                cur = base + off
                length = min(chunk, size - off)
                data = read_mem(h, cur, length)
                if data:
                    # candidate addresses are aligned to 8 for TArray at +0x5B0 (0x5B0 % 8 == 0), so base 8-byte aligned
                    for i in range(0, length - 0x5C0, 8):
                        a = cur + i
                        c = candidate_ok(h, a)
                        if c:
                            found.append(c)
                            if len(found) >= show:
                                pass
                off += length
                if len(found) >= show * 4:
                    break
            if len(found) >= show * 4:
                break
        # dedupe
        seen = {}
        for c in found:
            seen.setdefault(c["addr"], c)
        cands = list(seen.values())
        cands.sort(key=lambda c: c["count"] if 0 < c["count"] else 10**9)
        print(f"Found {len(cands)} candidate ACPP_ReadCardMain object(s):")
        for c in cands[:show]:
            print(f"  addr=0x{c['addr']:016X} mode={c['mode']} prev={c['prevMode']} "
                  f"DebugNesicaSelectNo={c['sel']} table=0x{c['tablePtr']:016X} count={c['count']} cap={c['cap']}")
    finally:
        k32.CloseHandle(h)


def set_slot(pid, slot, addr=None):
    h = open_game(pid)
    try:
        if addr is not None:
            candidates = [{"addr": addr, "sel": read_u32(h, addr + 0x590), "count": None}]
        else:
            allc = []
            for base, size in regions(h):
                chunk = 0x100000
                off = 0
                while off < size:
                    cur = base + off
                    length = min(chunk, size - off)
                    data = read_mem(h, cur, length)
                    if data:
                        for i in range(0, length - 0x5C0, 8):
                            c = candidate_ok(h, cur + i)
                            if c:
                                allc.append(c)
                    off += length
            # choose the best: smallest count, sel == -1 preferred
            best = None
            for c in allc:
                key = (c["sel"] != -1, c["count"] if 0 < c["count"] else 10**9)
                if best is None or key < best[0]:
                    best = (key, c)
            candidates = [best[1]] if best else []
        if not candidates:
            sys.exit("No candidate found. Ensure game is on the card screen.")
        c = candidates[0]
        cur_sel = read_u32(h, c["addr"] + 0x590)
        print(f"Target 0x{c['addr']:016X}: DebugNesicaSelectNo was {cur_sel} -> writing {slot}")
        write_u32(h, c["addr"] + 0x590, slot)
        after = read_u32(h, c["addr"] + 0x590)
        print(f"Verify: DebugNesicaSelectNo now = {after}")
    finally:
        k32.CloseHandle(h)


def write_u32(h, addr, val):
    buf = ctypes.c_uint32(val)
    n = ctypes.c_size_t(0)
    ok = k32.WriteProcessMemory(h, ctypes.c_void_p(addr), ctypes.byref(buf), 4, ctypes.byref(n))
    if not ok or n.value != 4:
        raise OSError(f"WriteProcessMemory failed at 0x{addr:X}: {ctypes.get_last_error()}")


def main():
    ap = argparse.ArgumentParser(description="Starwing card-screen runtime injector (no exe patch)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_scan = sub.add_parser("scan", help="Enumerate candidate ACPP_ReadCardMain objects")
    p_scan.add_argument("--pid", type=int, default=None)
    p_scan.add_argument("--show", type=int, default=20)
    p_set = sub.add_parser("set", help="Write DebugNesicaSelectNo to a slot index")
    p_set.add_argument("--slot", type=int, required=True)
    p_set.add_argument("--index", type=lambda x: int(x, 16), default=None, help="Exact object address (hex) if known")
    p_set.add_argument("--pid", type=int, default=None)
    args = ap.parse_args()

    if args.cmd == "scan":
        scan(args.pid, args.show)
    elif args.cmd == "set":
        set_slot(args.pid, args.slot, args.index)


if __name__ == "__main__":
    main()
