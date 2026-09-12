"""Disasm sub_142435890 (InitWeaponPack) full + find 0x388 reads + CreateWeaponBody via vtable.
Also disasm sub_14242ECC0 which InitalizeWeapon calls to create pack bodies.
"""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76v_initpack_disasm.json"

import ida_funcs, ida_name, ida_idaapi, idautils, idc  # noqa

res = {"disasm": {}}

def dump(start, end, label, max_ins=300):
    ins = []
    ea = start
    while ea < end and len(ins) < max_ins:
        txt = idc.generate_disasm_line(ea, 0)
        if txt:
            ins.append((hex(ea), txt))
        ea = idc.next_head(ea, end)
    res["disasm"][label] = ins

for lbl, start, end in [
    ("InitWeaponPack_sub_142435890", 0x142435890, None),
    ("ApplyPack_sub_14242ECC0", 0x14242ECC0, None),
]:
    f = ida_funcs.get_func(start)
    if f:
        dump(f.start_ea, f.end_ea, lbl)
    else:
        res["disasm"][lbl] = [("", "no func")]

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)