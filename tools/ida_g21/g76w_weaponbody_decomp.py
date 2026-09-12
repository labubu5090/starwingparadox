"""Decompile candidates for CreateWeaponBody: sub_142433B20 (called by InitWeaponPack-path),
sub_1427FA4B0, sub_14325AAD0 (weapon data lookups)."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76w_weaponbody_decomp.json"

import ida_funcs, ida_hexrays, ida_idaapi  # noqa
ida_hexrays.init_hexrays_plugin()

res = {"funcs": {}, "errors": []}

def add(ea, label):
    f = ida_funcs.get_func(ea)
    if not f:
        res["errors"].append("%s: no func" % label)
        return
    try:
        cfg = ida_hexrays.decompile(f.start_ea)
        res["funcs"][label] = {"ea": hex(f.start_ea), "code": str(cfg) if cfg else None}
    except Exception as e:
        res["errors"].append("%s: %r" % (label, e))

add(0x142433B20, "candidate_CreateWeaponBody")
add(0x1427FA4B0, "GetWeaponData")
add(0x14325AAD0, "WeaponDataParse")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)