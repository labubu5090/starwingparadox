"""Dump exact bytes for InitWeaponPack (sub_142435890) prologue, sub_14243CA80 entry,
and xrefs to both, to design a runtime null-guard patch."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g105_initpack_bytes.json"

import ida_bytes, ida_funcs, ida_idaapi, idautils, idc  # noqa

res = {"bytes": {}, "xrefs": {}, "errors": []}

def dump_bytes(start, end, label):
    out = []
    ea = start
    while ea < end:
        # next insn
        nxt = idc.next_head(ea, end)
        if nxt == ida_idaapi.BADADDR:
            nxt = end
        b = ida_bytes.get_bytes(ea, nxt - ea)
        txt = idc.generate_disasm_line(ea, 0)
        out.append((hex(ea), (b.hex() if b else None), txt))
        ea = nxt
    res["bytes"][label] = out

def xrefs_to(ea, label):
    xs = []
    for x in idautils.XrefsTo(ea, 0):
        xs.append((hex(x.frm), hex(x.to), x.type, x.iscode))
    res["xrefs"][label] = xs

dump_bytes(0x142435890, 0x1424358D0, "InitWeaponPack_prologue")
dump_bytes(0x14243CA80, 0x14243CAC0, "CA80_entry")
dump_bytes(0x142435A0A, 0x142435A20, "InitWeaponPack_epilogue")
xrefs_to(0x142435890, "InitWeaponPack_callees")
xrefs_to(0x14243CA80, "CA80_callees")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)