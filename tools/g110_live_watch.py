"""g110_live_watch.py - live crash watcher for the Starwing game.

Tails the game log for fatal markers, detects new CrashReportClient folders,
parses UE4Minidump.dmp (fault RIP/RVA + InitWeaponPack-window return addrs),
and reports game-process liveness. Runs until --maxsec or a crash is found.
"""
import json
import os
import struct
import sys
import time

CRASH_DIR = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Crashes"
LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"
PROC = "AcrGame-Win64-Shipping.exe"
MODSIZE = 0x9ec4000
FIXED_BASE = 0x7ff6c8f20000

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pids, module_base  # noqa: E402

FATAL_MARKS = ["Fatal error", "FatalError", "Session Timeout", "Is Not Success",
               "MessageId:20", "message:http:unknown", "OnServerError", "game server error"]


def read_crashes():
    try:
        return {d for d in os.listdir(CRASH_DIR) if d.startswith("UE4CC-Windows")}
    except Exception:
        return set()


def parse_dmp(path, modbase):
    data = open(path, "rb").read()
    sig, _v, nstreams, dir_rva = struct.unpack_from("<IIII", data, 0)[0:4]
    streams = {}
    for i in range(nstreams):
        st, sz, rva = struct.unpack_from("<III", data, dir_rva + i * 12)
        streams.setdefault(st, []).append((rva, sz))
    out = ["dmp=%s sig=%08x" % (os.path.basename(path), sig)]
    tid = rip = rsp = None
    if 6 in streams:
        rva, _ = streams[6][0]
        tid, = struct.unpack_from("<I", data, rva)
        ctx_size, ctx_rva = struct.unpack_from("<II", data, rva + 8 + 0x98)
        rip = struct.unpack_from("<Q", data, ctx_rva + 248)[0]
        rsp = struct.unpack_from("<Q", data, ctx_rva + 152)[0]
        out.append("  fault tid %d RIP %#x RVA %#x RSP %#x" % (tid, rip, rip - modbase, rsp))
    stack = None
    if 3 in streams:
        trva, _ = streams[3][0]
        nthreads, = struct.unpack_from("<I", data, trva)
        for i in range(nthreads):
            base = trva + 4 + i * 56
            t, = struct.unpack_from("<I", data, base)
            s_start, s_size, s_rva = struct.unpack_from("<QII", data, base + 32)
            if t == tid and s_size:
                stack = data[s_rva:s_rva + s_size]
                out.append("  fault thread stack: start %#x size 0x%x" % (s_start, s_size))
                break
    if stack is None and 5 in streams:
        mrva, _ = streams[5][0]
        nreg, = struct.unpack_from("<I", data, mrva)
        for i in range(nreg):
            start, dsize, drva = struct.unpack_from("<QII", data, mrva + 4 + i * 16)
            if rsp is not None and start <= rsp < start + dsize:
                stack = data[drva:drva + min(dsize, 0x4000)]
                out.append("  stack from memory-list stream, size 0x%x" % len(stack))
                break
    if stack:
        for i in range(0, len(stack) - 7, 8):
            val = struct.unpack_from("<Q", stack, i)[0]
            if modbase <= val < modbase + MODSIZE:
                r = val - modbase
                if 0x2400000 <= r <= 0x2440000:
                    out.append("  [battle-window +0x%04x] %#x rva=%#x" % (i, val, r))
    return "\n".join(out)


def tail_log(pos, maxlen=9000):
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


def modbase_of():
    try:
        pids = find_pids()
        if pids:
            b, _ = module_base(pids[0])
            if b:
                return b
    except Exception:
        pass
    return FIXED_BASE


def main():
    maxsec = float(sys.argv[1]) if len(sys.argv) > 1 else 1800
    base = modbase_of()
    known = read_crashes()
    try:
        pos = os.path.getsize(LOG)
    except Exception:
        pos = 0
    print("[watch] base=%#x known_crashes=%d log_pos=%d proc=%s" % (base, len(known), pos, PROC))
    start = time.time()
    last_beat = 0
    while time.time() - start < maxsec:
        now_procs = find_pids()
        new_crashes = read_crashes() - known
        for name in sorted(new_crashes):
            known.add(name)
            dmp = os.path.join(CRASH_DIR, name, "UE4Minidump.dmp")
            print("[CRASH] %s" % name, flush=True)
            if os.path.exists(dmp):
                print(parse_dmp(dmp, base), flush=True)
            else:
                print("  no UE4Minidump.dmp in new crash folder", flush=True)
        pos, text = tail_log(pos)
        if text:
            low = text.lower()
            marks = [m for m in FATAL_MARKS if m.lower() in low]
            if marks:
                lines = [l for l in text.splitlines() if any(m.lower() in l.lower() for m in marks)]
                print("[LOG MARKS] %s" % ", ".join(marks), flush=True)
                for l in lines[-8:]:
                    print("   " + l.strip(), flush=True)
        if not now_procs:
            print("[GAME EXITED]", flush=True)
            return
        el = time.time() - start
        if el - last_beat >= 15:
            last_beat = el
            print("[beat] t=%ds procs=%d crashes=%d" % (int(el), len(now_procs), len(known)), flush=True)
        time.sleep(1)
    print("[watch] timeout after %ds" % int(maxsec), flush=True)


if __name__ == "__main__":
    main()