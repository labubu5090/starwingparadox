# IDAPython: find function containing the 594h write sites and disassemble it fully
import json
import ida_funcs, ida_ua, ida_bytes, ida_pro, ida_name, idc

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g48_594writes.json"
EAS = [0x145518E3D, 0x145519138, 0x145519141, 0x1451C8330, 0x1451CA5AD, 0x1451CB901, 0x1451C77EB]
results = {"status":"RUNNING","funcs":{},"errors":[]}

def name_of(ea):
    return ida_name.get_name(ea) or ""

funcs_seen = {}
for ea in EAS:
    f = ida_funcs.get_func(ea)
    if not f:
        results["errors"].append({"ea":ea,"err":"no func"})
        continue
    fstart = f.start_ea
    if fstart in funcs_seen:
        funcs_seen[fstart].append(ea)
    else:
        funcs_seen[fstart] = [ea]

for fstart, hits in funcs_seen.items():
    f = ida_funcs.get_func(fstart)
    lines = []
    cur = f.start_ea
    while cur < f.end_ea:
        insn = ida_ua.insn_t()
        length = ida_ua.decode_insn(insn, cur)
        if length == 0:
            lines.append({"ea":cur,"len":1,"bytes":"","text":"<undecodable>"})
            cur += 1
            continue
        ops=[]
        for i in range(8):
            op=idc.print_operand(cur,i)
            if op: ops.append(op)
            else: break
        raw=ida_bytes.get_bytes(cur,length)
        bts=" ".join("%02X"%b for b in raw) if raw else ""
        lines.append({"ea":cur,"len":length,"bytes":bts,"text":(insn.get_canon_mnem()+" "+", ".join(ops)).strip()})
        cur += length
    results["funcs"][str(hex(fstart))] = {"name":name_of(fstart),"fstart":fstart,"fend":f.end_ea,
                                          "hit_eas":hits,"lines":lines}

results["status"]="SUCCESS"
with open(OUT,"w",encoding="utf-8") as fh:
    json.dump(results,fh,indent=2,default=str)
print("COMPLETE funcs", len(funcs_seen))
ida_pro.qexit(0)
