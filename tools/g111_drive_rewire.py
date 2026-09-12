"""g111_drive_rewire.py - rewrite the game's hardcoded ``D:\\...`` path literals
to drive-relative ``..\\...`` so the game reads/writes directly inside the game
directory instead of needing a ``D:`` drive mapping (subst).

Why ``..`` : the game launches with working directory
``<GameDir>\\BASE`` (see g79), so ``..\\Saved`` => ``<GameDir>\\Saved`` and
``..\\system`` => ``<GameDir>\\system``.  ``D:`` (2 ascii / 4 utf16 bytes) is
replaced by ``..`` (equal byte count), so every path stays in place + NULL
padding is untouched.

Only non-executable sections are touched (path literals live in .rdata-like
segments); instruction bytes are never modified.
"""
from __future__ import annotations

import ctypes
import struct
import sys

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pids, module_base, open_game, read_mem, write_mem  # noqa: E402

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
PAGE_EXECUTE_READWRITE = 0x40

ASCII_D = b"\x44\x3a"        # "D:"
UTF16_D = b"\x44\x00\x3a\x00"  # "D:" utf16-le
ASCII_DOT = b"\x2e\x2e"      # ".."
UTF16_DOT = b"\x2e\x00\x2e\x00"


def sections_from_file(path):
    data = open(path, "rb").read()
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_off = e_lfanew + 24 + opt_size
    sections = []
    for i in range(nsec):
        p = sec_off + i * 40
        vsz = struct.unpack_from("<I", data, p + 8)[0]
        va = struct.unpack_from("<I", data, p + 12)[0]
        rawsz = struct.unpack_from("<I", data, p + 16)[0]
        rawptr = struct.unpack_from("<I", data, p + 20)[0]
        chars = struct.unpack_from("<I", data, p + 36)[0]
        sections.append(dict(rawptr=rawptr, rawsz=rawsz, va=va, vsz=vsz,
                             exec=bool(chars & 0x20000000), name=bytes(data[p:p + 8]).rstrip(b"\x00").decode("latin1")))
    return data, sections


def _sector_of(sections, foff):
    for s in sections:
        if s["rawptr"] <= foff < s["rawptr"] + s["rawsz"]:
            return s
    return None


def file_patch_sites(path):
    """Return list of dicts {rva, wide, section} for every D: literal that lies in a
    non-executable mapped section and looks like a path string (preceded by a string
    boundary or printable, followed by a backslash or printable path chars)."""
    data, sections = sections_from_file(path)
    sites = []
    for wide, needle in ((False, ASCII_D), (True, UTF16_D)):
        i = 0
        while True:
            j = data.find(needle, i)
            if j < 0:
                break
            # context check (path strings only): prev byte is printable or NUL;
            # next two bytes are backslash (drive-relative D:\\...) 
            prev = data[j - 1] if j > 0 else 0
            nxt = data[j + len(needle)] if j + len(needle) < len(data) else 0
            is_path = nxt in (0x5C, 0x00) and (prev in (0, 9, 10, 13) or 0x20 <= prev < 0x7F)
            s = _sector_of(sections, j)
            if is_path and s is not None and not s["exec"] and s["name"] != ".pdata":
                sites.append(dict(foff=j, rva=s["va"] + (j - s["rawptr"]),
                                  wide=wide, section=s["name"]))
            i = j + len(needle)
    return sites


def vprotect(h, addr, size):
    old = ctypes.c_uint32(0)
    base_page = addr & ~0xFFF
    ok = ctypes.windll.kernel32.VirtualProtectEx(
        h, ctypes.c_void_p(base_page), size, PAGE_EXECUTE_READWRITE, ctypes.byref(old))
    return bool(ok), old.value


def rewire_process(pid, sites=None):
    """Rewrite every D: path literal to .. in a live game process. Idempotent."""
    if sites is None:
        sites = file_patch_sites(GAME_EXE)
    base, _ = module_base(pid)
    if not base:
        return {"ok": False, "reason": "no-modbase"}
    h = open_game(pid)
    if not h:
        return {"ok": False, "reason": "open-failed"}
    done = skip = 0
    rewritten = 0
    for site in sites:
        va = base + site["rva"]
        old = UTF16_D if site["wide"] else ASCII_D
        new = UTF16_DOT if site["wide"] else ASCII_DOT
        cur = read_mem(h, va, len(old))
        if cur == new:
            skip += 1
            continue
        if cur != old:
            continue
        if not write_mem(h, va, new):
            okp, _op = vprotect(h, va, len(old))
            write_mem(h, va, new)
            vprotect(h, va, len(old), )
            rewritten += _verify(h, va, new, done)
        after = read_mem(h, va, len(new))
        if after == new:
            done += 1
            rewritten += 1
    ctypes.windll.kernel32.CloseHandle(h)
    return {"ok": True, "patched": done, "already": skip, "total": len(sites)}


def _verify(h, va, want, n):
    return 1 if read_mem(h, va, len(want)) == want else 0


if __name__ == "__main__":
    pids = find_pids()
    print("pids:", pids)
    if not pids:
        sys.exit("game not running")
    sites = file_patch_sites(GAME_EXE)
    print("patch sites in data sections:", len(sites))
    for s in sites[:8]:
        print("  rva=%#08x wide=%s %s" % (s["rva"], s["wide"], s["section"]))
    for pid in pids:
        print(pid, rewire_process(pid, sites))