"""After PDB load: dump all names containing Weapon, and the address of the CF90 region's func."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76r_pdb_names.json"
PDB = r"C:\Users\KAHO\Downloads\Starwing Paradox\Hoshi Tsuba\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.pdb"

import importlib
for m in ("ida_loadpdb", "ida_pdb"):
    try:
        mod = importlib.import_module(m)
        try:
            mod.load_pdb(PDB)
        except Exception as e:
            pass
        break
    except Exception:
        mod = None

import ida_funcs, ida_name, ida_hexrays

res = {"names": [], "errors": []}
try:
    for ea in idautils.Functions():  # noqa
        nm = ida_name.get_name(ea)
        if nm and ("WeaponPack" in nm or "WeaponManager" in nm or "CreateWeaponBody" in nm or "InitWeaponPack" in nm):
            res["names"].append((hex(ea), nm))
except Exception as e:
    try:
        import idautils
        for ea in idautils.Functions():
            nm = ida_name.get_name(ea)
            if nm and ("WeaponPack" in nm or "WeaponManager" in nm or "CreateWeaponBody" in nm or "InitWeaponPack" in nm):
                res["names"].append((hex(ea), nm))
    except Exception as e2:
        res["errors"].append("iterate: %r" % e2)

# also dump names of funcs around CF90 region 0x142435000-0x142436000
for ea in range(0x142435000, 0x142437000):
    f = ida_funcs.get_func(ea)
    if f:
        res["names"].append((hex(f.start_ea), ida_name.get_name(f.start_ea) or ""))
        ea = f.end_ea - 1

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)