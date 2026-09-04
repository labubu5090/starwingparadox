import json
import os
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47c_fileoff.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_loader
    import ida_funcs
    import ida_name
    import ida_segment
    import ida_xref
    import ida_hexrays
    import idautils
    import ida_bytes
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


def file_off_to_ea(foff):
    for seg in idautils.Segments():
        segobj = ida_segment.getseg(seg)
        if not segobj:
            continue
        try:
            base = ida_loader.get_fileregion_offset(seg)
        except Exception:
            continue
        if base != 0xFFFFFFFFFFFFFFFF:
            size = segobj.end_ea - segobj.start_ea
            if base <= foff < base + size:
                return seg + (foff - base)
    return None


def decompile(fs):
    try:
        cf = ida_hexrays.decompile(fs)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


# Known file offsets of key strings (from string_analysis_results.json)
TARGETS = {
    "GetHostAddress_matchingtype": {"foff": 127387936, "is_unicode": True},
    "GetHostAddress_httpip_empty": {"foff": 127388944, "is_unicode": True},
    "Use_GetNesysInfo_addr_1": {"foff": 127178384, "is_unicode": True},
    "Use_GetNesysInfo_addr_2": {"foff": 127180208, "is_unicode": True},
    "SetNesysGameServerInfo_unicode": {"foff": 127742704, "is_unicode": True},
    "GetNesysGameServerHttpIP_ascii_127694384": {"foff": 127694384, "is_unicode": False},
    "GetNesysGameServerHttpIP_unicode_127796016": {"foff": 127796016, "is_unicode": True},
}

xref_results = {}

for name, t in TARGETS.items():
    entry = {"target": name, "file_offset": t["foff"],
             "string_ea": None, "xrefs": [], "functions": []}
    try:
        ea = file_off_to_ea(t["foff"])
        entry["string_ea"] = hex(ea) if ea else None
        if ea:
            # xrefs to the string address (code references)
            seen_funcs = set()
            for xref in idautils.XrefsTo(ea):
                fs, fe = func_of(xref.frm)
                entry["xrefs"].append({
                    "xref_ea": hex(xref.frm), "xref_type": xref.type,
                    "function_ea": hex(fs) if fs else None,
                    "function_name": fname(fs) if fs else fname(xref.frm),
                })
                if fs and fs not in seen_funcs:
                    seen_funcs.add(fs)
                    body = decompile(fs)
                    entry["functions"].append({
                        "function_ea": hex(fs),
                        "function_name": fname(fs),
                        "decompiled": body,
                    })
    except Exception as e:
        results["errors"].append({"name": name, "error": str(e), "traceback": traceback.format_exc()})
    xref_results[name] = entry

results["sections"]["xref_results"] = xref_results

# Also dump all segments with file offset ranges for reference
results["sections"]["segments"] = []
for seg in idautils.Segments():
    segobj = ida_segment.getseg(seg)
    if not segobj:
        continue
    try:
        base = ida_loader.get_fileregion_offset(seg)
    except Exception:
        base = 0xFFFFFFFFFFFFFFFF
    results["sections"]["segments"].append({
        "segment_ea": hex(seg),
        "size": segobj.end_ea - segobj.start_ea,
        "file_offset_base": base if base != 0xFFFFFFFFFFFFFFFF else None,
        "name": ida_segment.get_segm_name(segobj),
    })

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
