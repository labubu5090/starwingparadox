"""G60: decompile the EnterPressed handler (sub_142ADCE40) and related button
handlers to find the ReadCardExec -> PremissionOfflineNesys transition."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g60_enter.txt"

import ida_hexrays, ida_funcs, ida_name

TARGETS = [
    (0x142ADCE40, "EnterPressed_handler"),
    (0x142ADE8B0, "PressingN_handler"),
    (0x142AD1B40, "PressingB_handler"),
    (0x142AE4F90, "SetNextMode_helper"),
    (0x142AE47B0, "ChangeReadCardMode_helper"),
]

lines = []
for ea, label in TARGETS:
    lines.append("=" * 80)
    lines.append("### %s  ea=%s name=%s" % (label, hex(ea), ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or "?"))
    lines.append("=" * 80)
    try:
        c = ida_hexrays.decompile(ea)
        lines.append(str(c) if c else "no decomp")
    except Exception as e:
        lines.append("FAIL: %s" % e)
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("WROTE %s" % OUT)

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
