"""G61: locate + decompile ACPP_SystemDataCheck functions from CPP_SystemDataCheck.cpp
and the IsOnlineStatus / NESYS event check logic."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g61_sdc.txt"

import idautils, idc, ida_funcs, ida_hexrays, ida_bytes, ida_name

lines = []
target_funcs = {}

def note(s):
    lines.append(s)

# 1. find the source-file string
src_ea = None
for s_ea in idautils.Strings():
    try:
        v = idc.get_strlit_contents(s_ea)
    except Exception:
        v = None
    if not v:
        continue
    try:
        t = v.decode("utf-16-le", errors="ignore")
    except Exception:
        t = v.decode("utf-8", errors="ignore")
    if "CPP_SystemDataCheck.cpp" in t:
        src_ea = s_ea
        note("SOURCE STRING 0x%X : %s" % (s_ea, t))
        for xref in idautils.XrefsTo(s_ea):
            f = ida_funcs.get_func(xref.frm)
            if f:
                note("   xref 0x%X in func 0x%X (%s)" % (xref.frm, f.start_ea, ida_funcs.get_func_name(f.start_ea) or "?"))
        break

# 2. find IsOnlineStatus / CheckVersion / EventRequest related strings & their reading funcs
for needle in ["IsOnlineStatus", "CheckVersion", "CheckOpenKey", "NesysEventRequest", "EventRequest",
               "IsEventCheck", "EventError", "GetCurrentEventFileArrayNum", "SystemDataCheck"]:
    for s_ea in idautils.Strings():
        try:
            v = idc.get_strlit_contents(s_ea)
        except Exception:
            continue
        if not v:
            continue
        try:
            t = v.decode("utf-16-le", errors="ignore")
        except Exception:
            t = v.decode("utf-8", errors="ignore")
        if needle in t:
            note("  STR[%s] 0x%X : %r" % (needle, s_ea, t[:60]))
            for xref in list(idautils.XrefsTo(s_ea))[:4]:
                f = ida_funcs.get_func(xref.frm)
                if f:
                    note("     <- func 0x%X (%s)" % (f.start_ea, ida_funcs.get_func_name(f.start_ea) or "?"))
            break

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("WROTE %s (%d lines)" % (OUT, len(lines)))

# 3. decompile any functions that reference CodeVersion/IsOnline via known string refs
# find function containing the "CheckVersion" string read
def func_containing_string(needle):
    for s_ea in idautils.Strings():
        try:
            v = idc.get_strlit_contents(s_ea)
        except Exception:
            continue
        if not v:
            continue
        try:
            t = v.decode("utf-16-le", errors="ignore")
        except Exception:
            t = v.decode("utf-8", errors="ignore")
        if needle in t:
            for xref in list(idautils.XrefsTo(s_ea)):
                f = ida_funcs.get_func(xref.frm)
                if f:
                    return f.start_ea
    return None

res = []
for needle in ["CheckVersion", "CheckOpenKeyLoad"]:
    ea = func_containing_string(needle)
    if ea:
        note_fn = "### %s -> func 0x%X (%s)" % (needle, ea, ida_funcs.get_func_name(ea) or "?")
        res.append(note_fn + "\n")
        try:
            c = ida_hexrays.decompile(ea)
            res.append(str(c) if c else "no decomp")
        except Exception as e:
            res.append("FAIL %s" % e)
        res.append("\n\n")

with open(OUT.replace("g61", "g61b"), "w", encoding="utf-8") as f:
    f.write("\n".join(res))
print("WROTE %s" % OUT.replace("g61", "g61b"))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
