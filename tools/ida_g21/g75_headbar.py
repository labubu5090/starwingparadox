import json
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g75_headbar.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import ida_hexrays
    import ida_ua
    import idc
    import idautils
    import ida_bytes
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


STRING_VA = 0x146F17FDE  # 'UCPP_InfoParentWidget::SetUpHeadBarMob 空きなし)'


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


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


sec = {}
try:
    # confirm string at addr
    label = idc.get_strlit_contents(STRING_VA, -1, idc.STRTYPE_C_16)
    sec["string_at_va_utf16"] = None
    if label:
        sec["string_at_va_utf16"] = label.decode("utf-8", errors="replace")
    sec["string_va"] = hex(STRING_VA)

    # all code xrefs to the string
    xrefs = []
    for x in idautils.XrefsTo(STRING_VA, 0):
        fs, fe = func_of(x.frm)
        xrefs.append({
            "from": hex(x.frm), "type": x.type,
            "func_start": hex(fs) if fs else None,
            "func_name": fname(fs) if fs else fname(x.frm),
        })
    sec["xrefs_to_string"] = xrefs
    sec["xref_count"] = len(xrefs)

    # Unique calling functions, decompile each
    fns = {}
    for x in xrefs:
        if x["func_start"]:
            fns[x["func_start"]] = x["func_name"]
    decomp = []
    for fs, fn in fns.items():
        decomp.append({
            "func_start": fs, "func_name": fn,
            "decompiled": decompile(int(fs, 16)),
        })
    sec["functions_decompiled"] = decomp
    sec["function_count"] = len(decomp)
except Exception as e:
    results["errors"].append({"name": "main", "error": str(e), "traceback": traceback.format_exc()})

results["sections"]["headbar"] = sec
results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
print("STATUS: %s" % results["status"])
print("XRCOUNTS: %d" % len(sec.get("xrefs_to_string", [])))
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
