"""weaponmanager_crashfix_inject.py - runtime-only fix for the 2v2 setup crash.

ACPP_WeaponManager::InitalizeWeapon null-deref (EXCEPTION_ACCESS_VIOLATION @ 0x34)
when the owner has an AR skill whose index is -1 in SubWeaponDataTable:
GetSubWeaponDataInstancePtr returns nullptr, then `movzx ecx,[rax+34h]`.

Same pattern as acr_card_fix_patch.py / patch_online_gate.py / card_mem_inject.py:
NO exe patching; NO binary file modification. Runtime WriteProcessMemory only.

Patches (RVA from module base, IDA at imagebase 0x140000000):
  site1  0x0243CF13  74 60 -> 74 63   relay outer SP-pack jz CF75 -> CF78
  site2  0x0243CF46  75 2D -> 75 30   relay object-flag jnz CF75 -> CF78
  site3  0x0243CF50  40 bytes rewrite -> null-guard ARSkillDataPtr; skip SP init
         when GetARSkillDataPtr()==nullptr (Type read @[rax+34h] no longer crashed)
"""
from __future__ import annotations

import ctypes
import os
import struct
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

# (rva, old, new) — from IDA Analysis / Promise of the exact bytes in the pristine exe
CRASHFIX_PATCHES = [
    ("cf13-jz", 0x0243CF13,
     bytes.fromhex("7460"),
     bytes.fromhex("7463")),
    ("cf46-jnz", 0x0243CF46,
     bytes.fromhex("752d"),
     bytes.fromhex("7530")),
    ("cf50-nullguard", 0x0243CF50,
     bytes.fromhex("488bd80fb6483480e90280f9017716498bcee84928f9008b53304533c0488bc8e80bfbffff4885f6"),
     bytes.fromhex("85c074248b78300fb6483480e90280f9017715498bcee84928f90089fa4533c0488bc8e80bfbffff")),
]


def vprotect(h, addr, size, new_prot):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, new_prot, ctypes.byref(old))
    return bool(ok), old.value


def patch_with_protect(h, base, rva, old, new):
    """Write new bytes over old (must be same length), flipping page protection
    as needed (code section is typically PAGE_EXECUTE_READ)."""
    addr = base + rva
    before = read_mem(h, addr, len(old))
    if before is None:
        return {"addr": addr, "read": False, "before": None,
                "applied": False, "after": None, "ok": False, "reason": "unreadable"}
    if before == new:
        return {"addr": addr, "read": True, "before": before.hex(),
                "applied": True, "after": before.hex(), "ok": True, "reason": "already_patched"}
    if before != old:
        return {"addr": addr, "read": True, "before": before.hex(),
                "applied": False, "after": before.hex(), "ok": False,
                "reason": "mismatch (not pristine bytes)"}

    # try direct write first (page may already be writable)
    ok_direct = bool(write_mem(h, addr, new))
    after = read_mem(h, addr, len(new))
    if ok_direct and after == new:
        return {"addr": addr, "read": True, "before": before.hex(),
                "applied": True, "after": after.hex(), "ok": True, "reason": "direct"}

    # flip protection, write, restore
    ok_vp, old_prot = vprotect(h, addr, len(new), PAGE_EXECUTE_READWRITE)
    if not ok_vp:
        return {"addr": addr, "read": True, "before": before.hex(),
                "applied": False, "after": after.hex() if after else None, "ok": False,
                "reason": "VirtualProtectEx failed"}
    write_mem(h, addr, new)
    vprotect(h, addr, len(new), old_prot)
    after = read_mem(h, addr, len(new))
    return {"addr": addr, "read": True, "before": before.hex(),
            "applied": True, "after": after.hex(),
            "ok": after == new, "reason": "with_vprotect"}


def apply_all(h, base):
    return {name: patch_with_protect(h, base, rva, old, new)
            for name, rva, old, new in CRASHFIX_PATCHES}


def main():
    # regenerate STATIC asserts: patch length equality checked here
    for name, _, old, new in CRASHFIX_PATCHES:
        if len(old) != len(new):
            print("FATAL: size mismatch in %s" % name)
            return

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
    print("open ok")

    ok_all = True
    for name, r in apply_all(h, base).items():
        print("[%s] reason=%s applied=%s before=%s after=%s ok=%s"
              % (name, r.get("reason"), r.get("applied"),
                 (r.get("before") or "")[:32], (r.get("after") or "")[:32], r.get("ok")))
        if not r.get("ok"):
            ok_all = False

    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    print("[fix] all applied=%s  (keepalive until 2v2 setup is exercised)" % ok_all)

    start = time.time()
    while time.time() - start < 240:
        if find_pid() is None:
            print("GAME EXITED")
            return
        if not ok_all:
            ok_all = True
            for name, r in apply_all(h, base).items():
                if not r.get("ok"):
                    print("[re.%s] %s" % (name, r.get("reason")))
                    ok_all = False
            print("[fix] re-patch ok=%s" % ok_all)
        try:
            with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(pos)
                new = f.read().splitlines()
                pos = f.tell()
        except (OSError, ValueError):
            new = []
        for ln in new:
            if "InitalizeWeapon" in ln and "GetSubWeaponDataInstancePtr _index[-1]" in ln:
                print("[LOG] " + ln.strip())
        time.sleep(2)

    print("DONE (watch 240s expired)")


if __name__ == "__main__":
    main()