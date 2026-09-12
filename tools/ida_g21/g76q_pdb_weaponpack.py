"""Load PDB symbols then decompile ACPP_WeaponPack::CreateWeaponBody + InitWeaponPack + manager.
The .i64 currently lacks PDB; use ida_load_pdb.load_pdb to pull symbols in-batch."""
import json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76q_pdb_weaponpack.json"
PDB = r"C:\Users\KAHO\Downloads\Starwing Paradox\Hoshi Tsuba\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.pdb"

try:
    import ida_funcs
    import ida_hexrays
    import ida_name
    import ida_idaapi
    import idautils
    import idc
    import ida_loadpdb
except ImportError as e:
    pass

# IDA 9.3: ida_pdb / ida_loadpdb
import importlib
mods = {}
for m in ("ida_pdb", "ida_loadpdb"):
    try:
        mods[m] = importlib.import_module(m)
    except Exception as e:
        mods[m] = None

res = {"errors": [], "found": {}, "functions": {}}

def add(ea, label):
    if not ea or ea == ida_idaapi.BADADDR:
        res["errors"].append("%s: bad addr" % label)
        return
    f = ida_funcs.get_func(ea)
    if f:
        cfg = None
        try:
            cfg = ida_hexrays.decompile(f.start_ea)
        except Exception as e:
            res["errors"].append("%s: %r" % (label, e))
        res["functions"][label] = {"start_ea": hex(f.start_ea), "code": str(cfg) if cfg else None}
        res["found"][label] = hex(f.start_ea)
    else:
        res["errors"].append("%s: no func at %x" % (label, ea))

# load pdb
try:
    if mods.get("ida_loadpdb"):
        mods["ida_loadpdb"].load_pdb(PDB)
    elif mods.get("ida_pdb"):
        mods["ida_pdb"].load_pdb(PDB)
    res["pdb"] = "loaded"
except Exception as e:
    res["errors"].append("pdb load: %r" % e)

targets = [
    "ACPP_WeaponPack::CreateWeaponBody",
    "ACPP_WeaponPack::InitWeaponPack",
    "ACPP_WeaponManager::InitalizeWeapon",
    "ACPP_CharacterEvent::InitalizeWeapon",
]
for t in targets:
    ea = ida_name.get_name_ea(ida_idaapi.BADADDR, t)
    if ea != ida_idaapi.BADADDR:
        add(ea, t)
    else:
        res["errors"].append("%s: still not found after pdb" % t)

# fallback: brute-force names if pdb loaded but names differ
if not res["found"]:
    for ea in idautils.Functions():
        nm = ida_name.get_name(ea)
        if nm and ("WeaponPack::" in nm or nm.endswith("CreateWeaponBody")) and len(res["found"]) < 8:
            res["found"]["auto_" + nm] = hex(ea)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)