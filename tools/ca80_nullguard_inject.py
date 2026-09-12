"""ca80_nullguard_inject.py - runtime-only null-guard for the 2v2 InitalizeWeapon
crash (ACPP_WeaponPack::InitWeaponPack null-deref @0x388 this==NULL).

Root cause (confirmed via minidumps, both dumps RIP = 0x24358A2):
  ACPP_WeaponManager::InitalizeWeapon -> sub_14243CA80(a1 maybe NULL) ->
  sub_142435890(rcx=NULL) -> mov rax,[rcx+388h]  CRASH.

Fix: patch sub_14243CA80 entry (RVA 0x243CA80):
  - 5 bytes 48 89 5C 24 08 (mov [rsp+8],rbx)  ->  E9 rel32 -> cave
  cave payload (18 bytes, at RVA 0x063FC89B tail .text padding, no xrefs):
    test rcx,rcx
    jnz  +5
    xor  eax,eax
    ret                 ; NULL this -> no-op, eax=0
    mov  [rsp+8],rbx    ; replay encrypted prologue store
    jmp  loc_14243CA85  ; resume at mov [rsp+10h],rbp
Semantics: all 4 callers (3 calls in InitalizeWeapon + 1 tail-jmp in
sub_142431F90) never use CA80's return value on the NULL path except the tail
jmp which returns it up as "failed" (0).  Verified CA80's own later
mov rdi,[rbp+388h] is also covered by the entry guard.

Memory-only (WriteProcessMemory); NO exe modification.
"""
from __future__ import annotations

import ctypes
import os
import struct
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import (  # noqa: E402
    find_pids, module_base, open_game, read_mem, write_mem,
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

# RVAs (relative to module base; imagebase 0x140000000)
CA80_RVA = 0x0243CA80        # start of sub_14243CA80: mov [rsp+8],rbx (48 89 5C 24 08)
CA80_CONT_RVA = 0x0243CA85   # resume: mov [rsp+10h],rbp
CAVE_RVA = 0x063FC89B        # .text tail padding (357 x 0x00, no xrefs)

CA80_OLD = bytes.fromhex("48895c2408")          # 5 bytes
CAVE_OLD_BYTES = b"\x00" * 18


def vprotect(h, addr, size, new_prot):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, new_prot, ctypes.byref(old))
    return bool(ok), old.value


def build_patch(base):
    """Return (jmp5, cave18) byte strings for the given module base."""
    cave = base + CAVE_RVA
    jmp5 = b"\xe9" + struct.pack("<I", (cave - (base + CA80_RVA + 5)) & 0xFFFFFFFF)
    cave18 = b"\x48\x85\xc9\x75\x05\x31\xc0\xc3\x48\x89\x5c\x24\x08"
    cave18 += b"\xe9" + struct.pack("<I",
                                    ((base + CA80_CONT_RVA) - (cave + len(cave18) + 5)) & 0xFFFFFFFF)
    assert len(jmp5) == 5 and len(cave18) == 18
    return jmp5, cave18


def patch(h, base, addr, old, new):
    before = read_mem(h, addr, len(old))
    if before is None:
        return {"read": False, "before": None, "ok": False, "reason": "unreadable"}
    if before == new:
        return {"read": True, "before": before.hex(), "ok": True, "reason": "already"}
    if before != old:
        return {"read": True, "before": before.hex(), "ok": False, "reason": "mismatch"}
    if write_mem(h, addr, new):
        if read_mem(h, addr, len(new)) == new:
            return {"read": True, "before": before.hex(), "ok": True, "reason": "direct"}
    ok_vp, old_prot = vprotect(h, addr, len(new), PAGE_EXECUTE_READWRITE)
    if not ok_vp:
        return {"read": True, "before": before.hex(), "ok": False, "reason": "vprotect-failed"}
    write_mem(h, addr, new)
    vprotect(h, addr, len(new), old_prot)
    after = read_mem(h, addr, len(new))
    return {"read": True, "before": before.hex(), "after": after.hex(),
            "ok": after == new, "reason": "with_vprotect"}


def apply_all(h, base):
    jmp5, cave18 = build_patch(base)
    r = {}
    r["ca80-jmp"] = patch(h, base, base + CA80_RVA, CA80_OLD, jmp5)
    r["ca80-cave"] = patch(h, base, base + CAVE_RVA, CAVE_OLD_BYTES, cave18)
    return r


def patch_instance(pid):
    """Open one game process, apply the guard, return (base, summary)."""
    base, size = module_base(pid)
    if not base:
        return None, {"base": None, "ok": False, "reason": "no-modbase"}
    h = open_game(pid)
    if not h:
        return base, {"base": base, "ok": False, "reason": "open-failed"}
    res = apply_all(h, base)
    ok = all(r.get("ok") for r in res.values())
    ctypes.windll.kernel32.CloseHandle(h)
    return base, {"base": base, "ok": ok, "patches": res}


def recheck_instance(pid):
    """Re-apply guard if reverted. Returns (patched_something, summary)."""
    base, size = module_base(pid)
    if not base:
        return False, {"base": None, "ok": False, "reason": "no-modbase"}
    h = open_game(pid)
    if not h:
        return False, {"base": base, "ok": False, "reason": "open-failed"}
    jmp5, cave18 = build_patch(base)
    fixed = []
    if read_mem(h, base + CA80_RVA, len(jmp5)) != jmp5:
        fixed.append(("ca80-jmp", patch(h, base, base + CA80_RVA, CA80_OLD, jmp5)))
    if read_mem(h, base + CAVE_RVA, len(cave18)) != cave18:
        fixed.append(("ca80-cave", patch(h, base, base + CAVE_RVA, CAVE_OLD_BYTES, cave18)))
    ok = True
    for name, r in fixed:
        ok &= bool(r.get("ok"))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(fixed), {"base": base, "ok": ok, "fixed": [n for n, _ in fixed]}


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


WATCH = ["InitWeaponPack", "InitalizeWeapon", "Fatal error", "FatalError",
         "Assertion failed", "ACPP_WeaponPack"]


def main():
    pids = find_pids()
    if not pids:
        print("launching game...")
        os.system('start "" "%s" %s' % (GAME_EXE, " ".join(GAME_ARGS)))
        deadline = time.time() + 240
        while not pids and time.time() < deadline:
            time.sleep(2)
            pids = find_pids()
        if not pids:
            print("ERROR: game never appeared")
            return
    for pid in pids:
        base, r = patch_instance(pid)
        print("pid %d base 0x%x ok=%s reason=%s" % (pid, base or 0, r.get("ok"), r.get("reason")))
        for name, pr in (r.get("patches") or {}).items():
            print("   [%s] reason=%s ok=%s before=%s" % (name, pr.get("reason"),
                                                         pr.get("ok"), (pr.get("before") or "")[:24]))

    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    print("[fix] ca80 null-guard applied to all instances. keepalive running.")
    start = time.time()
    while time.time() - start < 1200:
        now_pids = find_pids()
        if not now_pids:
            print("GAME EXITED")
            return
        for pid in now_pids:
            fixed, r = recheck_instance(pid)
            if fixed:
                print("[RE-APPLIED] pid %d %s" % (pid, [n for n in r.get("fixed")]))
        pos, text = tail_log(pos)
        if "Fatal error" in text or "FatalError" in text:
            print("[LOG FATAL]")
            print(text[-8000:])
            return
        time.sleep(1)


if __name__ == "__main__":
    main()