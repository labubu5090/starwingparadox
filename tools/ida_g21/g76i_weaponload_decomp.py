"""Decompile the weapon JSON container handler + check the weapon_roles function direction."""
import json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76i_weaponload_decomp.json"

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

results = {"functions": {}, "errors": [], "xrefs": {}}
try:
    ida_hexrays.init_hexrays_plugin()
except Exception as e:
    results["errors"].append("hexrays init: %r" % e)

def add(ea, label):
    try:
        cfg = ida_hexrays.decompile(ea)
        if cfg:
            results["functions"][label] = {"ea": hex(ea), "name": ida_name.get_name(ea) or label, "code": str(cfg)}
        else:
            results["errors"].append("%s: None" % label)
    except Exception as e:
        results["errors"].append("%s: %r" % (label, e))

add(0x142C04E00, "container_handler")
add(0x142C072A0, "weapon_roles_fn")
add(0x142C04F68, "xref_weapon_roles")
add(0x142C04FE7, "xref_weapon_role_presets")
add(0x142C05066, "xref_weapon_role_preset_slots")

for s in ["weapon_roles", "weapon_role_presets", "weapon_role_preset_slots", "role_id", "preset_id", "slot_id", "weapon_id"]:
    addr = ida_name.get_name_ea(idc.BADADDR, s)
    if addr == idc.BADADDR:
        addr = 0
    refs = []
    if addr:
        for x in idautils.XrefsTo(addr):
            refs.append(hex(x.frm))
    results["xrefs"][s] = {"addr": hex(addr) if addr else None, "to": refs[:40]}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)