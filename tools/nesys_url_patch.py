import sys
import time
import os
import ctypes

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import (
    find_pid, module_base, open_game, read_mem, write_mem, write_fstring,
    PROCESS_ALL_ACCESS, MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE,
)

# --- fixed addrs (relative to module image base), from IDA disassembly ---
JNZ_RVA = 0x2C36309      # jnz loc_142C363AE  (GetNesysInfo path) -> NOP to force mock URL
JNZ_OLD = b"\x0f\x85\x9f\x00\x00\x00"
JNZ_NEW = b"\x90" * 6
CFG_FLAG_RVA = 0x8EE1804  # byte_148EE1804 config-armed flag (backup arm)
CFG_ADDR_RVA = 0x8EE17B8  # qword_148EE17B8 config matching address FString (backup)

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
GAME_ARGS = [
    "-UseConfigMatchingServer=1",
    "-DefaultMatchingServerAddress=127.0.0.1:6666",
    "-HttpServerAddress=127.0.0.1:4001",
    "-log",
]
LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"

SUCCESS_PATTERNS = [
    "GetHostAddress / HostURL[http://dev.starwing.jp/mock",
    "OnReceiveResponseMatchingServer / _IsSuccess[1]",
    "SetConnectAddress / address[",
    "bHttpSuccess[1]",
    "GetNesysGameServerHttpIP is empty.",
]

# --- offline fallback URL constant rewrite (G41/G43: UNRESOLVED) ---
# The client's RequestPlayerLogin POSTs to a hardcoded, unreachable offline URL.
# Same 35-char UTF-16 replacement so net/http still finds the string in place.
OFFLINE_URL_OLD = "http://api.example.com:8080/offline"
OFFLINE_URL_NEW = "http://dev.starwing.jp/mock/offline"
OFFLINE_URL_RVAS = [
    0x797E820,   # RVA = raw file offset 0x797D820 + 0x1000 (.rdata)
    0x7980530,   # RVA = raw file offset 0x797F530 + 0x1000
    0x79805B0,   # RVA = raw file offset 0x797F5B0 + 0x1000
]

PAGE_EXECUTE_READWRITE = 0x40
PAGE_READONLY = 0x02
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000


def patch_code(h, base):
    addr = base + JNZ_RVA
    old = read_mem(h, addr, len(JNZ_OLD))
    if old == JNZ_NEW:
        return True
    ok = write_mem(h, addr, JNZ_NEW)
    after = read_mem(h, addr, len(JNZ_OLD))
    return ok and after == JNZ_NEW


def arm_config(h, base):
    res = {}
    res["flag"] = bool(write_mem(h, base + CFG_FLAG_RVA, b"\x01"))
    res["addr"] = bool(write_fstring(h, base + CFG_ADDR_RVA, "127.0.0.1:6666"))
    return res


def patch_offline_url(h, base):
    """Rewrite the hardcoded offline URL constant in .rdata (read-only pages).

    Same-length UTF-16 replacement so pointers into the string stay valid.
    Uses VirtualProtectEx to make each page writable, writes, restores.
    """
    old_blob = OFFLINE_URL_OLD.encode("utf-16-le")
    new_blob = OFFLINE_URL_NEW.encode("utf-16-le")
    if len(old_blob) != len(new_blob):
        raise ValueError("old/new offline URL lengths differ")
    results = {}
    for rva in OFFLINE_URL_RVAS:
        addr = base + rva
        before = read_mem(h, addr, len(old_blob))
        if not before:
            results[rva] = {"addr": addr, "read": False}
            continue
        page = ctypes.c_size_t()
        old_prot = ctypes.c_uint32(0)
        base_page = addr & ~0xFFF
        ok = ctypes.windll.kernel32.VirtualProtectEx(
            h, ctypes.c_void_p(base_page), 0x1000, PAGE_EXECUTE_READWRITE,
            ctypes.byref(old_prot))
        written = ctypes.c_size_t(0)
        wok = bool(write_mem(h, addr, new_blob))
        ctypes.windll.kernel32.VirtualProtectEx(
            h, ctypes.c_void_p(base_page), 0x1000, old_prot.value, ctypes.byref(page))
        after = read_mem(h, addr, len(new_blob))
        results[rva] = {
            "addr": addr,
            "before": before.decode("utf-16-le", "replace") if before else None,
            "write": bool(wok),
            "after": after.decode("utf-16-le", "replace") if after else None,
            "ok": bool(after) and after == new_blob,
        }
    return results


def tail_log(pos, maxlen=200000):
    try:
        size = os.path.getsize(LOG)
        if size <= pos:
            return pos, ""
        with open(LOG, "rb") as fh:
            fh.seek(max(0, size - maxlen))
            data = fh.read()
        return size, data.decode("utf-8", errors="replace")
    except Exception:
        return pos, ""


def wait_log(pos, needles, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        pos, text = tail_log(pos)
        for n in needles:
            if n in text:
                return True, n
        time.sleep(1)
    return False, None


def main():
    pid = find_pid()
    if not pid:
        print("launching game...")
        os.system('start "" "%s" %s' % (GAME_EXE, " ".join(GAME_ARGS)))
        deadline = time.time() + 240
        while not pid and time.time() < deadline:
            time.sleep(2)
            pid = find_pid()
        if not pid:
            print("ERROR: game never appeared")
            return
    print("pid:", pid)
    base, size = module_base(pid)
    print("modbase: 0x%x  modsize: 0x%x" % (base or 0, size or 0))
    if not base:
        print("ERROR: no module base")
        return
    h = open_game(pid)
    if not h:
        print("ERROR: OpenProcess failed", ctypes.get_last_error())
        return

    # apply the code patch now (module code is static; no need to wait for matching phase)
    addr = base + JNZ_RVA
    old = read_mem(h, addr, len(JNZ_OLD))
    print("[code] @base+0x%x  before: %s" % (JNZ_RVA, old.hex() if old else None))
    ok = patch_code(h, base)
    print("[code] patch applied: %s  after: %s" % (ok, (read_mem(h, addr, len(JNZ_OLD)) or b"").hex()))

    cfg = arm_config(h, base)
    print("[cfg] backup arm: flag=%s addr=%s" % (cfg["flag"], cfg["addr"]))

    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    hit, pat = wait_log(pos, SUCCESS_PATTERNS, 420)
    print("[log] %s" % (pat if hit else "no success yet"))

    # keep re-applying while watching
    start = time.time()
    while time.time() - start < 240:
        if find_pid() is None:
            print("GAME EXITED")
            return
        if not patch_code(h, base):
            print("[code] RE-patch needed")
        pos, text = tail_log(pos)
        for p in SUCCESS_PATTERNS:
            if p in text:
                print("  LOG HIT: " + p)
        time.sleep(3)

    print("DONE (watch 240s expired)")


if __name__ == "__main__":
    main()