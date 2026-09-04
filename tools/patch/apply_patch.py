"""Apply the gate patch SAFELY to a COPY of the game exe.

Supports multi-site patches. The original is NEVER modified.
SHA256 is verified before patching. Backups are saved for manual revert.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(SCRIPT_DIR, "patch_plan.json")
BACKUP_DIR = os.path.join(SCRIPT_DIR, "backups")

DEFAULT_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    exe_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EXE

    if not os.path.isfile(PLAN_PATH):
        print(f"[ERROR] Patch plan not found: {PLAN_PATH}")
        sys.exit(1)

    with open(PLAN_PATH, encoding="utf-8") as f:
        plan = json.load(f)

    if not os.path.isfile(exe_path):
        print(f"[ERROR] Exe not found: {exe_path}")
        sys.exit(1)

    print("=" * 60)
    print("  NESYS Gate Patch (safe, copy-only)")
    print("=" * 60)
    print()

    exe_hash = sha256_of(exe_path)
    print(f"  Target:        {exe_path}")
    print(f"  Exe SHA256:    {exe_hash}")
    print(f"  Plan SHA256:   {plan['exe_sha256']}")

    if exe_hash != plan["exe_sha256"]:
        print()
        print("[ABORT] SHA256 MISMATCH — game exe updated since plan was created.")
        print("  Re-run analyze_gate.py")
        sys.exit(1)

    print("  SHA256: MATCH")
    print()

    # Normalize patches — support both single and multi-patch format
    patches = plan.get("patches", [])
    if not patches and "file_offset" in plan:
        patches = [plan]

    print(f"  Patch sites: {len(patches)}")
    print()

    # Output path
    exe_dir = os.path.dirname(exe_path)
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    patched_path = os.path.join(exe_dir, f"{exe_name}.PATCHED.exe")

    if os.path.isfile(patched_path):
        print(f"  [INFO] Overwriting existing patched copy")
        os.remove(patched_path)

    print("  Copying exe...")
    shutil.copy2(exe_path, patched_path)
    print(f"  Copy created: {patched_path}")
    print()

    # Save backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Apply each patch
    all_ok = True
    with open(patched_path, "r+b") as f:
        for i, patch in enumerate(patches):
            off = patch["file_offset"]
            orig = bytes.fromhex(patch["original_bytes"])
            new = bytes.fromhex(patch["patched_bytes"])
            note = patch.get("note", "")

            f.seek(off)
            current = f.read(len(orig))

            if current != orig:
                print(f"  [FAIL] Patch #{i+1} at 0x{off:X}")
                print(f"    Expected: {orig.hex(' ')}")
                print(f"    Found:    {current.hex(' ')}")
                all_ok = False
                continue

            # Save backup for this site
            backup_file = os.path.join(BACKUP_DIR, f"patch_{i+1}_0x{off:X}.bin")
            with open(backup_file, "wb") as bf:
                backup_data = {
                    "file_offset": off,
                    "original_bytes": patch["original_bytes"],
                    "exe_sha256": exe_hash,
                    "note": note,
                }
                bf.write(json.dumps(backup_data, indent=2).encode())

            f.seek(off)
            f.write(new)
            print(f"  [OK] Patch #{i+1}: 0x{off:X}")
            print(f"    {current.hex(' ')} -> {new.hex(' ')}")
            if note:
                print(f"    {note}")

    print()

    if not all_ok:
        print("[ABORT] Some patches failed. Removing broken copy.")
        os.remove(patched_path)
        sys.exit(1)

    print("=" * 60)
    print(f"  PATCHED EXE: {patched_path}")
    print(f"  Backups:     {BACKUP_DIR}")
    print()
    print("  Launch: AcrGame-Win64-Shipping.PATCHED.exe")
    print("  Revert: python tools/patch/revert_patch.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
