"""open_game_once.py - launch the game once, apply ALL patches once, then exit.

Opposite of the keepalive: no watch loop, no crash-relaunch. Game is launched,
memory patches + drive-rewire + card mount are applied a single time, the result
is printed, and this process terminates. Close the game whenever you like.

Usage: python open_game_once.py
"""
from __future__ import annotations

import time

import sys

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
import g79_allfix_keepalive as K  # noqa: E402
from nesys_online_inject import find_pids, module_base, open_game  # noqa: E402
import ctypes  # noqa: E402

STARTUP_DEADLINE_S = 60


def main():
    pids = find_pids()
    if not pids:
        print("[open-game] no game running - launching...")
        K.launch_game()
        deadline = time.time() + STARTUP_DEADLINE_S
        while not pids and time.time() < deadline:
            time.sleep(2)
            pids = find_pids()
        if not pids:
            print("[open-game] ERROR: game never appeared within %ds" % STARTUP_DEADLINE_S)
            sys.exit(1)
    else:
        print("[open-game] game already running (pid %s) - patching it" % pids)

    pid = pids[0]
    base, _size = module_base(pid)
    if not base:
        print("[open-game] ERROR: no module base for pid %d" % pid)
        sys.exit(1)

    h = open_game(pid)
    if not h:
        print("[open-game] ERROR: open_process failed")
        sys.exit(1)

    res = K.apply_all(h, base)
    ctypes.windll.kernel32.CloseHandle(h)

    failed = [n for n, r in res.items() if not r.get("ok")]
    rewire = K.g111_drive_rewire.rewire_process(pid)
    if not rewire.get("ok") or rewire.get("patched", 0) + rewire.get("already", 0) < 1:
        failed.append("drive-rewire")

    changed = [n for n, r in res.items() if r.get("applied") and r.get("reason") != "already"]
    print("[open-game] pid %d base=%#x" % (pid, base))
    print("[open-game] applied fresh: %s" % (", ".join(sorted(changed)) or "(none - all already)"))
    if failed:
        print("[open-game] FAILED: %s" % ", ".join(failed))
        sys.exit(2)
    print("[open-game] OK - game is patched. This script exits now; close the game when done.")


if __name__ == "__main__":
    main()