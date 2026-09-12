"""Probe around 0x243CF50: disasm, function containing, nearby funcs."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76o_probe_cf50.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_idaapi
    import idautils
    import idc
except ImportError as e:
    import ida_pro
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    ida_pro.qexit(1)

res = {"probe_pc": {}, "funcs_around": [], "errors": []}
BAD = ida_idaapi.BADADDR

anchor = 0x140000000 + 0x243CF50
f = ida_funcs.get_func(anchor)
res["probe_pc"]["func_at"] = (hex(f.start_ea), hex(f.end_ea)) if f else None

# disasm 20 insns before/after anchor
for i, ea in enumerate(range(anchor - 0x40, anchor + 0x80, 0x10)):
    try:
        res["probe_pc"]["i%02d_%x" % (i, ea)] = idc.generate_disasm_line(ea, 0)
    except Exception as e:
        res["errors"].append("disasm %x: %r" % (ea, e))

# all functions containing anchor-0x1000..anchor+0x1000
for ea in range(anchor - 0x2000, anchor + 0x2000, 1):
    ff = ida_funcs.get_func(ea)
    if ff:
        key = hex(ff.start_ea)
        if key not in [x[0] for x in res["funcs_around"]]:
            res["funcs_around"].append((key, hex(ff.end_ea)))
        ea = ff.end_ea - 1

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)