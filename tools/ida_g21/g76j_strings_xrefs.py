"""Locate JSON key strings in .rdata and list xrefs to create parser side map."""
import json, os, struct

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76j_strings_xrefs.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_name
    import idautils
    import idc
    import ida_bytes
    import ida_segment
except ImportError as e:
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"strings": {}, "functions": {}}
KEYS = ["weapon_roles", "weapon_role_presets", "weapon_role_preset_slots",
        "role_id", "preset_id", "slot_id", "weapon_id"]

def find_str_ea(s):
    for enc, label in [("utf-16-le", "utf16"), ("utf-8", "utf8")]:
        tail = s + "\x00"
        b = tail.encode(enc)
        ea = idc.BADADDR
        seg = ida_segment.get_segm_by_name(".rdata")
        if seg:
            start = seg.start_ea
            end = seg.end_ea
        else:
            start = 0x140000000
            end = 0x142B00000
        p = start
        while p < end:
            hit = ida_bytes.find_bytes(b.hex(), p)
            if hit == idc.BADADDR:
                break
            ea = hit
            refs = [x.frm for x in idautils.XrefsTo(ea)]
            if refs:
                results["strings"][s] = {
                    "enc": label,
                    "ea": hex(ea),
                    "refs": [hex(x) for x in refs[:30]],
                    "ref_count": len(refs),
                }
                return
            p = hit + len(b)
    results["strings"][s] = {"ea": None, "refs": [], "ref_count": 0}

for s in KEYS:
    find_str_ea(s)

# Also dump xref site context (first ref each)
for s, info in results["strings"].items():
    if info.get("refs"):
        ea = int(info["refs"][0], 16)
        fn = ida_funcs.get_func(ea)
        if fn:
            info["site_func"] = hex(fn.start_ea)
            info["site_offset_in_func"] = hex(ea - fn.start_ea)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)