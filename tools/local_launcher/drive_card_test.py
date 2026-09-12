"""drive_card_test.py - drive the game to the card screen, inject DebugNesicaSelectNo=0,
and verify whether NESiCA_ID gets populated.

No exe patching. Uses:
  - controller_mapper.keyboard_output.KeyboardOutput to send Start(Enter)/credit(Z)
  - card_mem_inject to set DebugNesicaSelectNo on the ACPP_ReadCardMain instance
"""
from __future__ import annotations

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "controller_mapper"))

from keyboard_output import KeyboardOutput  # noqa: E402
import card_mem_inject  # noqa: E402

LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\drive_card_test.txt"


def tail(n=400):
    with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return lines[-n:]


def grep_last(pattern, lines, count=15):
    hits = [ln for ln in lines if re.search(pattern, ln)]
    return hits[-count:] if hits else []


def pid_of():
    import subprocess
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process | Where-Object {$_.Name -like 'AcrGame*'} | Select-Object -First 1 -ExpandProperty Id)"],
        capture_output=True, text=True, timeout=30)
    s = out.stdout.strip()
    return int(s) if s.isdigit() else None


def main():
    kb = KeyboardOutput()
    report = []
    log = lambda msg: (report.append(msg), print(msg, flush=True))  # noqa: E731

    log("PID target: %s" % pid_of())

    marker = time.time()
    lines_before = tail()

    # --- Phase 1: press Start(Enter) to advance toward the card screen ---
    log("[PHASE1] Sending Start(Enter) taps to advance to ReadCard...")
    for _ in range(10):
        kb.tap("Enter", 0.08)
        time.sleep(0.3)
    # also tap credit just in case
    kb.tap("Z", 0.08)
    time.sleep(1.0)
    log("[PHASE1] done taps")

    # --- Phase 2: wait for card screen / ReadCard in log ---
    seen_card = False
    for i in range(60):
        t = tail()
        if any("SL_ReadCard" in ln for ln in t) or any("ReadCardExec" in ln for ln in t):
            log("[PHASE2] Card screen detected at iter %d" % i)
            seen_card = True
            break
        if i % 5 == 0:
            log("[PHASE2] waiting... iter %d" % i)
        time.sleep(1.0)

    if not seen_card:
        log("[RESULT] NOT_REACHED_CARD")
        _save(report, lines_before)
        return

    # --- Phase 3: inject DebugNesicaSelectNo=0 ---
    pid = pid_of()
    log("[PHASE3] Injecting DebugNesicaSelectNo=0 into PID %s ..." % pid)
    try:
        card_mem_inject.set_slot(pid, 0, None)
        log("[PHASE3] injection call returned")
    except SystemExit as e:
        log("[PHASE3] injector exited: %s" % e)
    except Exception as e:
        log("[PHASE3] injector error: %s" % e)

    # --- Phase 4: press Enter repeatedly to trigger EnterPressed validation ---
    log("[PHASE4] Pressing Enter to validate debug card...")
    for _ in range(20):
        kb.tap("Enter", 0.08)
        time.sleep(0.35)

    # --- Phase 5: check result ---
    time.sleep(2.0)
    t = tail(600)
    id_lines = grep_last("NESiCA_ID", t)
    mode_lines = grep_last("readCardMode", t)
    for ln in id_lines[-8:]:
        log("LAST_ENTER: %s" % ln.strip())
    accepted = any("NESiCA_ID" in ln and "</" not in ln and "[]" not in ln for ln in id_lines)
    log("[RESULT] %s" % ("CARD_ID_POPULATED" if accepted else "NO_CARD_ID"))
    _save(report, lines_before)


def _save(report, lines_before):
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n\n===== NEW LOG LINES =====\n")
        t = tail()
        for ln in t:
            f.write(ln)
    print("WROTE %s" % OUT)


if __name__ == "__main__":
    main()
