"""inject_at_readcard.py - continuously poll the game's memory for the
ACPP_ReadCardMain object and set DebugNesicaSelectNo=0 once present, so the
game populates NESiCA_ID at the card screen.

No exe patching. Polls memory in a loop (fast, safe read-only scans + one small
write per match) until the card slot is set and NESiCA_ID shows in the log.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_mem_inject  # noqa: E402

LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\inject_at_readcard.txt"

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
GAME_ARGS = [
    "-UseConfigMatchingServer=1",
    "-DefaultMatchingServerAddress=127.0.0.1:6666",
    "-HttpServerAddress=127.0.0.1:4001",
    "-log",
]


def pid_of():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
        capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def find_readcard_objects(h):
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
                    c = card_mem_inject.candidate_ok(h, cur + i)
                    if c:
                        found.append(c)
            off += length
    seen = {}
    for c in found:
        seen.setdefault(c["addr"], c)
    return list(seen.values())


def main():
    report = []
    log = lambda msg: (report.append(msg), print(msg, flush=True))  # noqa: E731

    pid = pid_of()
    if pid is None:
        log("[LAUNCH] game not running - launching")
        subprocess.Popen([GAME_EXE] + GAME_ARGS)
        time.sleep(2.0)
        pid = pid_of()
    log("[LAUNCH] game pid=%s" % pid)
    if pid is None:
        log("[RESULT] NO_GAME")
        _save(report)
        return

    deadline = time.time() + 300
    last_log_pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    injected_addrs = set()
    while time.time() < deadline:
        pid = pid_of()
        if pid is None:
            log("[WAIT] game exited, waiting for restart...")
            time.sleep(5)
            continue
        try:
            h = card_mem_inject.open_game(pid)
        except SystemExit:
            time.sleep(2)
            continue
        try:
            cands = find_readcard_objects(h)
        finally:
            card_mem_inject.k32.CloseHandle(h)

        if cands:
            cands.sort(key=lambda c: (c["sel"] != -1, c["count"] if 0 < c["count"] else 10**9))
            for c in cands[:6]:
                if c["addr"] not in injected_addrs:
                    log("[SCAN] 0x%016X mode=%d prev=%d sel=%d count=%d" % (c["addr"], c["mode"], c["prevMode"], c["sel"], c["count"]))
            # pick the best: debug-slot -1 preferred, smallest table count
            best = cands[0]
            if best["addr"] not in injected_addrs:
                log("[SET] writing DebugNesicaSelectNo=0 at 0x%016X (was %d)" % (best["addr"], best["sel"]))
                try:
                    h = card_mem_inject.open_game(pid)
                    try:
                        card_mem_inject.write_u32(h, best["addr"] + 0x590, 0)
                        after = card_mem_inject.read_u32(h, best["addr"] + 0x590)
                        log("[SET] verified= %d" % after)
                    finally:
                        card_mem_inject.k32.CloseHandle(h)
                except OSError as e:
                    log("[SET] write error: %s" % e)
                injected_addrs.add(best["addr"])

        # check log for NESiCA_ID population
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
        time.sleep(1.0)

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
