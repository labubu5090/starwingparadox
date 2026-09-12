import json
import re

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g49_objgetter.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import ida_hexrays
    import idautils
    import ida_ida
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


GLOBAL_RE = re.compile(r"(qword_|dword_|byte_|word_|__int64 _|off_|unk_|data_)[0-9A-Fa-f]+|0x149[0-9A-Fa-f]{6,}|L\"\w+\"")

TARGETS = {
    "sub_142C61450": 0x142C61450,
    "sub_142C64510": 0x142C64510,
    "sub_142C64490": 0x142C64490,
}

for key, ea in TARGETS.items():
    entry = {"function": key, "ea": hex(ea), "name": fname(ea), "decompiled": None, "referenced_names": []}
    body = decompile(ea)
    entry["decompiled"] = body
    if body:
        refs = set()
        for m in GLOBAL_RE.finditer(body):
            refs.add(m.group(0))
        # also extract any 0x140..8-digit addresses referenced as plain hex
        for m in re.finditer(r"\b0x1[0-4][0-9A-Fa-f]{6,}\b", body):
            refs.add(m.group(0))
        entry["referenced_names"] = sorted(refs)
    results["sections"][key] = entry

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