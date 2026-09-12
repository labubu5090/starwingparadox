import ctypes
import os
import struct
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pid, module_base, open_game, read_mem, write_mem
from nesys_url_patch import patch_code as patch_url_code, arm_config, GAME_EXE, GAME_ARGS, LOG
from nesys_url_patch import patch_offline_url

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
CARD_FILE = os.path.join(TOOLS_DIR, "card.txt")


def load_card():
    if os.path.exists(CARD_FILE):
        with open(CARD_FILE, "r", encoding="utf-8") as fh:
            digits = "".join(ch for ch in fh.read() if ch.isdigit())
        if digits:
            return digits
    return "11111111111111111"

# --- fixed addresses (RVA relative to module base), from IDA ---
# ACPP_ReadCardMain::EnterPressed (sub_142ADCE40), code patch region:
P_SELECT_RVA = 0x2ADCE85   # movsxd rax, dword ptr [rbx+590h]  (DebugNesicaSelectNo) -> xor eax,eax
P_SELECT_OLD = bytes.fromhex("48 63 83 90 05 00 00")
P_SELECT_NEW = bytes.fromhex("31 c0 90 90 90 90 90")
P_JGE_RVA    = 0x2ADCE9A   # jge loc_142ADCFB6 (select>=count -> skip) -> NOP
P_JGE_OLD    = bytes.fromhex("0f 8d 16 01 00 00")
P_JGE_NEW    = b"\x90" * 6
P_SLOT_RVA   = 0x2ADCEA8   # mov rax, [rbx+5B0h] (slot array base) -> lea rax,[rip+fake]
P_SLOT_OLD   = bytes.fromhex("48 8b 83 b0 05 00 00")
LEA_NEXT     = P_SLOT_RVA + 7

# fabricated debug-table slot + card string in the writable .data zero-gap:
SLOT_RVA = 0x9001029   # segment .data RVA base 0x8957000 + run offset 0x6AA029
STR_RVA  = SLOT_RVA + 0x30
CARD     = load_card()

SUCCESS_PATTERNS = [
    "NESiCA_ID[%s" % CARD,
    "SetReadCardMode [PrefileRead",
    "SetReadCardMode [PermissionCheck",
    "SetReadCardMode [PremissionOfflineNesys]",
]

# --- shop-gate bypass (approved fix): ACPP_ReadCardMain::CheckValidNESiCA ---
#     CheckValidNESiCA rejects the card unless IsNesicaReceptionTime(0) passes,
#     and GetShopMinutes clamps the (unconfigurable) window to [1800,1919] minutes,
#     so the card can NEVER be accepted while the machine clock is outside it.
#     0x142AD8A51 call IsNesicaReceptionTime; 0x142AD8A56 test al,al;
#     0x142AD8A58 jnz +0x15 (75 15) -> accept  ====  jmp +0x15 (EB 15) always accept
P_SHOP_RVA  = 0x2AD8A58
P_SHOP_OLD  = bytes.fromhex("75 15")
P_SHOP_NEW  = bytes.fromhex("EB 15")

# --- offline-login bypass: CardError fires BEFORE HttpPlayerProfileLoad ---
#     Root cause: ReveiceTimeNESiCA (+0x4DA) only set by CheckValidNESiCA's accept
#     block @0x142AD8A6F, gated behind CheckInfoNESYS && IsOnlineStatus &&
#     IsNesicaReceptionTime. In the offline box IsOnlineStatus returns 0, so the
#     flags reset every Tick and Tick's RequestPlayerLogin case hits
#       cmp byte ptr [rdi+4DAh],0 ; jz CardError(NesicaReceiveTimeOver)
#       call IsOnlineStatus       ; jz CardError(OffLine)
#     BEFORE HttpPlayerProfileLoad is ever reached.
#     Patch 1: CheckValidNESiCA @0x142AD8A19 `call CheckInfoNESYS` (E8 D2 FE FF FF)
#              -> `jmp loc_142AD8A6F` (E9 51 00 00 00) straight to accept block
#              (sets ValidUseNESiCA=1 @+4CB, ReveiceTimeNESiCA=1 @+4DA, returns 1)
P_CVN_RVA    = 0x2AD8A19
P_CVN_OLD    = bytes.fromhex("E8 D2 FE FF FF")
P_CVN_NEW    = bytes.fromhex("E9 51 00 00 00")
#     Patch 2: IsOnlineStatus @0x142A64310 prologue `40 53 48` -> `B0 01 C3`
#              (mov al,1; ret) => always returns true (covers CheckValidNESiCA
#              internal gate + Tick's direct IsOnlineStatus guards)
P_ONLINE_RVA = 0x2A64310
P_ONLINE_OLD = bytes.fromhex("40 53 48")
P_ONLINE_NEW = bytes.fromhex("B0 01 C3")

# --- BeginPlay mode force-offline branch (2026-09-06) ---
#     With P_CVN applied, CheckValidNESiCA ALWAYS accepts -> ValidUseNESiCA(+0x4CB)=1,
#     so BeginPlay @0x142AD55FD always goes the `!=0` path -> CheckInfoNESYS() fails
#     (no cabinet info) -> mode 0 = InitializeErrorNesys (dead-end, "cannot get
#     cabinet information"). Force the offline branch:
#       0x142AD55F3: cmp byte ptr [rdi+4CBh],0
#       0x142AD55FD: jz loc_142AD5620   (74 21)  ->  jmp loc_142AD5620 (EB 21)
#     loc_142AD5620 = mode 1 (PremissionOfflineNesys) + SetPlayerProfileUserIdOffline(1),
#     exactly the state run4 had when EnterPressed -> RequestPlayerLogin succeeded.
P_BPFORCEOFF_RVA = 0x2AD55FD
P_BPFORCEOFF_OLD = bytes.fromhex("74 21")
P_BPFORCEOFF_NEW = bytes.fromhex("EB 21")

# --- experiment (EXP) patches (runtime only) ---
# E1: force EnterPressed to always take the OFFLINE branch (PremissionOfflineNesys 0x16):
#     0x142ADCF53: 75 09  (jnz +9 -> online path)  -> NOP NOP
EXP_FORCEOFF_RVA  = 0x2ADCF53
EXP_FORCEOFF_OLD  = bytes.fromhex("75 09")
EXP_FORCEOFF_NEW  = b"\x90\x90"
# E2: block BP-facing direct SetNextMode (execSetNextMode), the ONLY non-C++ mode setter:
#     0x142B2DFB7: E8 D4 61 FB FF  (call SetNextMode)  -> NOP x5
EXP_BLOCKBP_RVA   = 0x2B2DFB7
EXP_BLOCKBP_OLD   = bytes.fromhex("E8 D4 61 FB FF")
EXP_BLOCKBP_NEW   = b"\x90" * 5

EXP_PATTERNS = SUCCESS_PATTERNS + [
    "Tick / RequestPlayerLogin",
    "OnReceivePlayerProfi",
    "RequestPlayerLockTimerStart",
    "HttpRequestPlayerProfileLoad",
    "isValidUSBIO[1]",
]

EXP_ENABLED = os.environ.get("ACR_EXP", "").strip().lower() in ("1", "true", "e1", "e2", "e1e2")

# ======================================================================
# --- USBIO-valid bypass (isValidUSBIO, byte @obj+0x4B3) 2026-09 ---
# Battle input is gated on isValidUSBIO which is only ever set to 1 when a
# physical USBIO board (VID 0x780 / PID 0x438) is detected. Without arcade
# hardware the flag stays 0 forever and the mech never receives movement/fire,
# regardless of keyboard/XInput bindings in DefaultInput.ini.
#
# Reads of +0x4B3 are INLINED at many sites (getter @0x2A0FDE0 has only 2
# direct callers), so patching a single getter is not enough. Instead force
# every WRITE site to produce 1 (all replacements are same-length bytes):
#   0x2804F92  init: mov [rcx+0x4B3],dil (param)      -> mov byte[rcx+0x4B3],1
#   0x2804FFA  success: mov [rbx+0x4B3],1  (guarded)  -> also NOP the 5 branch
#              gates so this ALWAYS executes for the init object (raw offset
#              0x2804FCE/4FD5/4FDF/4FEF/4FF6 in the VID/PID check)
#   0x2F2B253  vtable setter: mov [rcx+0x4B3],r8b     -> mov byte[rcx+0x4B3],1
#   0x2F53FE6  dl-setter callers (each can force 0):
#              0x2A99AFD: sete dl (toggle)  -> NOP
#              0x2A9B333: xor edx,edx; call  -> NOP (teardown marks invalid)
#   0x2A0FDE0  getter: movzx eax,[rcx+0x4B3];ret     -> mov al,1; nops; ret
#
# USBIO Wrapper state forcing (2026-09): With isValidUSBIO=1 the per-frame
# UGALAXYIOWrapper::Update now actively polls our proxy DLL (thunk 0x2A0D2D0
# -> GALAXYIO_GetStatus at [+0x28]) and accepts only states {0,0x100,0x200}.
# The proxy returned constant 1 -> "UIO_STAT_ERROR[1]" logged EVERY frame and
# the slot state stored at [obj + hardno*4 + 0x160] stayed 1 (errored), so
# input never reached the mech. Fix: force the stored state byte to 0 (the
# value the real DLL returns for hardware slot 0) by turning the movsxd at
#   0x2A17B6D  movsxd rcx,[rsp+0x44]   (precedes the state store at 0x2A17B77)
# into `xor eax,eax; nop; nop; nop`. GetStatus return is then always 0 =
# valid => normal processing + no error log each frame.
USBIO_PATCHES = [
    ("jig-gate-je1",  0x2804FCE, bytes.fromhex("74 37"), b"\x90\x90"),
    ("jig-gate-je2",  0x2804FD5, bytes.fromhex("74 30"), b"\x90\x90"),
    ("jig-gate-jne1", 0x2804FDF, bytes.fromhex("75 26"), b"\x90\x90"),
    ("jig-gate-jne2", 0x2804FEF, bytes.fromhex("75 16"), b"\x90\x90"),
    ("jig-gate-jne3", 0x2804FF6, bytes.fromhex("75 0f"), b"\x90\x90"),
    ("usbio-init",   0x2804F92, bytes.fromhex("40 88 b9 b3 04 00 00"), bytes.fromhex("c6 81 b3 04 00 00 01")),
    ("usbio-setter", 0x2F2B253, bytes.fromhex("44 88 81 b3 04 00 00"), bytes.fromhex("c6 81 b3 04 00 00 01")),
    ("usbio-tgl",    0x2A99AFD, bytes.fromhex("e8 de a4 4b 00"), b"\x90" * 5),
    ("usbio-tear",   0x2A9B333, bytes.fromhex("e8 a8 8c 4b 00"), b"\x90" * 5),
    ("usbio-getter", 0x2A0FDE0, bytes.fromhex("0f b6 81 b3 04 00 00 c3"), bytes.fromhex("b0 01 90 90 90 90 90 c3")),
    ("usbio-status", 0x2A17B6D, bytes.fromhex("48 63 4c 24 44"), bytes.fromhex("31 c0 90 90 90")),
]


def patch_usbio(h, base):
    res = {}
    subset = os.environ.get("ACR_USBIO_SUBSET", "").strip()
    names = None
    if subset:
        names = {n.strip() for n in subset.split(",") if n.strip()}
        print("[usbio] subset=%s" % ",".join(sorted(names)))
    for name, rva, old, new in USBIO_PATCHES:
        if names is not None and name not in names:
            continue
        res[name] = _p(h, base, rva, old, new)
    return res


def patch_exp(h, base):
    res = {}
    if EXP_ENABLED:
        if "e1" in os.environ.get("ACR_EXP", ""):
            res["force-off"] = _p(h, base, EXP_FORCEOFF_RVA, EXP_FORCEOFF_OLD, EXP_FORCEOFF_NEW)
        if "e2" in os.environ.get("ACR_EXP", ""):
            res["block-bp"]  = _p(h, base, EXP_BLOCKBP_RVA, EXP_BLOCKBP_OLD, EXP_BLOCKBP_NEW)
        print("[exp] enabled=%s" % os.environ.get("ACR_EXP", ""))
    return res


def patch_code(h, base):
    res = {}
    res["select"] = _p(h, base, P_SELECT_RVA, P_SELECT_OLD, P_SELECT_NEW)
    res["jge"]    = _p(h, base, P_JGE_RVA, P_JGE_OLD, P_JGE_NEW)
    disp = (base + SLOT_RVA) - (base + LEA_NEXT)
    slot_new = b"\x48\x8d\x05" + struct.pack("<i", disp)
    res["slot"]   = _p(h, base, P_SLOT_RVA, P_SLOT_OLD, slot_new)
    res["shop"]   = _p(h, base, P_SHOP_RVA, P_SHOP_OLD, P_SHOP_NEW)
    res["cvn"]    = _p(h, base, P_CVN_RVA, P_CVN_OLD, P_CVN_NEW)
    res["online"] = _p(h, base, P_ONLINE_RVA, P_ONLINE_OLD, P_ONLINE_NEW)
    res["bpforceoff"] = _p(h, base, P_BPFORCEOFF_RVA, P_BPFORCEOFF_OLD, P_BPFORCEOFF_NEW)
    no_usbio = os.environ.get("ACR_NO_USBIO", "").strip().lower() in ("1", "true", "yes")
    if no_usbio:
        print("[usbio] SKIPPED (ACR_NO_USBIO set)")
    else:
        res.update(patch_usbio(h, base))
    return res


def _p(h, base, rva, old, new):
    addr = base + rva
    before = read_mem(h, addr, len(old))
    ok = write_mem(h, addr, new)
    after = read_mem(h, addr, len(new))
    return {"addr": addr, "before": before.hex() if before else None,
            "applied": bool(ok), "after": after.hex() if after else None,
            "ok": bool(ok) and after == new}


def write_slot(h, base):
    # 48-byte slot: +0 zero, +8 = card string ptr, +16 = dword char count
    slot = bytearray(0x30)
    struct.pack_into("<Q", slot, 0x08, base + STR_RVA)
    struct.pack_into("<I", slot, 0x10, len(CARD))
    ok_slot = write_mem(h, base + SLOT_RVA, bytes(slot))
    blob = CARD.encode("utf-16-le") + b"\x00\x00"
    ok_str = write_mem(h, base + STR_RVA, blob)
    back = read_mem(h, base + STR_RVA, len(blob))
    return {"slot": bool(ok_slot), "str": bool(ok_str),
            "readback": back == blob}


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

    # 1) mock URL claim (same as nesys_url_patch)
    print("[url] patch: %s" % patch_url_code(h, base))
    print("[url] config: %s" % arm_config(h, base))

    # 1b) rewrite the hardcoded offline URL constant so RequestPlayerLogin's
    #     profile-load POST reaches our mock instead of timing out -> CardError
    off = patch_offline_url(h, base)
    for rva, r in off.items():
        print("[url.offline.0x%X] %s" % (rva, r))

    # 2) card-registration fix
    data = write_slot(h, base)
    print("[fix] slot@base+0x%X  str@base+0x%X  slot=%s str=%s readback=%s"
          % (SLOT_RVA, STR_RVA, data["slot"], data["str"], data["readback"]))
    code = patch_code(h, base)
    for name, r in code.items():
        print("[fix.%s] before=%s applied=%s after=%s ok=%s"
              % (name, r["before"], r["applied"], r["after"], r["ok"]))
    code.update(patch_exp(h, base))
    for name, r in code.items():
        if name.startswith("force") or name.startswith("block"):
            print("[exp.%s] before=%s applied=%s after=%s ok=%s"
                  % (name, r["before"], r["applied"], r["after"], r["ok"]))

    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    hit, pat = wait_log(pos, EXP_PATTERNS, 200)
    print("[log] %s" % (pat if hit else "no success yet"))

    start = time.time()
    while time.time() - start < 240:
        if find_pid() is None:
            print("GAME EXITED")
            return
        if not all(r["ok"] for r in code.values()):
            print("[fix] RE-patch needed")
            code.update(patch_code(h, base))
            code.update(patch_exp(h, base))
            for name, r in code.items():
                if not r["ok"]:
                    print("[re.%s] ok=%s" % (name, r["ok"]))
        pos, text = tail_log(pos)
        for p in EXP_PATTERNS:
            if p in text:
                print("  LOG HIT: " + p)
        time.sleep(3)

    print("DONE (watch 240s expired)")


if __name__ == "__main__":
    main()