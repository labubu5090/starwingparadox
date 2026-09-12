"""Decompile GetWeaponPackSet core + 3 weapon-role parse handlers via existing .i64."""
import json, os, sys

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76f_weaponpack_decomp.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_name
    import idautils
    import idc
except ImportError as e:
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"functions": {}, "errors": []}
try:
    ida_hexrays.init_hexrays_plugin()
except Exception as e:
    results["errors"].append("hexrays init: %r" % e)

# (addr, label)
TARGETS = [
    (0x142E6E040, "GetWeaponPackSet_core"),
    (0x142C072A0, "weapon_roles_parse"),
    (0x142C078A0, "weapon_role_presets_parse"),
    (0x142C07E20, "weapon_role_preset_slots_parse"),
]

for ea, label in TARGETS:
    try:
        fn = ida_funcs.get_func(ea)
        if not fn:
            # try to locate function containing ea
            fn = ida_funcs.get_func(ida_funcs.get_func(ea))
        if not fn:
            results["errors"].append("%s: no func @0x%x" % (label, ea))
            continue
        name = ida_name.get_name(ea) or label
        cf = ida_hexrays.decompile(ea)
        if cf:
            results["functions"][label] = {
                "name": name,
                "ea": hex(ea),
                "code": str(cf),
            }
        else:
            results["errors"].append("%s: decompile None" % label)
    except Exception as e:
        results["errors"].append("%s: %r" % (label, e))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)