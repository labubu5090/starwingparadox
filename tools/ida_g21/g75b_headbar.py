import json
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g75b_headbar.json"
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


def to_bytes_utf16le(s):
    return " ".join("%02X" % b for b in s.encode("utf-16-le"))


def scan_bytes(pattern):
    hits = []
    try:
        import ida_search
        _find_binary = ida_search.find_binary
    except Exception:
        _find_binary = idc.find_binary
    ea = _find_binary(0, ida_bytes.BADADDR, pattern, 16, ida_bytes.SEARCH_DOWN | ida_bytes.SEARCH_CASE)
    while ea not in (ida_bytes.BADADDR, None, 0xFFFFFFFFFFFFFFFF):
        hits.append(ea)
        ea = _find_binary(ea + 2, ida_bytes.BADADDR, pattern, 16, ida_bytes.SEARCH_DOWN | ida_bytes.SEARCH_CASE)
    return hits


sec = {}
try:
    # search the full literal prefix in UTF-16LE
    for label, s in [
        ("SetUpHeadBar_Mob_utf16", "SetUpHeadBarMob 空きなし"),
        ("InfoParentWidget_utf16", "UCPP_InfoParentWidget::SetUpHeadBarMob"),
        ("akinas_utf16", "空きなし"),
    ]:
        hits = scan_bytes(to_bytes_utf16le(s))
        entry = {"hits": [hex(h) for h in hits], "count": len(hits), "xrefs": []}
        for h in hits:
            for x in idautils.XrefsTo(h, 0):
                fs, fe = func_of(x.frm)
                entry["xrefs"].append({
                    "string_ea": hex(h), "from": hex(x.frm), "type": x.type,
                    "func_start": hex(fs) if fs else None,
                    "func_name": fname(fs) if fs else fname(x.frm),
                })
        sec[label] = entry

    # For each distinct string hit, also scan .text for LEA/MOV rip-relative refs manually
    # over the whole database via IDA disasm (fallback).
    # We'll instead gather functions whose name hints 'HeadBar' or 'InfoParent'
    fn_hits = []
    for ea, name in idautils.Names():
        if name and ("HeadBar" in name or "InfoParent" in name or "SetUpHeadBar" in name):
            fn_hits.append({"ea": hex(ea), "name": name})
    sec["named_functions_hint"] = fn_hits

    # decompile the calling functions found by xref
    decomp = []
    seen = set()
    for label in sec:
        if not isinstance(sec[label], dict):
            continue
        for x in sec[label].get("xrefs", []):
            fs = x.get("func_start")
            if fs and fs not in seen:
                seen.add(fs)
                decomp.append({
                    "func_start": fs, "func_name": x["func_name"],
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
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
