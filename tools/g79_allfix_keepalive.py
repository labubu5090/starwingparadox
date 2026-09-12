"""g79_allfix_keepalive.py - launch game + apply ALL runtime fixes and keep them alive.

Combines what previously ran as separate injectors (each rebooting the game and
home-growing their own patches, so the last one to run won the process):

  1. matching-server host fix   (JNZ->NOP @0x2C36309 forces SHORT_MOCK_URL / dev.starwing.jp)
  2. NESiCA card id mount       (slot FString + select/jge/slot redirection + w4)
  3. 2v2 InitalizeWeapon crash  (null-guard ARSkillDataPtr / SP-pack relays)
  4. sub_14243CA80 null-guard   (trampoline cave: rcx==NULL -> ret 0; otherwise
                                 replay mov [rsp+8],rbx and resume) - new in g79

All three are memory-only (WriteProcessMemory); NO exe modification. Re-applies any
patch that regresses (game re-condifies or a tick reverts it) until this process dies.
"""
from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import (  # noqa: E402
    find_pids, module_base, open_game, read_mem, write_mem,
)
import g111_drive_rewire  # noqa: E402

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
GAME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(GAME_EXE)))
# Working directory for the game: a child of GAME_DIR so the drive-rewired
# relative paths (..\\Saved, ..\\system) resolve inside the game directory.
BASE_DIR = os.path.join(GAME_DIR, "BASE")
GAME_ARGS = [
    "-UseConfigMatchingServer=1",
    "-DefaultMatchingServerAddress=127.0.0.1:6666",
    "-HttpServerAddress=127.0.0.1:4001",
    "-log",
]
LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"
PAGE_EXECUTE_READWRITE = 0x40

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
CARD_FILE = os.path.join(TOOLS_DIR, "card.txt")


def load_card():
    if os.path.exists(CARD_FILE):
        with open(CARD_FILE, "r", encoding="utf-8") as fh:
            digits = "".join(ch for ch in fh.read() if ch.isdigit())
        if digits:
            return digits
    return "11111111111111111"


CARD = load_card()

# ---------------- patch specs (RVA relative to module base) ----------------
# 1) matching server: force SHORT_MOCK_URL branch (host = dev.starwing.jp)
URL_JNZ = (0x2C36309, bytes.fromhex("0f859f000000"), bytes.fromhex("909090909090"))

# 2) NESiCA card mount
P_SELECT = (0x2ADCE85, bytes.fromhex("48638390050000"), bytes.fromhex("31c09090909090"))
P_JGE    = (0x2ADCE9A, bytes.fromhex("0f8d16010000"), bytes.fromhex("909090909090"))
P_SLOT   = 0x2ADCEA8
LEA_NEXT = P_SLOT + 7
SLOT_RVA = 0x9001029
STR_RVA  = SLOT_RVA + 0x30
W_ERROR  = (0x29C259B, b"\x72\x72", b"\xEB\x72")

# 3) 2v2 InitalizeWeapon crash
WM_PATCHES = [
    (0x0243CF13, bytes.fromhex("7460"), bytes.fromhex("7463")),
    (0x0243CF46, bytes.fromhex("752d"), bytes.fromhex("7530")),
    (0x0243CF50,
     bytes.fromhex("488bd80fb6483480e90280f9017716498bcee84928f9008b53304533c0488bc8e80bfbffff4885f6"),
     bytes.fromhex("85c074248b78300fb6483480e90280f9017715498bcee84528f90089fa4533c0488bc8e808fbffff")),
]

# 4) local-player movement freeze: m_AgingFlag gate in
#    ACPP_PlayerControllerBattle::TickInputMove @0x1422572DF cmp [rax+1AFh],dil
#    jnz loc_1422574F6 -> NOP so move-apply always runs (see g76_movefix_inject.py)
AGING_GATE = (0x22572E6, bytes.fromhex("0f850a020000"), bytes.fromhex("909090909090"))

# 5) UCPP_InfoParentWidget::SetUpHeadBarMob @0x1422B9E70: when MobInfomationes
#    array is empty/full it builds "空きなし" string + OutPutErrorLog spam every
#    tick. Patch 0x1422B9F84: xor eax,eax; jmp short epilogue@0x1422B9FD3
#    (return nullptr, skip ResizeGrow/OutPutErrorLog). Semantics unchanged.
HEADBAR = (0x22B9F84,
           bytes.fromhex("33d24c8964242048"),
           bytes.fromhex("33c0eb4b90909090"))

# 6) additional m_AgingFlag gates (jz→jmp to skip aging block)
# NOTE: do NOT NOP these. 0x201ba2f jz means "flag==0 => skip aging block";
#      NOPing forces deref of pAgingAIController ([Player+9E0h]) every tick
#      which is null outside aging battles => EXCEPTION_ACCESS_VIOLATION.
#      IsAging/SetAging fixes below already force flag=0 so the jz skips.
AGING_CAMERA  = (0x201ba2f, b"\x74\x33", b"\x74\x33")   # keep pristine (skip aging block)
AGING_ROT     = (0x2088ca2, b"\x74\x4a", b"\x74\x4a")   # keep pristine

# 7) IsAging -> xor eax,eax; ret (always "not aging"; keep camera unlocked)
ISAGING = (0x1e03ab0, bytes.fromhex("0fb681"), bytes.fromhex("31c0c3"))
# 8) SetAging -> mov byte[rcx+1AF],0; ret (force flag 0 on every write)
SETAGING = (0x1e0f3b0, bytes.fromhex("8891af010000c3cc"), bytes.fromhex("c681af01000000c3"))
# 9) GetCamType -> mov eax,1; ret (always cockpit-type camera path)
GETCAM = (0x20bbea0, bytes.fromhex("488bc4534156"), bytes.fromhex("b801000000c3"))
# 10) UCPP_BattleRecord::Tick cam/aging call -> NOP (fixes camera lock/jitter)
TICK_NOP = (0x2BDF790 + 0x34, bytes.fromhex("e867320000"), bytes.fromhex("9090909090"))
# 11) AddNicePlayID dispatcher call -> NOP (kill per-frame NicePlay spam)
NICEPLAY_NOP = (0x2BDA440 + 0x2E1, bytes.fromhex("e8da170000"), bytes.fromhex("9090909090"))
# 12) OnReceiveClearNicePlayDispatcher wrapper -> ret (avoid spam re-entry)
DISP_WRAP = (0x2BDBF00, bytes.fromhex("4883"), bytes.fromhex("c3cc"))
# 13) AddNicePlayID's 4 internal log calls (to sub_1431C8F80) -> NOP.
#     The log lines are printed from INSIDE UCPP_BattleRecord::AddNicePlayID
#     (CPP_BattleRecordData.cpp:2047/2055/2069/2079), so NOPing the single
#     dispatcher call (niceplay-nop) was not enough to stop the spam.
NICE_LOG_CALLS = [
    (0x2BDA67F, bytes.fromhex("e8fce85e00")),
    (0x2BDA854, bytes.fromhex("e827e75e00")),
    (0x2BDAA38, bytes.fromhex("e843e55e00")),
    (0x2BDAC09, bytes.fromhex("e872e35e00")),
]
# 14) UCPP_AcrUserWidget log spam from CPP_AcrUserWidget.cpp:246/284/290/296.
#     One WBP_InfoButtonWave_C_N AddToViewport prints 4 lines; every flying
#     phase creates several widget instances -> huge log spam.
WIDGET_LOG_CALLS = [
    (0x01D7EAF8, bytes.fromhex("e883a44401")),
    (0x01D7EBA9, bytes.fromhex("e8d2a34401")),
    (0x01D7EC2A, bytes.fromhex("e851a34401")),
    (0x01D92238, bytes.fromhex("e8436d4301")),
]

# 15) 2v2 InitalizeWeapon null-deref crash (this==NULL -> InitWeaponPack a1==NULL).
#     Both minidumps RIP=0x24358A2 (mov rax,[rcx+388h]). Guard at the single
#     choke point sub_14243CA80 entry via 5-byte jmp to a .text-tail cave:
#       test rcx,rcx; jnz +5; xor eax,eax; ret; mov [rsp+8],rbx; jmp 0x14243CA85
#     Rel32 payloads are base-dependent -> built at runtime (see dynamic_patches).
CA80_RVA = 0x0243CA80
CA80_CONT_RVA = 0x0243CA85
CAVE_RVA = 0x063FC89B
CA80_OLD = bytes.fromhex("48895c2408")
CAVE_OLD = b"\x00" * 18

# Simple 1..n-byte OR regex-free fixed patches keyed by name
CODE_PATCHES = [
    ("url-jnz",  URL_JNZ[0], URL_JNZ[1], URL_JNZ[2]),
    ("select",   P_SELECT[0], P_SELECT[1], P_SELECT[2]),
    ("jge",      P_JGE[0], P_JGE[1], P_JGE[2]),
    ("w4",       W_ERROR[0], W_ERROR[1], W_ERROR[2]),
    ("wm-cf13",  WM_PATCHES[0][0], WM_PATCHES[0][1], WM_PATCHES[0][2]),
    ("wm-cf46",  WM_PATCHES[1][0], WM_PATCHES[1][1], WM_PATCHES[1][2]),
    ("wm-cf50",  WM_PATCHES[2][0], WM_PATCHES[2][1], WM_PATCHES[2][2]),
    ("aging",    AGING_GATE[0], AGING_GATE[1], AGING_GATE[2]),
    ("aging-cam", AGING_CAMERA[0], AGING_CAMERA[1], AGING_CAMERA[2]),
    ("aging-rot", AGING_ROT[0], AGING_ROT[1], AGING_ROT[2]),
    ("headbar",  HEADBAR[0], HEADBAR[1], HEADBAR[2]),
    ("isaging",  ISAGING[0], ISAGING[1], ISAGING[2]),
    ("setaging", SETAGING[0], SETAGING[1], SETAGING[2]),
    ("getcam",   GETCAM[0], GETCAM[1], GETCAM[2]),
    ("tick-nop", TICK_NOP[0], TICK_NOP[1], TICK_NOP[2]),
    ("niceplay-nop", NICEPLAY_NOP[0], NICEPLAY_NOP[1], NICEPLAY_NOP[2]),
    ("disp-wrap", DISP_WRAP[0], DISP_WRAP[1], DISP_WRAP[2]),
]
# append the 4 niceplay-internal log NOPs under unique names
for _k, (_rva, _old) in enumerate(NICE_LOG_CALLS, start=1):
    CODE_PATCHES.append(("nice-log%d" % _k, _rva, _old, b"\x90" * len(_old)))
# append the 4 widget-log NOPs
for _k, (_rva, _old) in enumerate(WIDGET_LOG_CALLS, start=1):
    CODE_PATCHES.append(("widget-log%d" % _k, _rva, _old, b"\x90" * len(_old)))


def vprotect(h, addr, size, new_prot):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, new_prot, ctypes.byref(old))
    return bool(ok), old.value


def write_patch(h, base, name, rva, old, new):
    addr = base + rva
    before = read_mem(h, addr, len(old or new))
    if before is None:
        return {"name": name, "before": None, "applied": False, "ok": False, "reason": "unreadable"}
    if before == new:
        return {"name": name, "before": before.hex(), "applied": True, "ok": True, "reason": "already"}
    if old and before != old:
        return {"name": name, "before": before.hex(), "applied": False, "ok": False,
                "reason": "mismatch (not pristine)"}
    if write_mem(h, addr, new):
        after = read_mem(h, addr, len(new))
        if after == new:
            return {"name": name, "before": before.hex(), "after": after.hex(),
                    "applied": True, "ok": True, "reason": "direct"}
    ok_vp, old_prot = vprotect(h, addr, len(new), PAGE_EXECUTE_READWRITE)
    if not ok_vp:
        return {"name": name, "before": before.hex(), "applied": False, "ok": False,
                "reason": "vprotect-failed"}
    write_mem(h, addr, new)
    vprotect(h, addr, len(new), old_prot)
    after = read_mem(h, addr, len(new))
    return {"name": name, "before": before.hex(), "after": after.hex(),
            "applied": True, "ok": after == new, "reason": "with_vprotect"}


def slot_new(base):
    disp = (base + SLOT_RVA) - (base + LEA_NEXT)
    return b"\x48\x8d\x05" + struct.pack("<i", disp)


def build_ca80_patch(base):
    """(name, rva, old, new) list for the CA80 null-guard (base-dependent rel32)."""
    cave = base + CAVE_RVA
    jmp5 = b"\xe9" + struct.pack("<I", (cave - (base + CA80_RVA + 5)) & 0xFFFFFFFF)
    cave18 = b"\x48\x85\xc9\x75\x03\x31\xc0\xc3\x48\x89\x5c\x24\x08"
    cave18 += b"\xe9" + struct.pack("<I",
                                    ((base + CA80_CONT_RVA) - (cave + len(cave18) + 5)) & 0xFFFFFFFF)
    return [
        ("ca80-jmp", CA80_RVA, CA80_OLD, jmp5),
        ("ca80-cave", CAVE_RVA, CAVE_OLD, cave18),
    ]


# UStageWork::IsValidStageRuleID() crash: this->[0x60] (stage rule array) is NULL
# when entering national battle (matching UI). Function at 0x2dd8e50:
#   entry: mov [rsp+10h],edx / mov [rsp+8],rcx / sub rsp,38h ...
#   then this->[0x60] -> array[rule*0x38+0x34] deref crashes on NULL (RIP 0x2dd8eb4).
# Trampoline: jmp from entry to cave; if rcx==0 or [rcx+0x60]==0 -> return 0,
# else restore original stores+sub, jmp back to 0x2dd8e59 (sub rsp site), continue.
STAGE_RVA = 0x02DD8E50
STAGE_OLD = bytes.fromhex("8954241048")  # 5 bytes at entry (mov [rsp+10h],edx; 1st of mov [rsp+8],rcx)
STAGE_CONT_RVA = 0x02DD8E59             # resume point: sub rsp,38h
STAGE_CAVE_RVA = 0x63FC8AD              # verified 36 zero bytes


# 17) ACPP_WeaponBody::IsBulletCntEnable() crash:
#     EXCEPTION_ACCESS_VIOLATION reading address 0x00000554 @ func+0x19
#     ("movd xmm6, dword ptr [rcx+554h]" derefs this->+0x554 with this==NULL),
#     call chain ExecWeaponChangeCommand -> SeqAction -> Tick_Main
#     (cpp_weaponbody.cpp:1058 / cpp_characterevent.cpp:14971). Not caused by
#     any of our patches; server weapon data is complete. Whole function derefs
#     `this` ~7 times, so guard the single entry chokepoint (mirrors ca80):
#       test rcx,rcx; jnz +3; xor eax,eax; ret;  mov [rsp+8],rbx; jmp 0x14243D4A5
#     -> returns 0 (bullet count NOT enabled) when weapon body is NULL.
IBC_RVA = 0x0243D4A0
IBC_OLD = bytes.fromhex("48895c2408")    # 5 bytes at entry (mov [rsp+8],rbx)
IBC_CONT_RVA = 0x0243D4A5                # resume point: mov [rsp+0x10],rsi
IBC_CAVE_RVA = 0x63FC8D8                 # zero-fill gap after stage-cave (ends 0x63FC8CB)


def build_ibc_patch(base):
    """(name, rva, old, new) list for the IsBulletCntEnable null-guard."""
    cave = base + IBC_CAVE_RVA
    jmp5 = b"\xe9" + struct.pack("<I", (cave - (base + IBC_RVA + 5)) & 0xFFFFFFFF)
    cave18 = b"\x48\x85\xc9\x75\x03\x31\xc0\xc3"        # test rcx,rcx; jnz+3; xor eax,eax; ret
    cave18 += b"\x48\x89\x5c\x24\x08"                   # replay mov [rsp+8],rbx
    cave18 += b"\xe9" + struct.pack("<I",
                                    ((base + IBC_CONT_RVA) - (cave + len(cave18) + 5)) & 0xFFFFFFFF)
    return [
        ("ibc-jmp", IBC_RVA, IBC_OLD, jmp5),
        ("ibc-cave", IBC_CAVE_RVA, b"\x00" * len(cave18), cave18),
    ]


def build_stage_patch(base):
    cave = base + STAGE_CAVE_RVA
    jmp5 = b"\xe9" + struct.pack("<I", (cave - (base + STAGE_RVA + 5)) & 0xFFFFFFFF)
    # cave code: check rcx and [rcx+60h], return 0 if null, else resume
    #   test rcx,rcx / jz ret_zero(0x1c) / mov rax,[rcx+60h] / test rax,rax / jz ret_zero
    #   mov [rsp+10h],edx / mov [rsp+8],rcx / jmp back to 0x2dd8e59
    #   ret_zero: xor eax,eax / ret
    cave_code = b"\x48\x85\xc9\x74\x17"                     # test rcx,rcx; jz +0x17 -> off0x1c
    cave_code += b"\x48\x8b\x41\x60"                        # mov rax,[rcx+60h]
    cave_code += b"\x48\x85\xc0\x74\x0e"                    # test rax,rax; jz +0x0e -> off0x1c
    cave_code += b"\x89\x54\x24\x10"                        # mov [rsp+10h],edx
    cave_code += b"\x48\x89\x4c\x24\x08"                    # mov [rsp+8],rcx
    cave_code += b"\xe9" + struct.pack("<I",
                                       ((base + STAGE_CONT_RVA) - (cave + len(cave_code) + 5)) & 0xFFFFFFFF)
    cave_code += b"\x33\xc0\xc3"                            # ret_zero: xor eax,eax; ret
    cave_old = b"\x00" * len(cave_code)                      # verified zero region
    return [
        ("stage-jmp", STAGE_RVA, STAGE_OLD, jmp5),
        ("stage-cave", STAGE_CAVE_RVA, cave_old, cave_code),
    ]


def mount_card(h, base):
    res = {}
    slot = bytearray(0x30)
    struct.pack_into("<Q", slot, 0x08, base + STR_RVA)
    struct.pack_into("<I", slot, 0x10, len(CARD))
    if not write_mem(h, base + SLOT_RVA, bytes(slot)):
        res["slot-struct"] = {"ok": False}
        return res
    blob = CARD.encode("utf-16-le") + b"\x00\x00"
    write_mem(h, base + STR_RVA, blob)
    back = read_mem(h, base + STR_RVA, len(blob))
    res["slot-str"] = {"ok": back == blob, "card": CARD}
    res["slot-lea"] = write_patch(h, base, "slot", P_SLOT, None, slot_new(base))
    return res


def apply_all(h, base):
    res = {}
    for name, rva, old, new in CODE_PATCHES:
        res[name] = write_patch(h, base, name, rva, old, new)
    for name, rva, old, new in build_ca80_patch(base):
        res[name] = write_patch(h, base, name, rva, old, new)
    for name, rva, old, new in build_stage_patch(base):
        res[name] = write_patch(h, base, name, rva, old, new)
    for name, rva, old, new in build_ibc_patch(base):
        res[name] = write_patch(h, base, name, rva, old, new)
    res.update(mount_card(h, base))
    return res


def ensure_all_patched(pid):
    """Open one game process, (re)apply every patch + drive rewrite (idempotent),
    return failed names."""
    base, _size = module_base(pid)
    if not base:
        return ["no-modbase"]
    h = open_game(pid)
    if not h:
        return ["open-failed"]
    res = apply_all(h, base)
    ctypes.windll.kernel32.CloseHandle(h)
    rewire = g111_drive_rewire.rewire_process(pid)
    failed = [n for n, r in res.items() if not r.get("ok")]
    if not rewire.get("ok") or rewire.get("patched", 0) + rewire.get("already", 0) < 1:
        failed.append("drive-rewire")
    return failed


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


WATCH = ["NESiCA_ID[%s" % CARD, "OnReceivePlayerProfi", "InitalizeWeapon",
         "GetHostAddress / HostURL[http://dev.starwing.jp/mock"]


def launch_game():
    os.makedirs(BASE_DIR, exist_ok=True)
    print("launching game... cwd=%s" % BASE_DIR)
    subprocess.Popen([GAME_EXE] + GAME_ARGS, cwd=BASE_DIR,
                     creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))


def main():
    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    seen = set()
    while True:
        pids = find_pids()
        if not pids:
            launch_game()
            deadline = time.time() + 240
            while not pids and time.time() < deadline:
                time.sleep(2)
                pids = find_pids()
            if not pids:
                print("ERROR: game never appeared, retrying in 5s")
                time.sleep(5)
                continue
        for pid in pids:
            base, _size = module_base(pid)
            failed = ensure_all_patched(pid)
            if failed:
                # report a revert/apply failure once (throttled via print each loop)
                print("[patch] pid %d failed: %s" % (pid, failed))
        pos, text = tail_log(pos)
        for p in WATCH:
            if p in text and p not in seen:
                seen.add(p)
                print("[LOG] " + p)
        time.sleep(2)


if __name__ == "__main__":
    main()
