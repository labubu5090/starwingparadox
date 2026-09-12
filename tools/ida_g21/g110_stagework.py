import json
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g110_stagework.json"
import ida_funcs, ida_hexrays, idautils, idc, ida_bytes, ida_name, ida_segment
BADADDR = ida_idaapi.BADADDR
res = {"status": "RUNNING", "searched": [], "funcs": {}, "rip": None, "errors": []}

def fname(ea):
    return ida_funcs.get_func_name(ea) or hex(ea)

# locate by name variants
targets = []
for cand in ["UStageWork::IsValidStageRuleID", "IsValidStageRuleID", "UStageWork::GetStageRuleTerms", "GetStageRuleTerms"]:
    ea = idc.get_name_ea_simple(cand)
    if ea != BADADDR:
        targets.append((cand, ea))

# also search name list
for ea, name in idautils.Names():
    for cand in ["IsValidStageRuleID", "GetStageRuleTerms", "SetWidgetStageDirection"]:
        if cand.lower() in name.lower():
            targets.append((name, ea))

# dedupe
seen = set()
uniq = []
for n, ea in targets:
    if ea not in seen:
        seen.add(ea)
        uniq.append((n, ea))

res["searched"] = [{"name": n, "ea": hex(e)} for n, e in uniq]

RIP_RVA = 0x2DD8EB4
import ida_ida
base = ida_ida.inf_get_imagebase() if hasattr(ida_ida,"inf_get_imagebase") else ida_ida.inf_get_min_ea()
rip_ea = base + RIP_RVA
func = ida_funcs.get_func(rip_ea)
if func:
    res["rip"] = {"rva": hex(RIP_RVA), "ea": hex(rip_ea), "func": fname(func.start_ea), "func_rva": hex(func.start_ea - base)}
    import ida_lines
    lines = []
    for ea in range(func.start_ea, func.end_ea):
        d = idc.generate_disasm_line(ea, 0)
        if d:
            prev = idc.get_item_head(ea)
            lines.append({"rva": hex(ea - base), "text": d, "head": hex(prev - base)})
    res["funcs"][fname(func.start_ea)] = {"start_rva": hex(func.start_ea - base), "end_rva": hex(func.end_ea - base), "lines": lines[:260]}

for n, e in uniq:
    f = ida_funcs.get_func(e)
    if f:
        ida_hexrays.decompile(f.start_ea) if ida_hexrays.init_hexrays_plugin() else None
        try:
            cf = ida_hexrays.decompile(f.start_ea)
            if cf:
                res["funcs"][fname(f.start_ea)] = {"start_rva": hex(f.start_ea - base), "pseudo": str(cf)}
        except Exception as ex:
            res["errors"].append("decomp %s: %s" % (hex(f.start_ea), ex))

res["status"] = "DONE"
open(OUT, "w").write(json.dumps(res, indent=1))
print("wrote", OUT)
