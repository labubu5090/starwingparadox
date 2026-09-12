import json
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g77_charactercustomize_probe.json"
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


def to_bytes_ascii(s):
    return s.encode("ascii", errors="ignore")


def to_bytes_utf16le(s):
    return s.encode("utf-16-le")


def scan_bytes(pattern_bytes):
    hits = []
    n = len(pattern_bytes)
    for seg in idautils.Segments():
        seg_size = idc.get_segm_end(seg) - seg
        if seg_size <= 0 or seg_size > 0x40000000:
            continue
        data = idc.get_bytes(seg, seg_size)
        if not data:
            continue
        pos = data.find(pattern_bytes)
        while pos != -1:
            hits.append(seg + pos)
            pos = data.find(pattern_bytes, pos + 1)
    return hits


def collect(label, s):
    out = {"label": label, "target": s, "ascii": [], "utf16": [], "ascii_xrefs": [], "utf16_xrefs": []}
    try:
        ah = scan_bytes(to_bytes_ascii(s))
        out["ascii"] = [hex(h) for h in ah]
        for h in ah:
            for x in idautils.XrefsTo(h, 0):
                fs, fe = func_of(x.frm)
                out["ascii_xrefs"].append({
                    "string_ea": hex(h), "from": hex(x.frm), "type": x.type,
                    "func_start": hex(fs) if fs else None,
                    "func_end": hex(fe) if fe else None,
                    "func_name": fname(fs) if fs else fname(x.frm),
                })
        uh = scan_bytes(to_bytes_utf16le(s))
        out["utf16"] = [hex(h) for h in uh]
        for h in uh:
            for x in idautils.XrefsTo(h, 0):
                fs, fe = func_of(x.frm)
                out["utf16_xrefs"].append({
                    "string_ea": hex(h), "from": hex(x.frm), "type": x.type,
                    "func_start": hex(fs) if fs else None,
                    "func_end": hex(fe) if fe else None,
                    "func_name": fname(fs) if fs else fname(x.frm),
                })
    except Exception as e:
        results["errors"].append({"name": "collect_" + label, "error": str(e), "traceback": traceback.format_exc()})
    return out


try:
    sec = {}
    for label, s in [
        ("char_customize_in_profile", "FCharacterCustomize In PlayerProfile"),
        ("setplparts", "SetPlParts"),
        ("debug_char_customize", "Debug_CharacterCustomizeLog"),
        ("setplparts_err", "SetPlParts / FCharacterCustomize In PlayerProfile"),
    ]:
        sec[label] = collect(label, s)

    # Decompile the functions that reference these strings
    decomp = []
    seen = set()
    for label in ("char_customize_in_profile", "setplparts"):
        entry = sec.get(label, {})
        for x in entry.get("utf16_xrefs", []) + entry.get("ascii_xrefs", []):
            fs = x.get("func_start")
            if fs and fs not in seen:
                seen.add(fs)
                decomp.append({
                    "signature": label, "func_start": fs, "func_name": x["func_name"],
                    "decompiled": decompile(int(fs, 16)),
                })
        # also include the exact error-string function
    entry = sec.get("setplparts_err", {})
    for x in entry.get("utf16_xrefs", []) + entry.get("ascii_xrefs", []):
        fs = x.get("func_start")
        if fs and fs not in seen:
            seen.add(fs)
            decomp.append({
                "signature": "setplparts_err", "func_start": fs, "func_name": x["func_name"],
                "decompiled": decompile(int(fs, 16)),
            })
    sec["functions_decompiled"] = decomp
    results["sections"]["analysis"] = sec
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