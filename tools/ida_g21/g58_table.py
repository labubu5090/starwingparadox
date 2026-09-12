"""G58: decompile debug-card table source (sub_142A622C0) + copy (sub_142877AB0)
to understand table slots and what slot 0 contains."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g58_table.txt"

import ida_hexrays, ida_funcs, ida_name

TARGETS = [
    (0x142A622C0, "DebugCardTable_Source"),
    (0x142877AB0, "DebugCardTable_CopyInto"),
    (0x142AD8F00, "Clear_DebugCard_main"),
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
