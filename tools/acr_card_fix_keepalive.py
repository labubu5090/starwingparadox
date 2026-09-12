import ctypes
import os
import struct
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pid, module_base, open_game, read_mem, write_mem
from nesys_url_patch import patch_code as patch_url_code, arm_config, GAME_EXE, GAME_ARGS, LOG

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
P_SELECT_RVA = 0x2ADCE85
P_SELECT_OLD = bytes.fromhex("48 63 83 90 05 00 00")
P_SELECT_NEW = bytes.fromhex("31 c0 90 90 90 90 90")
P_JGE_RVA    = 0x2ADCE9A
P_JGE_OLD    = bytes.fromhex("0f 8d 16 01 00 00")
P_JGE_NEW    = b"\x90" * 6
P_SLOT_RVA   = 0x2ADCEA8
P_SLOT_OLD   = bytes.fromhex("48 8b 83 b0 05 00 00")
LEA_NEXT     = P_SLOT_RVA + 7

SLOT_RVA = 0x9001029
STR_RVA  = SLOT_RVA + 0x30
CARD     = load_card()

# --- experiment patches (runtime only) ---
# E1: force EnterPressed offline branch (jnz +9 -> online) -> NOP NOP
EXP_FORCEOFF_RVA  = 0x2ADCF53
EXP_FORCEOFF_OLD  = bytes.fromhex("75 09")
EXP_FORCEOFF_NEW  = b"\x90\x90"
# E2: block BP-facing execSetNextMode call
EXP_BLOCKBP_RVA   = 0x2B2DFB7
EXP_BLOCKBP_OLD   = bytes.fromhex("E8 D4 61 FB FF")
EXP_BLOCKBP_NEW   = b"\x90" * 5
# E3 (optional): also NOP the online branch's SetNextMode inside EnterPressed
#   (the whole if/else that routes to RequestPlayerLogin):
#   0x142ADCF5E: B2 03 E8 EB 41 ...  keep as-is for now

# W4: suppress 'WidgetTree内の名前を確認して下さい[...]' spam. Triggered by
#   UCPP_PlayerTitleWidget::Resetup on every ReadCard entry (widget WBP_PlayerTitle /
#   WBP_PlayerTitle_2on2 intentionally absent from that tree). The emit function at
#   RVA 0x29C2590 is a pure logger: `cmp byte [rip+X], 2 (verbosity)  /  jb +0x72
#   (skip)  /  ...build FString + call Logf...  /  add rsp,48; ret`. Forcing the
#   jump to always take the skip path (jb -> jmp) removes the log lines with zero
#   functional side effects.
W_ERROR_RVA = 0x29C259B
W_ERROR_OLD = b"\x72\x72"
W_ERROR_NEW = b"\xEB\x72"

EXP_ENABLED = os.environ.get("ACR_EXP", "").strip().lower() in ("1", "true", "e1", "e2", "e1e2")

# Which patches are "experiments" (watch for regressions and report loudly)
EXP_RVAS = {
    "force-off": EXP_FORCEOFF_RVA,
    "block-bp":  EXP_BLOCKBP_RVA,
}

SUCCESS_PATTERNS = [
    "NESiCA_ID[%s" % CARD,
    "SetReadCardMode [PrefileRead",
    "SetReadCardMode [PermissionCheck",
    "SetReadCardMode [PremissionOfflineNesys]",
    "Tick / RequestPlayerLogin",
    "OnReceivePlayerProfi",
    "RequestPlayerLockTimerStart",
    "HttpRequestPlayerProfileLoad",
]


def _try(desc, fn):
    try:
        return fn()
    except Exception as e:
        print("[!] %s raised: %r" % (desc, e))
        return None


def read_verify(h, addr, want, name):
    got = read_mem(h, addr, len(want))
    return got == want, got.hex() if got else None


def write_patch(h, addr, old, new, name):
    before = read_mem(h, addr, len(old))
    if before == new:
        return {"addr": addr, "name": name, "before": new.hex(), "applied": True,
                "after": new.hex(), "ok": True, "reverted": False}
    if before != old:
        print("[%s] WARN: bytes at 0x%X are %s, expected old %s" % (name, addr, before.hex() if before else None, old.hex()))
    if not write_mem(h, addr, new):
        print("[%s] write failed addr=0x%X err=%d" % (name, addr, ctypes.get_last_error()))
        return {"addr": addr, "name": name, "before": before.hex() if before else None,
                "applied": False, "after": None, "ok": False, "reverted": False}
    after = read_mem(h, addr, len(new))
    ok = after == new
    reverted = (before == old)
    return {"addr": addr, "name": name, "before": before.hex() if before else None,
            "applied": True, "after": after.hex() if after else None, "ok": ok,
            "reverted": reverted}


def apply_all(h, base):
    res = {}
    res["url"] = _try("url patch", lambda: {"applied": patch_url_code(h, base)})
    if os.environ.get("ACR_ARM", "").strip() == "1":
        res["config"] = _try("config", lambda: dict(arm_config(h, base)))
    else:
        res["config"] = {"skipped": True, "reason": "pre-arm disabled; SetConnectAddress arms on HTTP 200"}

    slot = bytearray(0x30)
    struct.pack_into("<Q", slot, 0x08, base + STR_RVA)
    struct.pack_into("<I", slot, 0x10, len(CARD))
    write_mem(h, base + SLOT_RVA, bytes(slot))
    blob = CARD.encode("utf-16-le") + b"\x00\x00"
    write_mem(h, base + STR_RVA, blob)
    back = read_mem(h, base + STR_RVA, len(blob))
    res["slot-str"] = {"ok": back == blob}

    disp = (base + SLOT_RVA) - (base + LEA_NEXT)
    slot_new = b"\x48\x8d\x05" + struct.pack("<i", disp)
    res["select"] = write_patch(h, base + P_SELECT_RVA, P_SELECT_OLD, P_SELECT_NEW, "select")
    res["jge"]    = write_patch(h, base + P_JGE_RVA, P_JGE_OLD, P_JGE_NEW, "jge")
    res["slot"]   = write_patch(h, base + P_SLOT_RVA, P_SLOT_OLD, slot_new, "slot")

    if EXP_ENABLED:
        ex = os.environ.get("ACR_EXP", "")
        if "e1" in ex:
            res["e1"] = write_patch(h, base + EXP_FORCEOFF_RVA, EXP_FORCEOFF_OLD, EXP_FORCEOFF_NEW, "e1")
        if "e2" in ex:
            res["e2"] = write_patch(h, base + EXP_BLOCKBP_RVA, EXP_BLOCKBP_OLD, EXP_BLOCKBP_NEW, "e2")

    # W4 widget-tree error suppression (always apply).
    res["w4"] = write_patch(h, base + W_ERROR_RVA, W_ERROR_OLD, W_ERROR_NEW, "w4")
    return res


PATCH_SPECS = {
    "select": (P_SELECT_RVA, P_SELECT_OLD, P_SELECT_NEW),
    "jge":    (P_JGE_RVA, P_JGE_OLD, P_JGE_NEW),
    "e1":     (EXP_FORCEOFF_RVA, EXP_FORCEOFF_OLD, EXP_FORCEOFF_NEW),
    "e2":     (EXP_BLOCKBP_RVA, EXP_BLOCKBP_OLD, EXP_BLOCKBP_NEW),
    "w4":     (W_ERROR_RVA, W_ERROR_OLD, W_ERROR_NEW),
}


def slot_new_bytes(base):
    disp = (base + SLOT_RVA) - (base + LEA_NEXT)
    return b"\x48\x8d\x05" + struct.pack("<i", disp)


def slot_old_bytes():
    return P_SLOT_OLD


def verify_all(h, base, res):
    """Re-read every patch region every cycle; if a region regressed to OLD bytes
    (or drifted to anything != NEW), re-write it and report. Returns list of
    (name, patch_result) regressions detected this cycle."""
    re_patched = []
    specs = dict(PATCH_SPECS)
    specs["slot"] = (P_SLOT_RVA, slot_old_bytes(), slot_new_bytes(base))
    for name, (rva, _old, new) in specs.items():
        addr = base + rva
        got = read_mem(h, addr, len(new))
        if got == new:
            continue
        if not write_mem(h, addr, new):
            print("[!] re-write failed %s addr=0x%X err=%d" % (name, addr, ctypes.get_last_error()))
            continue
        after = read_mem(h, addr, len(new))
        r = {"name": name, "addr": addr, "before": got.hex() if got else None,
             "after": after.hex() if after else None, "ok": after == new}
        re_patched.append((name, r))
        if name in res:
            res[name] = r
    return re_patched


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


def main():
    launched = False
    pid = find_pid()
    if not pid:
        print("launching game...")
        os.system('start "" "%s" %s' % (GAME_EXE, " ".join(GAME_ARGS)))
        launched = True
        deadline = time.time() + 240
        while not pid and time.time() < deadline:
            time.sleep(2)
            pid = find_pid()
        if not pid:
            print("ERROR: game never appeared")
            return

    base, size = module_base(pid)
    print("pid: %d modbase: 0x%x modsize: 0x%x" % (pid, base or 0, size or 0))
    if not base:
        print("ERROR: no module base")
        return
    h = open_game(pid)
    if not h:
        print("ERROR: OpenProcess failed", ctypes.get_last_error())
        return

    res = apply_all(h, base)
    for name, r in res.items():
        print("[%s] %s" % (name, r))

    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    start = time.time()
    last_ok = time.time()
    reverbose = set()
    while time.time() - start < 360:
        if find_pid() is None:
            print("GAME EXITED")
            break
        re = verify_all(h, base, res)
        for name, r in re:
            tag = "%d" % r["addr"]
            if (name, tag) not in reverbose:
                print("[REVERT] %s addr=0x%X before=%s after=%s ok=%s" % (name, r["addr"], r["before"], r["after"], r["ok"]))
                reverbose.add((name, tag))
        pos, text = tail_log(pos)
        for p in SUCCESS_PATTERNS:
            if p in text:
                print("[LOG] " + p)
        time.sleep(0.5)

    print("DONE")


if __name__ == "__main__":
    main()