"""Standalone NESYS named-pipe server — runs independently of the GUI launcher.

Follows the reference FakeNesicaService protocol. Creates the \\\\.\\pipe\\nesys_games
named pipe with a permissive security descriptor so the (possibly unprivileged)
game process can connect and complete the LCOMMAND/SCOMMAND handshake.

Usage:
    python -m tools.pipe_server
"""
from __future__ import annotations

import os
import sys
import time

_tools_dir = os.path.dirname(os.path.abspath(__file__))
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from local_launcher.nesys_pipe import (
    NesysPipeServer,
    profile_id_to_nesys_id,
)


def main() -> int:
    server = NesysPipeServer()

    # Default card id; can be overridden for testing
    if len(sys.argv) > 1:
        try:
            server.card_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid card id: {sys.argv[1]}")
            return 1

    def on_log(msg: str) -> None:
        print(f"[NESYS-PIPE] {msg}")

    server.set_log_callback(on_log)
    server.start()

    print("=" * 60)
    print("  FakeNesicaService-compatible pipe server")
    print("  Pipe: \\\\.\\pipe\\nesys_games")
    print(f"  Card ID: {server.card_id}")
    print()
    print("  Waiting for game connection...")
    print("  (Ctrl+C to stop)")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
