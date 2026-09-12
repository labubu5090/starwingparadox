"""G55: find all functions touching ReadCardMain offset +1424 (DebugNesicaSelectNo) and card-data table at +1456."""
import json

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g55_1424refs.txt"

import ida_bytes, ida_funcs, ida_name, idautils, idc, ida_hexrays

def ea_to_str(ea):
    n = ida_name.get_name(ea) or ida_funcs.get_func_name(ea) or hex(ea)
    return n

results = []
# Scan all functions, look for instructions referencing [reg+1424] or [reg+0x590]
OFFSETS = [1424, 1456]
interesting = []

for func_ea in idautils.Functions():
    fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or hex(func_ea)
    f = ida_funcs.get_func(func_ea)
    if not f:
        continue
    cur = f.start_ea
    end = f.end_ea
    hits = []
    while cur < end:
        try:
            mnem = idc.print_insn_mnem(cur)
            if mnem:
                opstr = idc.generate_disasm_line(cur, 0)
                low = opstr.lower()
                if ("+1424" in low) or ("+0x590" in low) or ("+1424" in low) or ("+1456" in low) or ("+0x5b0" in low):
                    # check operands reference the offset
                    hits.append((hex(cur), opstr))
        except Exception:
            pass
        cur = idc.next_head(cur, end)
    if hits:
        interesting.append((func_ea, fname, hits))

lines = []
for ea, fname, hits in interesting:
    lines.append("#" * 80)
    lines.append("# func %s  %s" % (hex(ea), fname))
    lines.append("#" * 80)
    for haddr, hop in hits:
        lines.append("   %s: %s" % (haddr, hop))
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Found %d functions referencing offset 1424/1456" % len(interesting))
for ea, fname, hits in interesting:
    print("  %s %s (%d hits)" % (hex(ea), fname, len(hits)))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
