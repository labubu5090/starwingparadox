"""IDA targeted decompilation for FAcrNetworkConfig and MatchingServer paths."""
import json
import os
import sys
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_decompile.json"

try:
    import ida_ida
    import ida_kernwin
    import ida_nalt
    import ida_bytes
    import ida_funcs
    import ida_name
    import ida_segment
    import ida_hexrays
    import idautils
    import idc
except ImportError as e:
    with open(OUT, "w") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"status": "RUNNING", "functions": {}, "errors": []}

# Wait for auto-analysis (limited)
try:
    ida_auto = __import__("ida_auto")
    ida_auto.auto_wait()
except:
    pass

def decompile_func(ea):
    """Try to decompile a function at ea."""
    try:
        cfunc = ida_hexrays.decompile(ea)
        if cfunc:
            return str(cfunc)
    except:
        pass
    return None

def find_func_by_name(name_patterns):
    """Find functions matching name patterns."""
    found = {}
    for func_ea in idautils.Functions():
        fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
        for pat in name_patterns:
            if pat.lower() in fname.lower():
                found[fname] = func_ea
    return found

# Target functions
TARGET_PATTERNS = [
    "FAcrNetworkConfig",
    "AcrNetworkConfig",
    "NetworkConfig",
    "Decide connect",
    "MatchingServer address",
    "Connect MatchingServer",
    "UseConfigMatchingServer",
    "MatchingServerType",
    "UAcrProtocol::Connect",
    "OnReceiveMatchingServer",
    "NesysControl",
    "IsOnline",
]

# Find matching functions
found_funcs = find_func_by_name(TARGET_PATTERNS)
results["found_functions"] = {name: hex(ea) for name, ea in found_funcs.items()}

# Try to decompile each
for fname, ea in found_funcs.items():
    try:
        pseudocode = decompile_func(ea)
        if pseudocode:
            results["functions"][fname] = {
                "ea": hex(ea),
                "pseudocode_length": len(pseudocode),
                "pseudocode_preview": pseudocode[:5000],
            }
        else:
            results["functions"][fname] = {
                "ea": hex(ea),
                "decompile_failed": True,
            }
    except Exception as e:
        results["functions"][fname] = {
            "ea": hex(ea),
            "error": str(e),
        }

# Also find string xrefs for key strings
STRING_TARGETS = [
    "FAcrNetworkConfig::Init",
    "Decide connect type INI",
    "Use Config(.ini)",
    "MatchingServerType",
    "DefaultMatchingServerAddress",
    "DefaultHttpServerAddress",
    "HttpServerAddress",
    "Configure AcrNetworkConfig",
    "FCommandLine::Get",
]

for s_ea in idautils.Strings():
    try:
        s = idc.get_strlit_contents(s_ea)
        if s:
            s = s.decode("utf-8", errors="ignore")
            for target in STRING_TARGETS:
                if target in s:
                    xrefs = []
                    for xref in idautils.XrefsTo(s_ea):
                        fn_ea = None
                        f = ida_funcs.get_func(xref.frm)
                        if f:
                            fn_ea = f.start_ea
                            fn_name = ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or hex(f.start_ea)
                        else:
                            fn_name = hex(xref.frm)
                        xrefs.append({
                            "ea": hex(xref.frm),
                            "function": fn_name,
                            "function_ea": hex(fn_ea) if fn_ea else None,
                        })
                    results["functions"]["str_" + target] = {
                        "string": s[:200],
                        "string_ea": hex(s_ea),
                        "xrefs": xrefs[:5],
                    }
                    break
    except:
        pass

results["status"] = "SUCCESS"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("STATUS: %s" % results["status"])
print("FUNCTIONS: %d" % len(results["functions"]))
for name, data in results["functions"].items():
    ea = data.get("ea", "?")
    has_code = "pseudocode_length" in data
    print("  %s: %s (decompiled=%s)" % (name, ea, has_code))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
