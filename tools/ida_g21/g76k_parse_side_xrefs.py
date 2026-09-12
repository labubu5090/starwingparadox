"""Find parse-side mirrors: xrefs to the 3 weapon serializers and the container handler."""
import json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76k_parse_side_xrefs.json"

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

results = {}
TARGETS = {
    "weapon_roles_ser": 0x142C072A0,
    "weapon_role_presets_ser": 0x142C078A0,
    "weapon_role_preset_slots_ser": 0x142C07E20,
    "container_ser": 0x142C04AF0,
    "weapon_pack": 0x142E6E040,
}
for label, ea in TARGETS.items():
    refs = [x.frm for x in idautils.XrefsTo(ea)]
    out = []
    for r in refs:
        fn = ida_funcs.get_func(r)
        out.append({"from": hex(r), "in_func": hex(fn.start_ea) if fn else None,
                    "name": ida_name.get_name(fn.start_ea) if fn else None})
    results[label] = out

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)