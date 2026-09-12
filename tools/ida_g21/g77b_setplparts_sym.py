import json
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g77b_setplparts_sym.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_bytes
    import ida_funcs
    import ida_name
    import ida_hexrays
    import idc
    import idautils
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e), "traceback": traceback.format_exc()})
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


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


try:
    named = []
    for ea, name in idautils.Names():
        low = name.lower() if name else ""
        if "setplparts" in low or ("charactercustomize" in low and "playerstate" in low):
            named.append({"ea": hex(ea), "name": name})

    results["sections"]["named"] = named

    decomp = []
    seen = set()
    for item in named:
        ea = int(item["ea"], 16)
        f = ida_funcs.get_func(ea)
        if not f:
            continue
        fs = f.start_ea
        if fs in seen:
            continue
        seen.add(fs)
        d = decompile(fs)
        if not d:
            continue
        decomp.append({"ea": hex(fs), "name": item["name"], "decompiled": d})
    results["sections"]["decompiled"] = decomp
except Exception as e:
    results["errors"].append({"name": "main", "error": str(e), "traceback": traceback.format_exc()})

results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
print("STATUS: %s" % results["status"])
print("ERR: %d" % len(results["errors"]))
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass