"""card_id_inject.py - Starwing ReadCard fix.

Watches the running AcrGame and, once the ACPP_ReadCardMain object appears
(ReadCard screen), writes a valid 17-digit NESiCA card into the object's

  +0x4E0 (1248) NESiCA_ID  (FString: ptr / count=17 / cap=17)
  +0x590 (1424) DebugNesicaSelectNo = 0
  +0x594 (1428) permission gate    = 0

and, if the resident debug-card table (+0x5B0) is empty, fabricates slot 0
(48-byte slot whose FString at +8 points at the same card string) so the
game's EnterPressed path can also read it.

Rationale (from IDA, Shipping exe):
  - EnterPressed (sub_142ADCE40) registers the card ONLY if
    DebugNesicaSelectNo>=0 && < count(+0x5B8); constructor sets it to -1 and
    the table is empty in a clean install, so no card ever gets registered.
  - The story flow re-checks the card by validating a1+1248 (sub_142C64E10:
    exactly 17 wide chars, all digits) in modes 22/24 (sub_142AD75E0 case
    22/23, 24); an invalid/empty card there leads to the timed-out
    PremissionOfflineNesys -> ReturnTitle we observed.

Usage:
  python card_id_inject.py            # run once; exits when card appears in log
  python card_id_inject.py --forever  # keep patching on every read-card attempt
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_mem_inject  # noqa: E402

LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\card_id_inject.txt"

CARD_ID = "11111111111111111"  # 17 digits, passes sub_142C64E10

PROCESS_ALL = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04


def _alloc_remote(h, size):
    k32 = card_mem_inject.k32
    k32.VirtualAllocEx.restype = ctypes.c_void_p
    k32.VirtualAllocEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]
    addr = k32.VirtualAllocEx(h, None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
    if not addr:
        raise OSError(f"VirtualAllocEx failed: {ctypes.get_last_error()}")
    return int(addr)


def _write_mem(h, addr, data: bytes):
    buf = ctypes.create_string_buffer(data, len(data))
    n = ctypes.c_size_t(0)
    ok = card_mem_inject.k32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, len(data), ctypes.byref(n))
    if not ok or n.value != len(data):
        raise OSError(f"WriteProcessMemory failed at 0x{addr:X}: {ctypes.get_last_error()}")


def _write_ptr(h, addr, val):
    _write_mem(h, addr, (val & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little"))


def _write_i32(h, addr, val):
    _write_mem(h, addr, (val & 0xFFFFFFFF).to_bytes(4, "little"))


def relaxed_candidate_ok(h, addr) -> dict | None:
    """Like card_mem_inject.candidate_ok but tolerates an EMPTY debug table."""
    mode = card_mem_inject.read_mem(h, addr + 0x4C0, 1)
    if mode is None or mode[0] not in (1, 2, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27):
        return None
    prev = card_mem_inject.read_mem(h, addr + 0x4C1, 1)
    if prev is None or prev[0] not in (1, 2, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 0):
        return None
    sel = card_mem_inject.read_u32(h, addr + 0x590)
    if sel is None:
        return None
    if not (-1 <= sel <= 16):
        return None
    gate = card_mem_inject.read_mem(h, addr + 0x594, 1)
    if gate is None or gate[0] > 1:
        return None
    # NESiCA_ID at +0x4E0 is (usually still) an empty FString on a fresh card screen
    idlen = card_mem_inject.read_u32(h, addr + 0x4E0 + 8)
    if idlen is None or idlen > 24:
        return None
    tptr = card_mem_inject.read_u64(h, addr + 0x5B0)
    count_b = card_mem_inject.read_mem(h, addr + 0x5B0 + 8, 8)
    if count_b is None:
        return None
    count = int.from_bytes(count_b[:4], "little")
    cap = int.from_bytes(count_b[4:], "little")
    if count > 1_000_000 or (count and not card_mem_inject.is_readable_ptr(h, tptr)):
        return None
    return {
        "addr": addr, "mode": mode[0], "prevMode": prev[0], "sel": sel,
        "tablePtr": tptr, "count": count, "cap": cap,
    }


def find_objects(h):
    found = []
    for base, size in card_mem_inject.regions(h):
        chunk = 0x100000
        off = 0
        while off < size:
            cur = base + off
            length = min(chunk, size - off)
            data = card_mem_inject.read_mem(h, cur, length)
            if data:
                for i in range(0, length - 0x5C0, 8):
                    c = relaxed_candidate_ok(h, cur + i)
                    if c:
                        found.append(c)
            off += length
    seen = {}
    for c in found:
        seen.setdefault(c["addr"], c)
    return list(seen.values())


def patch_object(h, obj):
    base = obj["addr"]
    # 1) card string
    card_ptr = _alloc_remote(h, 40)
    _write_mem(h, card_ptr, CARD_ID.encode("utf-16-le") + b"\x00\x00")
    # 2) NESiCA_ID at +0x4E0 (a1+1248) -> FString(ptr, count=17, cap=17)
    _write_ptr(h, base + 0x4E0, card_ptr)
    _write_i32(h, base + 0x4E0 + 8, 17)
    _write_i32(h, base + 0x4E0 + 12, 17)
    # 3) select slot 0 + clear gate
    _write_i32(h, base + 0x590, 0)
    _write_mem(h, base + 0x594, b"\x00")
    # 4) if the resident debug table is empty, fabricate slot 0
    if obj["count"] == 0:
        slot = _alloc_remote(h, 48)
        _write_ptr(h, slot + 8, card_ptr)
        _write_i32(h, slot + 16, 17)
        _write_ptr(h, slot + 24, 0)
        _write_i32(h, slot + 32, 0)
        _write_i32(h, slot + 40, 1)
        _write_ptr(h, base + 0x5B0, slot)
        _write_i32(h, base + 0x5B0 + 8, 1)
        _write_i32(h, base + 0x5B0 + 12, 1)
    return {
        "card_ptr": card_ptr, "slot_ptr": slot if obj["count"] == 0 else obj["tablePtr"],
    }


def pid_of():
    return card_mem_inject.find_game_pid()


def main():
    ap = argparse.ArgumentParser(description="Starwing ReadCard card-ID injector")
    ap.add_argument("--forever", action="store_true", help="keep watching after the first patch")
    args = ap.parse_args()

    report = []
    def log(msg):
        report.append(msg)
        print(msg, flush=True)
        _save(report)

    deadline = time.time() + 900
    last_log_pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    done = set()
    last_open_err = None
    last_open_err_t = 0
    last_beat = 0
    while time.time() < deadline:
        pid = pid_of()
        if pid is None:
            last_open_err = "no process"
            time.sleep(1.0)
            continue
        try:
            h = card_mem_inject.open_game(pid)
        except SystemExit as e:
            msg = str(e) or "open failed"
            # log a change of error state immediately, otherwise throttled
            if msg != last_open_err or time.time() - last_open_err_t > 30:
                log("[ERR] %s" % msg)
                last_open_err = msg
                last_open_err_t = time.time()
            time.sleep(1.0)
            continue
        last_open_err = None
        try:
            cands = find_objects(h)
        finally:
            card_mem_inject.k32.CloseHandle(h)

        if time.time() - last_beat > 20:
            log("[BEAT] pid=%d candidates=%d (scan ok)" % (pid, len(cands)))
            last_beat = time.time()

        for c in cands:
            if c["addr"] in done:
                continue
            log("[OBJ] 0x%016X mode=%d sel=%d count=%d" % (c["addr"], c["mode"], c["sel"], c["count"]))
            try:
                h = card_mem_inject.open_game(pid)
                try:
                    info = patch_object(h, c)
                    log("[PATCH] card=0x%016X slot=0x%016X sel=0 gate=0" % (info["card_ptr"], info["slot_ptr"]))
                    verify = relaxed_candidate_ok(h, c["addr"])
                    if verify:
                        cnt = card_mem_inject.read_u32(h, verify["addr"] + 0x4E0 + 8)
                        log("[VERIFY] NESiCA_ID len=%r DebugNesicaSelectNo=%d tableCount=%d" % (cnt, verify["sel"], verify["count"]))
                finally:
                    card_mem_inject.k32.CloseHandle(h)
            except OSError as e:
                log("[ERR] %s" % e)
            done.add(c["addr"])

        # scan log for a populated NESiCA_ID
        try:
            with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(last_log_pos)
                new = f.read().splitlines()
                last_log_pos = f.tell()
        except (OSError, ValueError):
            new = []
        for ln in new:
            if "NESiCA_ID" in ln:
                log("[LOG] " + ln.strip())
                if "NESiCA_ID[]" not in ln and "NESiCA_ID&#" not in ln:
                    log("[RESULT] CARD_ID_POPULATED")
                    _save(report)
                    return
        if not args.forever and done:
            return
        time.sleep(0.5)

    log("[RESULT] TIMEOUT_NO_CARD_ID")
    _save(report)


def _save(report):
    try:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(report) + "\n")
    except OSError:
        pass
    print("WROTE %s" % OUT)


if __name__ == "__main__":
    main()