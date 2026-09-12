"""G64: full decompile of the SystemDataCheck Tick (0x142AFF640) and disasm
of the CheckVersion / IsOnlineStatus + event-request gate regions."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g64_sdc2.txt"

import ida_hexrays, ida_funcs, idc, ida_ua

lines = []

def decompile(ea, label):
    lines.append("=" * 90)
    lines.append("### %s  %08X (%s)" % (label, ea, ida_funcs.get_func_name(ea) or "?"))
    lines.append("=" * 90)
    try:
        c = ida_hexrays.decompile(ea)
        lines.append(str(c) if c else "no decomp")
    except Exception as e:
        lines.append("FAIL: %s" % e)

# Full decompile of the Tick function
decompile(0x142AFF640, "SystemDataCheck_Tick")

# Disassemble the CheckVersion / EventRequest / CheckOpenKey regions
def disasm_range(start, end, label):
    lines.append("=" * 90)
    lines.append("### DISASM %s %08X..%08X" % (label, start, end))
    lines.append("=" * 90)
    ea = start
    while ea < end:
        txt = idc.GetDisasm(ea)
        lines.append("%08X: %s" % (ea, txt))
        ea = idc.next_head(ea, end)
        if ea == idc.BADADDR or ea <= start:
            break
    lines.append("")

# EventRequest region and CheckVersion region from sd_flag_func_disasm.json
disasm_range(0x142AFF730, 0x142AFFAFE+4, "EventRequest_region")
disasm_range(0x142B000D6, 0x142B0049A+8, "CheckVersion_region")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("WROTE %s (%d chars)" % (OUT, sum(len(l)+1 for l in lines)))

try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
