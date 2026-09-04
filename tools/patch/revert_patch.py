"""Revert the gate patch.

Deletes AcrGame-Win64-Shipping.PATCHED.exe (the original was never touched).
Optionally restores original bytes from backup via --restore-bytes.
"""
from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(SCRIPT_DIR, "backups")

DEFAULT_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"


def sha256_of(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    exe_path = DEFAULT_EXE
    restore_mode = False

    for arg in sys.argv[1:]:
        if arg == "--restore-bytes":
            restore_mode = True
        elif os.path.isfile(arg):
            exe_path = arg

    print("=" * 60)
    print("  NESYS Gate Patch — Revert")
    print("=" * 60)
    print()

    # Delete patched copy
    exe_dir = os.path.dirname(exe_path)
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    patched_path = os.path.join(exe_dir, f"{exe_name}.PATCHED.exe")

    if os.path.isfile(patched_path):
        os.remove(patched_path)
        print(f"  Deleted: {patched_path}")
    else:
        print(f"  No patched copy found")

    # Optional: restore bytes from backups
    if restore_mode:
        if not os.path.isdir(BACKUP_DIR):
            print(f"  No backup directory found: {BACKUP_DIR}")
            print("  Original exe was never modified — nothing to restore.")
            print()
            return

        if not os.path.isfile(exe_path):
            print(f"  [ERROR] Target exe not found: {exe_path}")
            sys.exit(1)

        exe_hash = sha256_of(exe_path)

        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".bin")],
        )

        if not backup_files:
            print("  No backup files found.")
            return

        with open(exe_path, "r+b") as f:
            for bf_name in backup_files:
                bf_path = os.path.join(BACKUP_DIR, bf_name)
                with open(bf_path, encoding="utf-8") as jf:
                    backup = json.load(jf)

                off = backup["file_offset"]
                orig = bytes.fromhex(backup["original_bytes"])
                expected_sha = backup.get("exe_sha256", "")

                if expected_sha and exe_hash != expected_sha:
                    print(f"  [SKIP] {bf_name} — SHA256 mismatch")
                    continue

                f.seek(off)
                current = f.read(len(orig))
                if current == orig:
                    print(f"  [OK] 0x{off:X} — already correct")
                else:
                    f.seek(off)
                    f.write(orig)
                    print(f"  [RESTORED] 0x{off:X}: {current.hex(' ')} -> {orig.hex(' ')}")

    print()
    print("  Original exe was never modified. Revert complete.")


if __name__ == "__main__":
    main()
