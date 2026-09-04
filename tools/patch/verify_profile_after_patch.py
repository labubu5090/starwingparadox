"""Post-patch profile flow verifier.

Reads logs/nesys_trace.log to check whether the patch actually results in
a card-tap / profile exchange on TCP 1042 or the named pipe.

READ-ONLY — does not touch the game, stubs, or any config.
"""
from __future__ import annotations

import os
import re
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TRACE_LOG = os.path.join(PROJECT_ROOT, "logs", "nesys_trace.log")

DEFAULT_WAIT = 60  # seconds to tail


def tail_lines(path: str, since_pos: int = 0) -> tuple[str, int]:
    """Read new bytes from path starting at since_pos. Returns (new_data, new_pos)."""
    try:
        size = os.path.getsize(path)
        if size <= since_pos:
            return "", since_pos
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(since_pos)
            data = f.read()
            return data, f.tell()
    except FileNotFoundError:
        return "", since_pos


def has_card_id(data: str) -> str | None:
    m = re.search(r"card_id[=:]\s*(\d{10,20})", data)
    if m:
        return m.group(1)
    runs = re.findall(r"\b\d{16,20}\b", data)
    if runs:
        return runs[0]
    return None


def main() -> None:
    wait_sec = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WAIT

    print("=" * 60)
    print("  Profile Flow Verifier (post-patch)")
    print("=" * 60)
    print()
    print(f"  Tailing: {TRACE_LOG}")
    print(f"  Duration: {wait_sec}s")
    print(f"  (Ctrl+C to stop early)")
    print()

    if not os.path.isfile(TRACE_LOG):
        print(f"  [WARN] Trace log not found: {TRACE_LOG}")
        print("  Launch the game and tap a card, then re-run this script.")

    saw_rx = False
    saw_tx = False
    saw_card_id = None
    start_pos = os.path.getsize(TRACE_LOG) if os.path.isfile(TRACE_LOG) else 0
    elapsed = 0

    try:
        while elapsed < wait_sec:
            new_data, start_pos = tail_lines(TRACE_LOG, start_pos)
            if new_data:
                lines = new_data.strip().splitlines()
                for line in lines:
                    if "[conn#" in line and ("TCP1042" in line or "PIPE" in line):
                        if "RX" in line:
                            saw_rx = True
                            print(f"  [OBSERVE] {line.strip()}")
                        elif "TX" in line:
                            saw_tx = True
                            print(f"  [OBSERVE] {line.strip()}")

                    # Check for card id in raw hex dumps (follows an RX line)
                    cid = has_card_id(line)
                    if cid and not saw_card_id:
                        saw_card_id = cid
                        print(f"  [OBSERVE] Card ID detected: {cid}")

            time.sleep(1)
            elapsed += 1

    except KeyboardInterrupt:
        pass

    print()
    print("=" * 60)
    print("  VERDICT")
    print("=" * 60)

    if saw_rx and saw_tx:
        print()
        print("  PROFILE FLOW ALIVE")
        print("  Card tap received on 1042/pipe, stub replied.")
        if saw_card_id:
            print(f"  Card ID: {saw_card_id}")
        print("  The patch is sufficient for local profile loading.")
    elif saw_rx and not saw_tx:
        print()
        print("  RX SEEN BUT NO TX REPLY")
        print("  Card tap arrived but our stub did not send a reply.")
        print("  Check stub logs for errors.")
    elif not saw_rx:
        print()
        print("  NO CARD TAP SEEN")
        print("  Possible reasons:")
        print("    1. Patch not applied (game still offline)")
        print("    2. User didn't tap a card")
        print("    3. Card tap UI still gated")
        print("  Launch the patched exe, confirm the globe icon is green,")
        print("  then tap a card and re-run this script.")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
