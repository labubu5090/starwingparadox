import ctypes
import ctypes.wintypes as wt
import struct
import sys
import time

PROCESS_NAME = "AcrGame-Win64-Shipping.exe"

OBJ_INFO_OFF   = 0x180   # +384 : pointer to info struct (non-NULL in online run)
OBJ_HTTPIP_OFF = 0x648   # +1608: FString mirrored from info+128 by sub_142C64490
INFO_HTTPIP    = 0x80    # info +128: FString httpip source
FS_SIZE        = 16

GLOB_CFG_ADDR  = 0x8EE17B8   # qword_148EE17B8 : config matching address FString
GLOB_CFG_FLAG  = 0x8EE1804   # byte_148EE1804  : config-armed flag

HTTPIP_TEXT   = "127.0.0.1"
CFGADDR_TEXT  = "127.0.0.1:6666"
PROBE_TEXT    = "PROBE"
RETRY_S       = 10.0          # game matching retry period, seconds
PROBE_WAIT_S  = 14.0          # wait after probe write before identifying

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
MEM_PRIVATE = 0x20000
PROTECT_OK = (0x04, 0x08, 0x20, 0x40, 0x80)

ULONG_PTR = ctypes.c_size_t


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


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("th32ModuleID", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("GlblcntUsage", wt.DWORD),
        ("ProccntUsage", wt.DWORD),
        ("modBaseAddr", ctypes.c_void_p),
        ("modBaseSize", wt.DWORD),
        ("hModule", ctypes.c_void_p),
        ("szModule", ctypes.c_wchar * 256),
        ("szExePath", ctypes.c_wchar * 260),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.VirtualAllocEx.restype = ctypes.c_void_p
kernel32.VirtualAllocEx.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
    wt.DWORD, wt.DWORD,
]
kernel32.WriteProcessMemory.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
]


def find_pids():
    """Return ALL PIDs of the game (there can be several instances running)."""
    out = []
    snap = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if not snap or snap == ctypes.c_void_p(-1).value:
        return out
    try:
        class PE(ctypes.Structure):
            _fields_ = [
                ("dwSize", wt.DWORD),
                ("cntUsage", wt.DWORD),
                ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ULONG_PTR),
                ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_wchar * 260),
            ]
        proc = PE()
        proc.dwSize = ctypes.sizeof(PE)
        ok = kernel32.Process32FirstW(ctypes.c_void_p(snap), ctypes.byref(proc))
        while ok:
            if proc.szExeFile.lower() == PROCESS_NAME.lower():
                out.append(proc.th32ProcessID)
            ok = kernel32.Process32NextW(ctypes.c_void_p(snap), ctypes.byref(proc))
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(snap))
    return out


def find_pid():
    pids = find_pids()
    return pids[0] if pids else None


def module_base(pid):
    snap = kernel32.CreateToolhelp32Snapshot(0x00000008, pid)
    if not snap or snap == ctypes.c_void_p(-1).value:
        return None, None
    try:
        me = MODULEENTRY32W()
        me.dwSize = ctypes.sizeof(MODULEENTRY32W)
        ok = kernel32.Module32FirstW(ctypes.c_void_p(snap), ctypes.byref(me))
        while ok:
            if me.szModule.lower() == PROCESS_NAME.lower():
                return me.modBaseAddr, me.modBaseSize
            ok = kernel32.Module32NextW(ctypes.c_void_p(snap), ctypes.byref(me))
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(snap))
    return None, None


def open_game(pid):
    return kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)


def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(max(size, 1))
    n = ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, max(size, 1), ctypes.byref(n)):
        return buf.raw[:n.value]
    return None


def write_mem(h, addr, data):
    n = ctypes.c_size_t(0)
    return kernel32.WriteProcessMemory(h, ctypes.c_void_p(addr), data, len(data), ctypes.byref(n))


def read_fstring(h, addr):
    d = read_mem(h, addr, FS_SIZE)
    if d is None or len(d) < FS_SIZE:
        return None
    pdata, num, cap = struct.unpack_from("<QII", d)
    if num <= 0 or num > 65535 or pdata == 0:
        return ""
    buf = read_mem(h, pdata, num * 2)
    if buf is None:
        return None
    return buf.decode("utf-16-le", errors="replace")


def write_fstring(h, addr, text):
    data = text.encode("utf-16-le") + b"\x00\x00"
    alloc = kernel32.VirtualAllocEx(h, None, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
    if not alloc:
        return 0
    buf = ctypes.create_string_buffer(data)
    n = ctypes.c_size_t(0)
    if not kernel32.WriteProcessMemory(h, ctypes.c_void_p(alloc), buf, len(data), ctypes.byref(n)):
        return 0
    payload = struct.pack("<QII", alloc, len(text), len(text) + 1)
    if not write_mem(h, addr, payload):
        return 0
    return alloc


def enumerate_regions(h):
    regions = []
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while True:
        res = kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if res == 0:
            break
        base = mbi.BaseAddress or addr
        size = mbi.RegionSize
        if base > 0x7FFFFFFFFFFFFFFF:
            break
        if mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE and (mbi.Protect & 0xFF) in PROTECT_OK and (mbi.Protect & 0x100) == 0:
            regions.append((base, size))
        addr = base + size
        if addr == 0 or addr > 0x700000000000:
            break
    return regions


def find_candidates(h, modbase, modsize):
    """Scan committed private RW regions for candidate UObjects.

    Signature: vtable in module at +0, and an EMPTY FString (Num==0) at +1608.
    The empty-FString Num/Max slot (8 zero bytes at obj+1616) is located first
    with a C-level bytes.find for speed; then vtable/info are validated.

    class_a: info (+384) == 0          -> write httpip FString at +1608 directly
    class_b: info (+384) != 0 (Theory B) -> probe-identify then write info+128
    """
    modbase_i = modbase
    modend_i = modbase + modsize
    class_a = []
    class_b = []
    needle = b"\x00" * 8
    for base, size in enumerate_regions(h):
        if size > 512 * 1024 * 1024 or size < OBJ_HTTPIP_OFF + FS_SIZE:
            continue
        raw = read_mem(h, base, size)
        if raw is None:
            continue
        pos = raw.find(needle)
        while pos != -1:
            cand = pos - 1616
            if cand >= 0 and cand % 8 == 0:
                vtable = struct.unpack_from("<Q", raw, cand)[0]
                if modbase_i <= vtable < modend_i:
                    info = struct.unpack_from("<Q", raw, cand + OBJ_INFO_OFF)[0]
                    if info != 0:
                        class_b.append((base + cand, info))
                    else:
                        class_a.append(base + cand)
            pos = raw.find(needle, pos + 1)
    return class_a, class_b


def run_probe_identify(h, modbase, class_b):
    if not class_b:
        return {}
    for idx, (obj, info) in enumerate(class_b):
        write_fstring(h, info + INFO_HTTPIP, PROBE_TEXT)
        print("  probe->obj=0x%x info=0x%x info+128='%s'" % (
            obj, info, read_fstring(h, info + INFO_HTTPIP)))
    time.sleep(PROBE_WAIT_S)
    identified = {}
    for idx, (obj, info) in enumerate(class_b):
        mirrored = read_fstring(h, obj + OBJ_HTTPIP_OFF)
        if mirrored == PROBE_TEXT:
            identified[obj] = info
            print("  IDENTIFIED nesysObject: obj=0x%x info=0x%x (+1608 mirrors probe)" % (obj, info))
    return identified


def main():
    mode = "full"
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose":
        mode = "diagnose"

    pid = find_pid()
    if not pid:
        print("game not found; waiting for AcrGame-Win64-Shipping.exe (max 600s)...")
        deadline = time.time() + 600
        while not pid and time.time() < deadline:
            time.sleep(2)
            pid = find_pid()
        if not pid:
            print("TIMEOUT: game never appeared")
            return
    print("pid:", pid)
    modbase, modsize = module_base(pid)
    print("modbase: 0x%x  modsize: 0x%x" % (modbase or 0, modsize or 0))
    if not modbase:
        print("can't resolve module base")
        return
    h = open_game(pid)
    if not h:
        print("OpenProcess failed, err:", ctypes.get_last_error())
        return
    print("open ok")

    class_a, class_b = find_candidates(h, modbase, modsize)
    print("candidates  class_a(info==0, write +1608): %d" % len(class_a))
    for idx, obj in enumerate(class_a[:15]):
        print("    A obj=0x%x +1608='%s'" % (obj, read_fstring(h, obj + OBJ_HTTPIP_OFF)))
    print("candidates  class_b(info!=0, write info+128): %d" % len(class_b))
    for idx, (obj, info) in enumerate(class_b[:15]):
        print("    B obj=0x%x info=0x%x httpip='%s' +1608='%s'" % (
            obj, info, read_fstring(h, info + INFO_HTTPIP), read_fstring(h, obj + OBJ_HTTPIP_OFF)))

    if mode == "diagnose":
        kernel32.CloseHandle(h)
        print("DIAGNOSE_DONE")
        return

    identified = run_probe_identify(h, modbase, class_b)
    kernel32.CloseHandle(h)

    if identified:
        # Theory B: write the real httpip into identified info+128
        h = open_game(pid)
        for obj, info in identified.items():
            old = read_fstring(h, info + INFO_HTTPIP)
            print("  fixing obj=0x%x info+128 '%s' -> '%s'" % (obj, old, HTTPIP_TEXT))
            write_fstring(h, info + INFO_HTTPIP, HTTPIP_TEXT)
            # restore +1608 mirror consistency
            write_fstring(h, obj + OBJ_HTTPIP_OFF, HTTPIP_TEXT)
        print("CFG arm:", arm_config(h, modbase))
        print("FIX_DONE")
        return

    # Theory A fallback / plain: write directly into +1608 for class_a
    if class_a:
        h = open_game(pid)
        print("Theory B identified nothing; writing +1608 directly for %d class_a candidates" % len(class_a))
        for obj in class_a:
            print("  write +1608 obj=0x%x -> '%s'" % (obj, HTTPIP_TEXT))
            write_fstring(h, obj + OBJ_HTTPIP_OFF, HTTPIP_TEXT)
        print("CFG arm:", arm_config(h, modbase))
        print("FIX_DONE")
        kernel32.CloseHandle(h)
        return

    print("NO_CANDIDATES")


def arm_config(h, modbase):
    res = {}
    res["cfg_addr"] = bool(write_fstring(h, modbase + GLOB_CFG_ADDR, CFGADDR_TEXT))
    res["cfg_flag"] = bool(write_mem(h, modbase + GLOB_CFG_FLAG, b"\x01"))
    return res


if __name__ == "__main__":
    main()