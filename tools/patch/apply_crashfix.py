"""Apply the WeaponManager crash fix to a COPY of the game exe.

Fixes EXCEPTION_ACCESS_VIOLATION @ 0x34 in ACPP_WeaponManager::InitalizeWeapon
when GetSubWeaponDataInstancePtr returns nullptr (AR skill index -1).

The original exe is NEVER modified. SHA256 is verified and backups are kept.
Optionally also produces a COMBINED exe = your existing gate plan + crash fix.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CRASHFIX_PLAN = os.path.join(SCRIPT_DIR, "crashfix_patch_plan.json")
GATE_PLAN = os.path.join(SCRIPT_DIR, "patch_plan.json")
BACKUP_DIR = os.path.join(SCRIPT_DIR, "backups_crashfix")

DEFAULT_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_plan(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_patches(exe_path: str, plan: dict, out_path: str) -> None:
    print(f"  Target:        {exe_path}")
    exe_hash = sha256_of(exe_path)
    print(f"  Exe SHA256:    {exe_hash}")
    print(f"  Plan SHA256:   {plan['exe_sha256']}")
    if exe_hash != plan["exe_sha256"]:
        print("[ABORT] SHA256 MISMATCH - game exe updated since plan was created.")
        sys.exit(1)
    print("  SHA256: MATCH")

    patches = plan.get("patches", [])
    print(f"  Patch sites:   {len(patches)}")

    if os.path.isfile(out_path):
        os.remove(out_path)
    shutil.copy2(exe_path, out_path)
    print(f"  Copy created:  {out_path}")

    os.makedirs(BACKUP_DIR, exist_ok=True)
    all_ok = True
    with open(out_path, "r+b") as f:
        for i, patch in enumerate(patches):
            off = int(patch["file_offset"], 0) if isinstance(patch["file_offset"], str) else int(patch["file_offset"])
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

            backup_file = os.path.join(BACKUP_DIR, f"patch_{i+1}_0x{off:X}.bin")
            with open(backup_file, "wb") as bf:
                bf.write(json.dumps({
                    "file_offset": hex(off),
                    "original_bytes": patch["original_bytes"],
                    "exe_sha256": exe_hash,
                    "note": note,
                }, indent=2).encode())

            f.seek(off)
            f.write(new)
            print(f"  [OK] Patch #{i+1}: 0x{off:X}")
            print(f"    {current.hex(' ')} -> {new.hex(' ')}")
            if note:
                print(f"    {note}")

    if not all_ok:
        print("[ABORT] Some patches failed. Removing broken copy.")
        os.remove(out_path)
        sys.exit(1)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    exe_path = args[0] if args else DEFAULT_EXE
    combined = "--combined" in sys.argv

    if not os.path.isfile(exe_path):
        print(f"[ERROR] Exe not found: {exe_path}")
        sys.exit(1)

    print("=" * 60)
    print("  WeaponManager crash-fix patch (safe, copy-only)")
    print("=" * 60)
    print()

    exe_dir = os.path.dirname(exe_path)
    make_combined = False

    if combined:
        plan = load_plan(GATE_PLAN)
        combined_sites = [p for p in plan["patches"]] + [p for p in load_plan(CRASHFIX_PLAN)["patches"]]
        out = os.path.join(exe_dir, "AcrGame-Win64-Shipping-PATCHED-COMBINED.exe")
        print("  Mode:          COMBINED (gate patches + crash fix)")
        apply_patches(exe_path, {
            "exe_sha256": plan["exe_sha256"],
            "patches": combined_sites,
        }, out)
    else:
        plan = load_plan(CRASHFIX_PLAN)
        alt_plan = os.path.join(SCRIPT_DIR, "crashfix_patch_plan_patched.json")
        if os.path.isfile(alt_plan) and sha256_of(exe_path) == load_plan(alt_plan)["exe_sha256"]:
            plan = load_plan(alt_plan)
            out = os.path.join(exe_dir, "AcrGame-Win64-Shipping-Patched-CRASHFIX.exe")
            print("  Mode:          CRASH FIX on legacy -Patched.exe")
        else:
            out = os.path.join(exe_dir, "AcrGame-Win64-Shipping-PATCHED-CRASHFIX.exe")
            print("  Mode:          CRASH FIX only")
        apply_patches(exe_path, plan, out)

    print()
    print("=" * 60)
    print(f"  PATCHED EXE: {out}")
    print(f"  Backups:     {BACKUP_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()