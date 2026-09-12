import json
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g110_stagework_full.json"
import ida_funcs, ida_hexrays, idautils, idc, ida_bytes, ida_ida, ida_name
res = {"status": "RUNNING", "funcs": {}, "errors": []}
base = ida_ida.inf_get_min_ea()
func = ida_funcs.get_func(base + 0x2DD8E50)
res["func_start_ea"] = hex(func.start_ea)
ea = func.start_ea
lines = []
while ea < func.end_ea:
    text = idc.generate_disasm_line(ea, idc.GENDSM_FORCE_CODE)
    if not text:
        ea = idc.next_head(ea, func.end_ea)
        continue
    size = idc.get_item_size(ea)
    b = idc.get_bytes(ea, size).hex() if size else ""
    lines.append({"rva": hex(ea - base), "bytes": b, "text": text})
    ea += size
res["funcs"]["IsValidStageRuleID"] = {"start_rva": hex(func.start_ea - base), "end_rva": hex(func.end_ea - base), "lines": lines}
res["status"] = "DONE"
open(OUT, "w").write(json.dumps(res, indent=1))
print("ok", len(lines))
