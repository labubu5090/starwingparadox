"""Decompile ACPP_WeaponPack::InitWeaponPack (sub_142435890) + resolve +1520 vtable target."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76p_initweaponpack.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_idaapi
    import ida_name
    import idautils
    import idc
except ImportError as e:
    import ida_pro
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    ida_pro.qexit(1)

res = {"funcs": {}, "errors": []}

def add(ea, label):
    cfg = None
    try:
        f = ida_funcs.get_func(ea)
        if not f:
            res["errors"].append("%s: no func" % label)
            return
        if ea != f.start_ea:
            ea = f.start_ea
        cfg = ida_hexrays.decompile(ea)
        res["funcs"][label] = {"start_ea": hex(ea), "code": str(cfg) if cfg else None}
        if not cfg:
            res["errors"].append("%s: decompile None" % label)
    except Exception as e:
        res["errors"].append("%s: %r" % (label, e))

# InitWeaponPack
add(0x142435890, "InitWeaponPack")

# CreateWeaponBody candidates: functions called via vtable +1520. Find xrefs to CFA0 family?
# Instead: list all functions whose code mentions offset 0x388 reads from a local — brute:
# find all __cdecl? no. Use decompiled code scan for '0x388'.

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)