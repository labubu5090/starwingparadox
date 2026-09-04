# Find callers of these candidate functions and disassemble each candidate fully
import json
import ida_funcs, ida_ua, ida_bytes, ida_pro, ida_name, idc, idautils

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g48_candidates.json"
CAND = [0x145518FE0, 0x145518D50, 0x1451C8320, 0x1451CA3D0, 0x1451CB880]
results = {"status":"RUNNING","candidates":{},"errors":[]}

def name_of(ea): return ida_name.get_name(ea) or ""

for c in CAND:
    entry = {"ea":c,"name":name_of(c),"callers":[]}
    f = ida_funcs.get_func(c)
    if f: entry["range"]=[f.start_ea,f.end_ea]
    for x in idautils.XrefsTo(c):
        if x.type == 0x15 or x.type == 0x10:  # call direct/indirect near/far
            entry["callers"].append({"from":x.frm,"caller_func":name_of(ida_funcs.get_func(x.frm).start_ea if ida_funcs.get_func(x.frm) else None)})
    # also list other xref types
    results["candidates"][hex(c)] = entry

results["status"]="SUCCESS"
with open(OUT,"w",encoding="utf-8") as fh:
    json.dump(results,fh,indent=2,default=str)
print("COMPLETE")
ida_pro.qexit(0)
