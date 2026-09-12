import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g51_disasm.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import idautils
    import ida_bytes
    import ida_ua
    import ida_lines
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


def disasm_range(start, end, max_insn=9000):
    insns = []
    ea = start
    while ea < end and len(insns) < max_insn:
        insn = ida_ua.insn_t()
        if not ida_ua.decode_insn(insn, ea):
            insns.append({"ea": hex(ea), "text": "???"})
            ea += 1
            continue
        text = ida_lines.generate_disasm_line(ea, 0)
        insns.append({
            "ea": hex(ea),
            "rva": ea - 0x140000000,
            "size": insn.size,
            "bytes": ida_bytes.get_bytes(ea, insn.size).hex() if ida_bytes.get_bytes(ea, insn.size) else "",
            "text": text,
        })
        ea += insn.size
    return insns


f = ida_funcs.get_func(0x142C36160)
results["sections"]["GetHostAddress"] = {
    "start": hex(f.start_ea), "end": hex(f.end_ea),
    "insns": disasm_range(f.start_ea, f.end_ea),
}

f2 = ida_funcs.get_func(0x142C64510)
results["sections"]["sub_142C64510"] = {
    "start": hex(f2.start_ea), "end": hex(f2.end_ea),
    "insns": disasm_range(f2.start_ea, f2.end_ea),
}

# the JUMPOUT target context (info-present path)
results["sections"]["jumpout_context"] = []
for ea in range(0x143B76FC0 - 64, 0x143B76FC0 + 96):
    insn = ida_ua.insn_t()
    if ida_ua.decode_insn(insn, ea):
        results["sections"]["jumpout_context"].append({
            "ea": hex(ea),
            "size": insn.size,
            "bytes": ida_bytes.get_bytes(ea, insn.size).hex(),
            "text": ida_lines.generate_disasm_line(ea, 0),
        })
        ea += insn.size - 1

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
