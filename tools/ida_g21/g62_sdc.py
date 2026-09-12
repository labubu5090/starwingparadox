"""G62: locate + decompile ACPP_SystemDataCheck functions and their CheckVersion/Event logic.
Fixes decode: try utf-8 first for source-path strings."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g62_sdc.txt"

import idautils, idc, ida_funcs, ida_hexrays, ida_bytes, ida_name

lines = []

def get_strs(s_ea):
    try:
        v = idc.get_strlit_contents(s_ea)
    except Exception:
        return ""
    if not v:
        return ""
    for enc in ("utf-8", "utf-16-le"):
        try:
            return v.decode(enc, errors="ignore")
        except Exception:
            continue
    return ""

def find_string(needle):
    for s_ea in idautils.Strings():
        t = get_strs(s_ea)
        if needle in t:
            return s_ea, t
    return None, None

def funcs_using(needle):
    """Return set of func addresses whose strings include needle."""
    found = set()
    for s_ea in idautils.Strings():
        t = get_strs(s_ea)
        if needle in t:
            for xref in idautils.XrefsTo(s_ea):
                f = ida_funcs.get_func(xref.frm)
                if f:
                    found.add(f.start_ea)
    return found

# 1) functions referencing SystemDataCheck source path
sdc_funcs = funcs_using("SystemDataCheck.cpp")
lines.append("FUNCS referencing SystemDataCheck.cpp: %d" % len(sdc_funcs))
for ea in sorted(sdc_funcs):
    lines.append("  0x%X (%s) size=0x%X" % (ea, ida_funcs.get_func_name(ea) or "?", ida_funcs.get_func(ea).size() if ida_funcs.get_func(ea) else 0))

# 2) CheckVersion / IsOnlineStatus reading functions
for needle in ["CheckVersion", "IsOnlineStatus", "CheckOpenKey", "NesysEventRequest", "GetCurrentEventFileArrayNum", "EventRequest"]:
    fs = funcs_using(needle)
    lines.append("\nFUNCS referencing '%s': %d" % (needle, len(fs)))
    for ea in sorted(fs):
        lines.append("  0x%X (%s)" % (ea, ida_funcs.get_func_name(ea) or "?"))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("WROTE %s (%d lines)" % (OUT, len(lines)))
print("\n".join(lines[:80]))
print("sdc_funcs=%s" % [hex(e) for e in sorted(sdc_funcs)])

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
