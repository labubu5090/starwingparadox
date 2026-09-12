"""G59: find the 'PremissionOfflineNesys' gate - locate the string, its xrefs,
and the enclosing decision that routes EnterPressed to it."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g59_premission.txt"

import ida_bytes, ida_funcs, ida_name, idautils, idc, ida_hexrays

lines = []

def find_string(s):
    out = []
    for s_ea in idautils.Strings():
        try:
            val = idc.get_strlit_contents(s_ea)
        except Exception:
            val = None
        if not val:
            continue
        try:
            txt = val.decode("utf-16-le", errors="ignore")
        except Exception:
            txt = val.decode("utf-8", errors="ignore")
        if s in txt:
            out.append((s_ea, txt))
    return out

for needle in ["PremissionOfflineNesys", "PremissionOnline", "PermissionOffline", "OfflineNesys"]:
    for s_ea, txt in find_string(needle):
        lines.append("STRING 0x%X : %r" % (s_ea, txt))
        for xref in idautils.XrefsTo(s_ea):
            frm = xref.frm
            f = ida_funcs.get_func(frm)
            if f:
                lines.append("   xref 0x%X  in func 0x%X (%s)" % (frm, f.start_ea, ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or "?"))
            else:
                lines.append("   xref 0x%X (no func)" % frm)
        lines.append("")

# Also find strings 'Ani_NESiCA_Offline' / green icon related
for needle in ["NESiCA_Offline", "NESiCA_Online", "bUseNesys", "isNesysOnline"]:
    for s_ea, txt in find_string(needle):
        lines.append("STRING 0x%X : %r" % (s_ea, txt[:60]))
        for xref in idautils.XrefsTo(s_ea):
            f = ida_funcs.get_func(xref.frm)
            if f:
                lines.append("   xref 0x%X in func 0x%X (%s)" % (xref.frm, f.start_ea, ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or "?"))
        lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("WROTE %s" % OUT)

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
