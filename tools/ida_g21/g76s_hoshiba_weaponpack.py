"""Open Hoshi Tsuba exe (should auto-load sibling PDB in batch with -A + autoload),
enumerate any names and decompile weapon-related functions found by heuristic."""
import json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76s_hoshiba_weaponpack.json"

res = {"hexrays_ok": None, "names_sample": [], "weapon_funcs": [], "errors": []}

try:
    import ida_hexrays
    ida_hexrays.init_hexrays_plugin()
    res["hexrays_ok"] = True
except Exception as e:
    res["errors"].append("hexrays: %r" % e)
    res["hexrays_ok"] = False

import ida_funcs, ida_name, idautils, idc  # noqa

names = []
for ea in idautils.Functions():
    nm = ida_name.get_name(ea)
    if nm:
        names.append((ea, nm))

res["names_sample"] = [(hex(e), n) for e, n in names[:200]]

# find weapon-pack-ish functions
for ea, nm in names:
    if any(k in nm for k in ("WeaponPack", "WeaponManager", "WeaponBody", "WeaponSet")):
        res["weapon_funcs"].append((hex(ea), nm))

# count
res["total_named"] = len(names)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)