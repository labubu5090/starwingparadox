"""find_code_cave.py - find >=24-byte runs of 0xCC/0x00 padding in .text for a
runtime trampoline cave (2v2 InitalizeWeapon null-guard patch).

Pure PE parse from the pristine X: exe; NO IDA required. Also verifies the
file-offset <-> RVA mapping by locating known instructions.
"""
import json
import struct
import sys

EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
IMG_BASE = 0x140000000
MIN_RUN = 24

RVA_TICK = 0x2BDF7C4
KNOWN = [
    # (label, rva, hex) - verified against the idb / earlier patch specs
    ("CA80_entry",   0x0243CA80, "48895c2408"),
    ("tick-nop_old", RVA_TICK,   "e867320000"),
    ("wm-cf13",      0x0243CF13, "7460"),
    ("crash_mov",    0x024358A2, "488b8188030000"),
]


def rva_to_off(sections, rva):
    for _name, va, vsize, _raw_size, raw_off in sections:
        if va <= rva < va + vsize:
            return raw_off + (rva - va)
    return None


def main():
    with open(EXE, "rb") as fh:
        data = fh.read()

    if data[:2] != b"MZ":
        print("FATAL: not a PE")
        return 1
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[e_lfanew:e_lfanew + 4] == b"PE\x00\x00"

    nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    secoff = e_lfanew + 24 + opt_size

    sections = []
    for i in range(nsec):
        off = secoff + i * 40
        name = data[off:off + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsize = struct.unpack_from("<I", data, off + 8)[0]
        va = struct.unpack_from("<I", data, off + 12)[0]
        rsize = struct.unpack_from("<I", data, off + 16)[0]
        roff = struct.unpack_from("<I", data, off + 20)[0]
        sections.append((name, va, vsize, rsize, roff))

    print("sections:")
    for name, va, vsize, rsize, roff in sections:
        print("  %-8s rva=0x%08x vsize=0x%08x raw=0x%08x+0x%08x"
              % (name, va, vsize, roff, rsize))

    text = next((s for s in sections if s[0] == ".text"), None)
    if not text:
        print("FATAL: no .text")
        return 1
    _, tva, tvsize, trsize, troff = text
    text_raw = data[troff:troff + trsize]

    # verify mapping
    print("\nmapping check:")
    ok = True
    for label, ea, hexpat in KNOWN:
        rva = ea  # KNOWN entries are already RVA
        off = rva_to_off(sections, rva)
        if off is None:
            print("  %-14s rva=0x%08x  NO SECTION" % (label, rva))
            ok = False
            continue
        got = data[off:off + len(hexpat) // 2].hex()
        match = got == hexpat
        ok &= match
        print("  %-14s rva=0x%08x off=0x%08x got=%s %s"
              % (label, rva, off, got, "OK" if match else "MISMATCH"))
    if not ok:
        print("FATAL: mapping mismatch")
        return 1

    # scan .text raw for runs
    runs = []
    i = 0
    n = len(text_raw)
    while i < n:
        b = text_raw[i]
        if b == 0xCC or b == 0x00:
            j = i
            while j < n and text_raw[j] == b:
                j += 1
            length = j - i
            if length >= MIN_RUN:
                runs.append((tva + i, length, "cc" if b == 0xCC else "00"))
            i = j
        else:
            i += 1

    runs.sort(key=lambda r: -r[1])
    out = {
        "exe": EXE,
        "text_rva": tva,
        "min_run": MIN_RUN,
        "runs": [(hex(rva), length, kind) for rva, length, kind in runs],
    }
    outpath = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\code_cave_candidates.json"
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    print("\ntop cave candidates (.text, >=%d bytes %s runs):"
          % (MIN_RUN, "encoded as hex"))
    for rva, length, kind in runs[:30]:
        print("  rva=0x%08x  ea=0x%x  len=%d  (%s)" % (rva, IMG_BASE + rva, length, kind))
    print("total runs: %d  -> %s" % (len(runs), outpath))
    return 0


if __name__ == "__main__":
    sys.exit(main())