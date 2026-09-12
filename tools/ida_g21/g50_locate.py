import json
import re

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g50_locate.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import ida_hexrays
    import ida_bytes
    import ida_segment
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


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


def func_start_containing(ea):
    f = ida_funcs.get_func(ea)
    if f:
        return f.start_ea
    return None


TARGETS = {
    "sub_1445A9CE0": 0x1445A9CE0,
    "sub_142A2DA10": 0x142A2DA10,
    "sub_14337DF10": 0x14337DF10,
    "sub_142C5F260": 0x142C5F260,
}
results["sections"]["decompiles"] = {}
for key, ea in TARGETS.items():
    results["sections"]["decompiles"][key] = {
        "ea": hex(ea), "name": fname(ea), "decompiled": decompile(ea),
    }

# function containing the JUMPOUT target 0x143B76FC0
jump_ea = 0x143B76FC0
fs = func_start_containing(jump_ea)
results["sections"]["jumpout"] = {
    "target": hex(jump_ea),
    "func_start": hex(fs) if fs else None,
    "func_name": fname(fs) if fs else None,
    "decompiled": decompile(fs) if fs else None,
}

# data dump around off_148EE1730 (type descriptor) and the config block
def dump_data(va, n):
    out = []
    for off in range(0, n, 8):
        q = ida_bytes.get_qword(va + off)
        ea = va + off
        try:
            nm = ida_name.get_name(ea) or ""
        except Exception:
            nm = ""
        out.append({"offset": off, "ea": hex(ea), "name": nm, "qword": q, "hex": hex(q)})
    return out

results["sections"]["data_148EE1730_area"] = dump_data(0x148EE1730, 0x100)
results["sections"]["data_1494BA9E8"] = dump_data(0x1494BA9E8, 0x40)

# search strings containing "Nesys" near class names (StaticClass name refs)
results["sections"]["nesys_strings"] = []
try:
    for s in idautils.Strings():
        text = str(s)
        if "Nesys" in text or "NESYS" in text or "nesys" in text:
            ea = s.ea
            xrefs = []
            for x in idautils.XrefsTo(ea, 0):
                xrefs.append({"from": hex(x.frm), "func": fname(func_start_containing(x.frm) or x.frm)})
            results["sections"]["nesys_strings"].append({
                "ea": hex(ea), "text": text[:200], "xrefs": xrefs[:8],
            })
except Exception as e:
    results["errors"].append({"name": "nesys_strings", "error": str(e)})

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