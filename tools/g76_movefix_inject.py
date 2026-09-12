"""g76_movefix_inject.py - runtime-only fix for the 8v8 local-player movement freeze.

Root cause (IDA decompile of ACPP_PlayerControllerBattle::TickInputMove @ 0x142257210):
  The only code that calls ACPP_CharacterEvent::SetMoveFowardValue / SetMoveRightValue
  is gated behind the machine "aging" flag:

      0x1422572DF  40 38 B8 AF 01 00 00   cmp   byte ptr [rax+1AFh], dil   ; m_AgingFlag
      0x1422572E6  0F 85 0A 02 00 00      jnz   loc_1422574F6              ; if aged -> SKIP move apply

  If m_AgingFlag is set, the whole movement block (incl. the actual SetMove*Value)
  is skipped, so the local mecha receives the input but never moves (camera stays
  Cockpit, mecha frozen at spawn, becomes a sitting duck -> 168 respawns).

  Fix: NOP the jnz so the move-apply always runs. Memory-only (WriteProcessMemory),
  NO exe/binary modification. --restore writes the original 6 bytes back.

Same pattern as weaponmanager_crashfix_inject.py / acr_card_fix_patch.py:
  byte-exact pristine assert before write, page-protection flip, restore option.
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
LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"

PAGE_EXECUTE_READWRITE = 0x40

# (rva, pristine_old, patched_new)  - absolute 0x1422572E6 - imagebase 0x140000000
#   jnz loc_1422574F6  ->  6x NOP
MOVE_PATCHES = [
    ("aging-gate", 0x22572E6,
     bytes.fromhex("0f850a020000"),
     bytes.fromhex("909090909090")),
]


def vprotect(h, addr, size, new_prot):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, new_prot, ctypes.byref(old))
    return bool(ok), old.value


def patch_bytes(h, base, rva, expect, want):
    """Write want over expect (same length) with pristine assert + prot flip."""
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

    for name, _, old, new in MOVE_PATCHES:
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

    for name, rva, old, new in MOVE_PATCHES:
        expect = old if not restore else new
        want = new if not restore else old
        r = patch_bytes(h, base, rva, expect, want)
        print("[%s] %s: %s before=%s after=%s ok=%s"
              % (name, "RESTORE" if restore else "APPLY",
                 r.get("reason"), r.get("before"), r.get("after"), r.get("ok")))

    print(("RESTORED" if restore else "APPLIED") + " (in-memory only; reboot game = back to pristine)")

    if not restore:
        pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
        start = time.time()
        print("watching for player move/respawn log 120s...")
        while time.time() - start < 120:
            if find_pid() is None:
                print("GAME EXITED")
                return
            try:
                with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(pos)
                    newlines = f.read().splitlines()
                    pos = f.tell()
            except (OSError, ValueError):
                newlines = []
            for ln in newlines:
                if ("E_RespawnReturn" in ln or "InitMovePram" in ln
                        or "Cockpit" in ln or "MoveForward" in ln or "SetInputType" in ln):
                    print("[LOG]", ln.strip()[:160])
            time.sleep(2)
        print("watch done")


if __name__ == "__main__":
    main()
