import json
import os
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47f_callers2.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import ida_hexrays
    import ida_xref
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


def decompile_with_retry(ea):
    last = None
    for attempt in range(3):
        try:
            cf = ida_hexrays.decompile(ea)
            if cf:
                return str(cf)
        except Exception as e:
            last = "DECOMPILE_ERR: %s" % e
    return last


FUNCS = {
    "OnReceiveResponseMatchingServer": 0x142C8FD30,
    "SetConnectAddress": 0x142C93310,
    "recheck_142CA1360": 0x142CA1360,
    "tail_142C806E0": 0x142C806E0,
    "GetHostAddress": 0x142C36160,
    "http_success_checker_142C85940": 0x142C85940,
}

func_dump = {}
for name, ea in FUNCS.items():
    func_dump[name] = {
        "ea": hex(ea),
        "name": fname(ea),
        "decompiled": decompile_with_retry(ea),
    }
results["sections"]["function_dump"] = func_dump

caller_targets = {
    "OnReceiveResponseMatchingServer_callers": 0x142C8FD30,
    "SetConnectAddress_callers": 0x142C93310,
    "recheck_142CA1360_callers": 0x142CA1360,
    "GetHostAddress_callers": 0x142C36160,
}
callers = {}
for name, ea in caller_targets.items():
    entry = {"target_ea": hex(ea), "target_name": fname(ea), "xrefs": [], "functions": []}
    seen = set()
    try:
        for xref in idautils.XrefsTo(ea, 0):
            fs, fe = func_of(xref.frm)
            entry["xrefs"].append({
                "xref_ea": hex(xref.frm), "xref_type": xref.type,
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
