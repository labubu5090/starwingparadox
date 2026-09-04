import json
import os
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47d_callers.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_loader
    import ida_funcs
    import ida_name
    import ida_segment
    import ida_xref
    import ida_hexrays
    import idautils
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e)})
    results["status"] = "FATAL_IMPORT_ERROR"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    try:
        import ida_pro
        ida_pro.qexit(1)
    except Exception:
        pass
    raise SystemExit


def fname(ea):
    try:
        return ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or hex(ea)
    except Exception:
        return hex(ea)


def func_of(ea):
    try:
        f = ida_funcs.get_func(ea)
        if f:
            return f.start_ea, f.end_ea
    except Exception:
        pass
    return None, None


def decompile(fs):
    try:
        cf = ida_hexrays.decompile(fs)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


def decompile_with_retry(ea):
    for attempt in range(3):
        body = decompile(ea)
        if body and not body.startswith("DECOMPILE_ERR"):
            return body
    return body


# Known function EAs from prior g47c run (file-offset mapped)
FUNC_EAS = {
    "SetNesysGameServerInfo": 0x142D52C60,
    "GetNesysGameServerHttpIP_getter": 0x142D49DE0,
    "nesys_object_getter_142C6C600": 0x142C6C600,
    "httpip_reader_142C64490": 0x142C64490,
    "GetHostAddress": 0x142C36160,
}

# 1) Decompile each known function directly
func_dump = {}
for name, ea in FUNC_EAS.items():
    func_dump[name] = {
        "ea": hex(ea),
        "name": fname(ea),
        "decompiled": decompile_with_retry(ea),
    }
results["sections"]["function_dump"] = func_dump

# 2) Callers (xrefs) of SetNesysGameServerInfo and GetNesysGameServerHttpIP
caller_targets = {
    "SetNesysGameServerInfo_callers": 0x142D52C60,
    "GetNesysGameServerHttpIP_callers": 0x142D49DE0,
    "httpip_reader_callers": 0x142C64490,
}
callers = {}
for name, ea in caller_targets.items():
    entry = {"target_ea": hex(ea), "target_name": fname(ea), "xrefs": [], "functions": []}
    seen = set()
    try:
        for xref in idautils.XrefsTo(ea):
            fs, fe = func_of(xref.frm)
            entry["xrefs"].append({
                "xref_ea": hex(xref.frm),
                "xref_type": xref.type,
                "function_ea": hex(fs) if fs else None,
                "function_name": fname(fs) if fs else fname(xref.frm),
            })
            if fs and fs not in seen:
                seen.add(fs)
                entry["functions"].append({
                    "function_ea": hex(fs),
                    "function_name": fname(fs),
                    "decompiled": decompile_with_retry(fs),
                })
    except Exception as e:
        results["errors"].append({"name": name, "error": str(e), "traceback": traceback.format_exc()})
    callers[name] = entry
results["sections"]["callers"] = callers

results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
print("STATUS: %s" % results["status"])
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
