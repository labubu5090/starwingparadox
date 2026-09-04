import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47g_disasm.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_ua
    import ida_bytes
    import ida_pro
    import ida_lines
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e)})
    results["status"] = "FATAL_IMPORT_ERROR"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    raise SystemExit

FUNCS = {
    "GetHostAddress_sub_142C36160": 0x142C36160,
    "type_getter_sub_142C6C600": 0x142C6C600,
    "httpip_reader_sub_142C64490": 0x142C64490,
    "GetHostAddress_caller_sub_142C81E20": 0x142C81E20,
}

def disasm_func(ea):
    lines = []
    f = ida_funcs.get_func(ea)
    if not f:
        return lines, "no func"
    cur = f.start_ea
    while cur < f.end_ea:
        insn = ida_ua.insn_t()
        length = ida_ua.decode_insn(insn, cur)
        if length == 0:
            lines.append({"ea": cur, "text": "<undecodable>"})
            cur += 1
            continue
        mnem = insn.get_canon_mnem()
        ops = []
        for i in range(8):
            try:
                oplen = ida_ua.print_operand(cur, i)
                if oplen:
                    ops.append(oplen)
                else:
                    break
            except Exception:
                break
        raw = ida_bytes.get_bytes(cur, length)
        bts = " ".join("%02X" % b for b in raw) if raw else ""
        text = (mnem + " " + ", ".join(ops)).strip()
        lines.append({"ea": cur, "len": length, "bytes": bts, "text": text})
        cur += length
    return lines, "ok"

for name, ea in FUNCS.items():
    try:
        lines, status = disasm_func(ea)
        results["sections"][name] = {"status": status, "lines": lines}
    except Exception as e:
        import traceback
        results["errors"].append({"name": name, "error": str(e), "traceback": traceback.format_exc()})

results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
ida_pro.qexit(0)
