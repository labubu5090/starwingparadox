"""G57: decompile debug card button handler + gate callers to complete no-patch injection picture."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g57_debugbtn.txt"

import ida_hexrays, ida_funcs, ida_name

TARGETS = [
    (0x142B210A0, "DebugNesicaButtonPressed"),
    (0x142ADADB0, "GateCaller_A"),
    (0x142B236F0, "ReadNESiCA"),
    (0x142B2BEA0, "GateCaller_D"),
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
