import json
import os
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47b_bytescan.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_bytes
    import ida_funcs
    import ida_name
    import ida_xref
    import ida_hexrays
    import ida_ua
    import idc
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


try:
    import ida_search
    _find_binary = ida_search.find_binary
except Exception:
    _find_binary = idc.find_binary


def scan_bytes(pattern):
    """Return list of addresses where pattern (hex-string) occurs."""
    hits = []
    ea = _find_binary(0, ida_bytes.BADADDR, pattern, 16, ida_bytes.SEARCH_DOWN | ida_bytes.SEARCH_CASE)
    while ea != ida_bytes.BADADDR and ea is not None and ea != 0xFFFFFFFFFFFFFFFF:
        hits.append(ea)
        ea = _find_binary(ea + 1, ida_bytes.BADADDR, pattern, 16, ida_bytes.SEARCH_DOWN | ida_bytes.SEARCH_CASE)
    return hits


def to_bytes_ascii(s):
    return " ".join("%02X" % b for b in s.encode("ascii", errors="ignore"))


def to_bytes_utf16le(s):
    return " ".join("%02X" % b for b in s.encode("utf-16-le"))


def get_string_at(ea):
    try:
        s = idc.get_strlit_contents(ea)
        if s:
            return s.decode("utf-8", errors="ignore")
    except Exception:
        pass
    return None


def decompile(fs):
    try:
        cf = ida_hexrays.decompile(fs)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


targets = [
    "Use GetNesysInfo address:%s ENesysGameServerType:%s",
    "GetNesysGameServerHttpIP is empty.",
    "GetNesysGameServerHttpIP",
    "GetNesysGameServerTcpIP",
    "SetNesysGameServerInfo",
    "ResetNesysGameServerInfo",
    "MatchingServerType",
    "GetNetworkConfig",
]

# ---------------------------------------------------------------------------
# 1. Byte-scan each target (ASCII and UTF-16LE), find xrefs, decompile callers
# ---------------------------------------------------------------------------
for t in targets:
    entry = {"target": t, "ascii_hits": [], "utf16_hits": [], "xref_functions": []}
    try:
        for enc_name, pat in (("ascii", to_bytes_ascii(t)), ("utf16le", to_bytes_utf16le(t))):
            hits = scan_bytes(pat)
            entry[enc_name + "_hits"] = [hex(h) for h in hits[:50]]
            # for each hit, find all code xrefs
            for h in hits[:50]:
                for xref in idautils.XrefsTo(h):
                    fs, fe = func_of(xref.frm)
                    entry["xref_functions"].append({
                        "case": enc_name, "string_ea": hex(h),
                        "xref_ea": hex(xref.frm), "xref_type": xref.type,
                        "function_ea": hex(fs) if fs else None,
                        "function_name": fname(fs) if fs else fname(xref.frm),
                    })
        # dedupe xref_functions by function_ea
        seen = {}
        for xf in entry["xref_functions"]:
            key = xf["function_ea"]
            if key and key not in seen:
                seen[key] = xf
        entry["xref_functions"] = list(seen.values())
    except Exception as e:
        results["errors"].append({"name": "scan_" + t, "error": str(e), "traceback": traceback.format_exc()})
    results["sections"]["scan_" + t.replace(" ", "_").replace("%", "p")[:60]] = entry

# ---------------------------------------------------------------------------
# 2. Decompile the functions found via the two key format strings
# ---------------------------------------------------------------------------
try:
    decompiled = []
    seen = set()
    for t in ["Use GetNesysInfo address:%s ENesysGameServerType:%s",
              "GetNesysGameServerHttpIP is empty."]:
        key = "scan_" + t.replace(" ", "_").replace("%", "p")[:60]
        entry = results["sections"].get(key)
        if not entry:
            continue
        for xf in entry["xref_functions"]:
            if xf["function_ea"] and xf["function_ea"] not in seen:
                seen.add(xf["function_ea"])
                body = decompile(int(xf["function_ea"], 16))
                decompiled.append({
                    "target": t,
                    "function_ea": xf["function_ea"],
                    "function_name": xf["function_name"],
                    "decompiled": body,
                })
    results["sections"]["decompiled_functions"] = decompiled
except Exception as e:
    results["errors"].append({"name": "decompile_fns", "error": str(e), "traceback": traceback.format_exc()})

results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
print("STATUS: %s" % results["status"])
print("SECTIONS: %d" % len(results["sections"]))
print("ERRORS: %d" % len(results["errors"]))
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
