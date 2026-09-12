"""g78_netfix_onlyjnz.py - minimal runtime-only fix for matching server empty host.

Previous full patch (nesys_url_patch.py) also rewrote .rdata offline URL + armed
config globals, which correlated with a MallocBinned2 heap corruption crash.
That extra memory churn is unnecessary: the single JNZ->NOP at 0x2C36309 forces
GetHostAddress to take the SHORT_MOCK_URL branch (dev.starwing.jp/mock), which
resolves via hosts to 127.0.0.1 and reaches the local backend (confirmed in log:
"Response url:[http://dev.starwing.jp/mock/matching/server] code:[200]").

This script applies ONLY that one code NOP. Memory-only, no exe modification.
--restore writes the original 6 bytes back. --launch starts the game if needed.
"""
from __future__ import annotations

import ctypes
import os
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import (  # noqa: E402
    find_pid, module_base, open_game, read_mem, write_mem,
)

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
GAME_ARGS = [
    "-UseConfigMatchingServer=1",
    "-DefaultMatchingServerAddress=127.0.0.1:6666",
    "-HttpServerAddress=127.0.0.1:4001",
    "-log",
]
PAGE_EXECUTE_READWRITE = 0x40

# jnz loc_142C363AE  ->  6x NOP  (forces SHORT_MOCK_URL branch)
JNZ_PATCH = ("matching-url-jnz", 0x2C36309,
             bytes.fromhex("0f859f000000"),
             bytes.fromhex("909090909090"))


def vprotect(h, addr, size, new_prot):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, new_prot, ctypes.byref(old))
    return bool(ok), old.value


def patch_bytes(h, base, rva, expect, want):
    addr = base + rva
    before = read_mem(h, addr, len(expect))
    if before is None:
        return {"addr": addr, "read": False, "reason": "unreadable", "ok": False}
    if before == want:
        return {"addr": addr, "before": before.hex(), "after": before.hex(),
                "applied": True, "ok": True, "reason": "already"}
    if before != expect:
        return {"addr": addr, "before": before.hex(), "after": before.hex(),
                "applied": False, "ok": False,
                "reason": "mismatch (not pristine bytes - ABORT)"}
    if write_mem(h, addr, want):
        after = read_mem(h, addr, len(want))
        if after == want:
            return {"addr": addr, "before": before.hex(), "after": after.hex(),
                    "applied": True, "ok": True, "reason": "direct"}
    ok_vp, old_prot = vprotect(h, addr, len(want), PAGE_EXECUTE_READWRITE)
    if not ok_vp:
        return {"addr": addr, "reason": "VirtualProtectEx failed", "ok": False}
    write_mem(h, addr, want)
    vprotect(h, addr, len(want), old_prot)
    after = read_mem(h, addr, len(want))
    return {"addr": addr, "before": before.hex(), "after": after.hex(),
            "applied": True, "ok": after == want, "reason": "with_vprotect"}


def main():
    restore = "--restore" in sys.argv
    wait_launch = "--launch" in sys.argv

    name, rva, old, new = JNZ_PATCH
    if len(old) != len(new):
        print("FATAL size mismatch", name)
        return

    pid = find_pid()
    if not pid:
        if not wait_launch:
            print("game not running (pid not found). use --launch to start it.")
            return
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
    print("modbase: 0x%x modsize: 0x%x" % (base or 0, size or 0))
    if not base:
        print("ERROR no module base")
        return
    h = open_game(pid)
    if not h:
        print("ERROR OpenProcess failed", ctypes.get_last_error())
        return

    expect = old if not restore else new
    want = new if not restore else old
    r = patch_bytes(h, base, rva, expect, want)
    print("[%s] %s: %s before=%s after=%s ok=%s"
          % (name, "RESTORE" if restore else "APPLY",
             r.get("reason"), r.get("before"), r.get("after"), r.get("ok")))

    print(("RESTORED" if restore else "APPLIED") + " (in-memory only; reboot game = back to pristine)")


if __name__ == "__main__":
    main()
