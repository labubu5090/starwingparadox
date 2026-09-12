"""Query .i64 for weapon-pack function addresses using mangled-name prefix scan.
Try loading X:\ sibling PDB first (the DB was likely created from X:\ exe)."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76t_mangled_query.json"
PDB_X = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.pdb"

res = {"found": [], "errors": []}
import ida_funcs, ida_name, ida_idaapi, idautils, idc  # noqa

# try load with X: pdb (matching module path)
for mod in ("ida_loadpdb", "ida_pdb"):
    try:
        m = __import__(mod)
        try:
            m.load_pdb(PDB_X)
            res["pdb_load_%s" % mod] = "ok"
        except Exception as e:
            res["pdb_load_%s" % mod] = "err: %r" % e
        break
    except Exception:
        continue

prefixes = ["?CreateWeaponBody@ACPP_WeaponPack@@",
            "?InitWeaponPack@ACPP_WeaponPack@@",
            "?InitalizeWeapon@ACPP_WeaponManager@@"]
count_all = 0
for ea in idautils.Functions():
    nm = ida_name.get_name(ea)
    if not nm:
        continue
    count_all += 1
    for p in prefixes:
        if nm.startswith(p):
            res["found"].append((hex(ea), nm))
            break
res["total_named"] = count_all

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)