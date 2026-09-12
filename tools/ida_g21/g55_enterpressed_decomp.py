"""G55: decompile ACPP_ReadCardMain::EnterPressed (sub_142ADCE40) and the
Constructor to map exactly how NESiCA_ID is populated in local/offline mode."""
import json
import traceback

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g55_enterpressed_decomp.txt"

TARGETS = [
    ("0x142ADCE40", "EnterPressed_ReadCardMain"),
    ("0x142AD8A90", "Constructor_ReadCardMain"),
    ("0x142AE4190", "SetReadCardMode"),
    ("0x142AD4F90", "BeginPlay_ReadCardMain"),
]

results = {}

for ea_str, label in TARGETS:
    ea = int(ea_str, 16)
    entry = {"ea": ea, "label": label}
    try:
        import ida_funcs, ida_name, ida_hexrays
        f = ida_funcs.get_func(ea)
        if f:
            entry["start"] = hex(f.start_ea)
            entry["end"] = hex(f.end_ea)
            name = ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or ""
            entry["name"] = name
        cfunc = ida_hexrays.decompile(ea)
        entry["ok"] = True
        entry["code"] = str(cfunc)
    except Exception as e:
        entry["ok"] = False
        entry["error"] = str(e)
    results[ea_str] = entry

lines = []
for ea_str, label in TARGETS:
    entry = results[ea_str]
    lines.append("=" * 80)
    lines.append("### %s  ea=%s label=%s" % (entry.get("name", "?"), ea_str, label))
    lines.append("=" * 80)
    if not entry.get("ok"):
        lines.append("DECOMPILE FAILED: %s" % entry.get("error", "?"))
    else:
        lines.append(entry.get("code", ""))
    lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("WROTE %s" % OUT)
for ea_str, label in TARGETS:
    print("  %s %s ok=%s" % (ea_str, label, results[ea_str].get("ok")))

try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass