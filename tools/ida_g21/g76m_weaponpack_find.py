"""Locate + decompile ACPP_WeaponPack::CreateWeaponBody / InitWeaponPack from .i64."""
import json, os, sys

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76m_weaponpack_find.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_name
    import ida_search
    import ida_idaapi
    import idautils
    import idc
except ImportError as e:
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

res = {"functions": {}, "all_by_name": [], "errors": []}
try:
    ida_hexrays.init_hexrays_plugin()
except Exception as e:
    res["errors"].append("hexrays init: %r" % e)

if True:
    # every defined function -> name, in case PDB names are present
    for ea in idautils.Functions():
        nm = ida_name.get_name(ea)
        if nm:
            res["all_by_name"].append((hex(ea), nm))

    # find function via name if present
    targets = [
        "ACPP_WeaponPack::CreateWeaponBody",
        "ACPP_WeaponPack::InitWeaponPack",
        "ACPP_WeaponManager::InitalizeWeapon",
        "CPP_WeaponPack::CreateWeaponBody",
        "CPP_WeaponPack::InitWeaponPack",
    ]
    for t in targets:
        ea = ida_name.get_name_ea(0 if False else ida_idaapi.BADADDR, t)
        if ea != ida_idaapi.BADADDR and ea != 0xFFFFFFFFFFFFFFFF:
            try:
                cfg = ida_hexrays.decompile(ea)
                res["functions"][t] = {
                    "ea": hex(ea),
                    "name": t,
                    "code": str(cfg) if cfg else None,
                }
                if not cfg:
                    res["errors"].append("%s: decompile None" % t)
            except Exception as e:
                res["errors"].append("%s: %r" % (t, e))
        else:
            res["errors"].append("%s: not found by name" % t)
            # fallback: scan disasm text for the mangled name string
            try:
                for ea in idautils.Functions():
                    for ref in idautils.CodeRefsTo(ea, 1):
                        pass
            except Exception:
                pass

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)