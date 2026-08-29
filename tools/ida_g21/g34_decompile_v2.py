"""IDA decompile without auto_wait - uses existing analysis database."""
import json
import os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_decompile_v2.json"

try:
    import ida_ida
    import ida_funcs
    import ida_name
    import ida_hexrays
    import idautils
    import idc
except ImportError as e:
    with open(OUT, "w") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"status": "RUNNING", "functions": {}, "errors": []}

# Check if hex-rays is available
try:
    hr = ida_hexrays.init_hexrays_plugin()
    results["hexrays_available"] = hr
except Exception as e:
    results["hexrays_available"] = False
    results["hexrays_error"] = str(e)

# Find functions by name
PATTERNS = [
    "FAcrNetworkConfig",
    "AcrNetworkConfig",
    "Decide_connect",
    "MatchingServer",
    "UAcrProtocol",
    "Connect",
    "NesysControl",
    "IsOnline",
    "HttpServer",
    "MatchingServerType",
]

found = {}
for func_ea in idautils.Functions():
    fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
    for pat in PATTERNS:
        if pat.lower() in fname.lower():
            found[fname] = func_ea
            break

results["found_count"] = len(found)
results["found_functions"] = {name: hex(ea) for name, ea in found.items()}

# Try to decompile
if results["hexrays_available"]:
    for fname, ea in found.items():
        try:
            cfunc = ida_hexrays.decompile(ea)
            if cfunc:
                code = str(cfunc)
                results["functions"][fname] = {
                    "ea": hex(ea),
                    "length": len(code),
                    "code": code[:8000],
                }
            else:
                results["functions"][fname] = {"ea": hex(ea), "decompile_failed": True}
        except Exception as e:
            results["functions"][fname] = {"ea": hex(ea), "error": str(e)}
else:
    results["errors"].append("Hex-Rays not available")

results["status"] = "SUCCESS"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("HEXRAYS: %s" % results.get("hexrays_available"))
print("FOUND: %d functions" % results.get("found_count", 0))
print("DECOMPILED: %d functions" % len(results.get("functions", {})))
for name, data in list(results.get("functions", {}).items())[:10]:
    print("  %s: %s" % (name, data.get("ea", "?")))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
