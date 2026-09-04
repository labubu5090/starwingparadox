"""Analyze the bNesysServerLive gate check in AcrGame-Win64-Shipping.exe.

READ-ONLY. Locates the conditional branch, dumps disassembly, proposes a
minimal reversible patch, and writes patch_plan.json for apply_patch.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys

# ──────────────────────────────────────────────────────────────
# CONFIG — edit these if the game updates
# ──────────────────────────────────────────────────────────────

# Default path to the game exe
DEFAULT_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"

# RVA of sub_142C71500 (the function that checks *(byte*)(NESYS_state+1600)==1)
# If you have a different RVA, set it here.
TARGET_RVA = 0x142C71500

# Byte signature to search for as fallback (the test+branch pattern).
# x86-64: test byte [rcx+640h], 1 / jz <skip>  or similar.
# This is a heuristic — adjust if the compiler emits different code.
SIGNATURE = b"\xf6\x81\x40\x06\x00\x00\x01"  # test byte [rcx+640h], 1

# How many bytes around the match to dump
CONTEXT_BYTES = 32

# ──────────────────────────────────────────────────────────────


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_pe(data: bytes) -> tuple[int, int]:
    """Return (image_base, section_list) from PE headers.
    section_list = [(name, vrt_addr, raw_addr, raw_size), ...]
    """
    if data[:2] != b"MZ":
        raise ValueError("Not a PE file")
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off:pe_off + 4] != b"PE\x00\x00":
        raise ValueError("Invalid PE signature")
    opt_off = pe_off + 24
    magic = struct.unpack_from("<H", data, opt_off)[0]
    if magic == 0x20B:  # PE32+
        image_base = struct.unpack_from("<Q", data, opt_off + 24)[0]
        num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
        opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    elif magic == 0x10B:  # PE32
        image_base = struct.unpack_from("<I", data, opt_off + 28)[0]
        num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
        opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    else:
        raise ValueError(f"Unknown PE magic: 0x{magic:X}")

    sec_off = opt_off + opt_size
    sections = []
    for i in range(num_sections):
        s = sec_off + i * 40
        name = data[s:s + 8].rstrip(b"\x00").decode("ascii", errors="replace")
        vrt = struct.unpack_from("<I", data, s + 12)[0]
        raw_addr = struct.unpack_from("<I", data, s + 20)[0]
        raw_size = struct.unpack_from("<I", data, s + 16)[0]
        sections.append((name, vrt, raw_addr, raw_size))
    return image_base, sections


def rva_to_offset(rva: int, sections: list[tuple]) -> int | None:
    for name, vrt, raw, raw_size in sections:
        if vrt <= rva < vrt + raw_size:
            return RVA - vrt + raw
    return None


def search_signature(data: bytes, sig: bytes) -> int | None:
    idx = data.find(sig)
    return idx if idx >= 0 else None


def try_disasm(data: bytes, offset: int) -> str:
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_64
        md = Cs(CS_ARCH_X86, CS_MODE_64)
        code = data[offset:offset + 64]
        lines = []
        for insn in md.disasm(code, offset):
            lines.append(f"  0x{insn.address:X}:  {insn.mnemonic:8s} {insn.op_str}")
            if len(lines) >= 16:
                break
        return "\n".join(lines)
    except ImportError:
        return "  (install capstone for disassembly: pip install capstone)"
    except Exception as e:
        return f"  (disassembly error: {e})"


def find_conditional_jump(data: bytes, offset: int) -> tuple[int, bytes, bytes] | None:
    """Scan backwards and forwards from offset to find a conditional jump (0F 8x or 7x)
    that likely gates the online path. Returns (jump_offset, original_bytes, patched_bytes).
    """
    # Look in a window around the test instruction
    window = data[offset - 16:offset + 48]
    base = offset - 16

    for i in range(len(window) - 1):
        pos = base + i
        b = window[i]
        b1 = window[i + 1] if i + 1 < len(window) else 0

        # jz/jnz near (0F 84/0F 85) — 6 bytes
        if b == 0x0F and b1 in (0x84, 0x85):
            jump_len = 6
            orig = data[pos:pos + jump_len]
            # Patch: replace 0F 8x rel32 with 90 90 EB xx (nop+nop+jmp short)
            # or simpler: flip 0F 84 -> 0F 85 (jz->jnz) or vice versa
            patched = bytearray(orig)
            patched[1] = 0x85 if b1 == 0x84 else 0x84  # flip condition
            return pos, bytes(orig), bytes(patched)

        # jz/jnz short (74/75) — 2 bytes
        if b in (0x74, 0x75):
            jump_len = 2
            orig = data[pos:pos + jump_len]
            patched = bytearray(orig)
            patched[0] = 0x75 if b == 0x74 else 0x74  # flip condition
            return pos, bytes(orig), bytes(patched)

    return None


def main() -> None:
    exe_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EXE
    plan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch_plan.json")

    if not os.path.isfile(exe_path):
        print(f"[ERROR] Exe not found: {exe_path}")
        sys.exit(1)

    print("=" * 60)
    print("  NESYS Gate Analysis (READ-ONLY)")
    print("=" * 60)
    print()

    # SHA256
    exe_hash = sha256_of(exe_path)
    print(f"  Exe: {exe_path}")
    print(f"  SHA256: {exe_hash}")
    exe_size = os.path.getsize(exe_path)
    print(f"  Size: {exe_size:,} bytes")
    print()

    # Load exe
    with open(exe_path, "rb") as f:
        data = f.read()

    # PE parse
    try:
        image_base, sections = parse_pe(data)
        print(f"  Image base: 0x{image_base:X}")
        print("  Sections:")
        for name, vrt, raw, raw_size in sections:
            print(f"    {name:8s}  RVA=0x{vrt:08X}  Raw=0x{raw:08X}  Size=0x{raw_size:X}")
        print()
    except Exception as e:
        print(f"  [WARN] PE parse failed: {e}")
        image_base = 0
        sections = []

    # Locate target
    file_offset = None
    method = None

    # Try RVA conversion first
    if sections:
        file_offset = rva_to_offset(TARGET_RVA, sections)
        if file_offset is not None:
            method = f"RVA 0x{TARGET_RVA:X}"

    # Fallback: byte signature search
    if file_offset is None:
        sig_offset = search_signature(data, SIGNATURE)
        if sig_offset is not None:
            file_offset = sig_offset
            method = f"byte signature at 0x{sig_offset:X}"

    if file_offset is None:
        print("[ERROR] Could not locate gate check region.")
        print("  Edit TARGET_RVA or SIGNATURE in this file and re-run.")
        sys.exit(1)

    print(f"  Gate check located via: {method}")
    print(f"  File offset: 0x{file_offset:X}")
    print()

    # Dump context
    start = max(0, file_offset - CONTEXT_BYTES)
    end = min(len(data), file_offset + CONTEXT_BYTES)
    dump = data[start:end]
    print("  Context hex dump:")
    for i in range(0, len(dump), 16):
        addr = start + i
        chunk = dump[i:i + 16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        marker = " <---" if start + i <= file_offset < start + i + 16 else ""
        print(f"    0x{addr:08X}:  {hex_str:<48s}  {ascii_str}{marker}")
    print()

    # Disassembly
    print("  Disassembly around gate check:")
    print(try_disasm(data, file_offset))
    print()

    # Find conditional jump and propose patch
    result = find_conditional_jump(data, file_offset)
    if result:
        jmp_off, orig_bytes, patched_bytes = result
        print(f"  Conditional jump found at: 0x{jmp_off:X}")
        print(f"    Original:    {orig_bytes.hex(' ')}")
        print(f"    Patched:     {patched_bytes.hex(' ')}")
        print(f"    Change:      flip jz<->jnz (condition inversion)")
        print()

        plan = {
            "exe_sha256": exe_hash,
            "file_offset": jmp_off,
            "original_bytes": orig_bytes.hex(),
            "patched_bytes": patched_bytes.hex(),
            "note": (
                "Flip conditional jump (jz<->jnz) at the bNesysServerLive check. "
                "This makes the gate always take the 'online' path. "
                "Revert by flipping back or deleting the PATCHED copy."
            ),
        }
        with open(plan_path, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"  Patch plan written to: {plan_path}")
    else:
        print("  [WARN] Could not auto-locate conditional jump.")
        print("  Manually inspect the hex dump above and edit find_conditional_jump().")

    print()
    print("  NOTHING WAS MODIFIED. This is analysis only.")


if __name__ == "__main__":
    main()
