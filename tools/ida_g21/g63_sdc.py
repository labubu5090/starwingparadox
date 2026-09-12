"""G63e: locate SystemDataCheck strings via ida_search.find_binary (g47b-proven),
find referencing funcs, and decompile the SystemDataCheck Tick + CheckVersion logic."""
import json, traceback

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g63_sdc.txt"
lines = []

import ida_bytes, ida_funcs, ida_hexrays, ida_name, idc, idautils, ida_search

BADEND = 0xFFFFFFFFFFFFFFFF

def find_all(hexpat, limit=8):
    res = []
    ea = 0
    guard = 0
    while len(res) < limit and guard < 500:
        ea = ida_search.find_binary(ea, BADEND, hexpat, 16, ida_bytes.SEARCH_DOWN | ida_bytes.SEARCH_CASE)
        if ea == BADEND or ea is None or ea == 0xFFFFFFFFFFFFFFFF:
            break
        res.append(ea)
        ea += 1
        guard += 1
    return res

def hexa(s):
    if isinstance(s, bytes):
        return " ".join("%02X" % b for b in s)
    return " ".join("%02X" % ord(c) for c in s)

def xref_funcs(ea):
    out = {}
    for xr in idautils.XrefsTo(ea):
        f = ida_funcs.get_func(xr.frm)
        if f:
            out[f.start_ea] = ida_funcs.get_func_name(f.start_ea) or "?"
    return out

try:
    import idata  # noqa
except Exception:
    pass

for pat in [b"CPP_SystemDataCheck.cpp", b"ACPP_SystemDataCheck", b"CheckVersion",
            b"IsOnlineStatus", b"NesysEventRequest", b"GetCurrentEventFileArrayNum",
            b"CheckOpenKeyLoad", b"EventRequest", b"CheckPackage", b"CheckMasterData"]:
    addrs = find_all(hexa(pat), 6)
    lines.append("PATTERN %r -> %d hits: %s" % (pat, len(addrs), [hex(a) for a in addrs]))
    for ea in addrs:
        for fea, nm in xref_funcs(ea).items():
            lines.append("    <- func 0x%X (%s)" % (fea, nm))
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("WROTE %s" % OUT)
print("\n".join(lines[:150]))

try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
