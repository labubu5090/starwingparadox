"""Decompile parse-side handlers for weapon JSON."""
import json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76l_parse_side_decomp.json"

try:
    import ida_hexrays
    import ida_name
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

TARGETS = [
    (0x142C3ADA0, "load_preset_slots_a"),
    (0x142C3CFF0, "load_roles_presets"),
    (0x142C3FA40, "load_roles"),
]
for ea, label in TARGETS:
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            results["functions"][label] = {"ea": hex(ea), "name": ida_name.get_name(ea) or label, "code": str(cf)}
        else:
            results["errors"].append("%s: None" % label)
    except Exception as e:
        results["errors"].append("%s: %r" % (label, e))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)