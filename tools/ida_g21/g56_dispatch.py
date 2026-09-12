"""G56: decompile the ReadCard dispatcher (DebugNesicaButtonPressed / ReadNESiCA / ResetNESiCA)
and find callers of the DebugNesicaSelectNo gate sub_142AD6810."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g56_dispatch.txt"

import ida_funcs, ida_name, ida_hexrays, idautils, idc

lines = []

def decompile(ea, label):
    lines.append("=" * 80)
    lines.append("### %s  ea=%s name=%s" % (label, hex(ea), ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or "?"))
    lines.append("=" * 80)
    try:
        c = ida_hexrays.decompile(ea)
        lines.append(str(c) if c else "no decomp")
    except Exception as e:
        lines.append("FAIL: %s" % e)
    lines.append("")

# 1) The ReadCard component dispatcher containing DebugNesicaButtonPressed etc
decompile(0x142B089D0, "ReadCard_ComponentDispatcher")

# 2) callers of the 0x590 gate sub_142AD6810
lines.append("#" * 80)
lines.append("# CALLERS of sub_142AD6810 (DebugNesicaSelectNo gate / ChangeDebugWidgetInfo)")
lines.append("#" * 80)
for xref in idautils.XrefsTo(0x142AD6810):
    frm = xref.frm
    f = ida_funcs.get_func(frm)
    if f:
        lines.append("  %s  in func %s (%s)" % (hex(frm), hex(f.start_ea), ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or "?"))
    else:
        lines.append("  %s  (no func)" % hex(frm))
lines.append("")

# 3) callers of the constructor (to confirm it is the ReadCardMain constructor)
lines.append("#" * 80)
lines.append("# CALLERS of sub_142AD8A90 (constructor / Clear, sets DebugNesicaSelectNo=-1)")
lines.append("#" * 80)
for xref in idautils.XrefsTo(0x142AD8A90):
    frm = xref.frm
    f = ida_funcs.get_func(frm)
    if f:
        lines.append("  %s  in func %s (%s)" % (hex(frm), hex(f.start_ea), ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or "?"))
    else:
        lines.append("  %s  (no func)" % hex(frm))
lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("WROTE %s" % OUT)
print("decompiled dispatcher; size=%d" % len(lines))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
