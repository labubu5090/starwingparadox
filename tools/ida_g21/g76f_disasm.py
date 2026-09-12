import json, re
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76f_disasm.json"
results={"errors":[]}
try:
    import ida_bytes, ida_funcs, idc, idautils, ida_name
except Exception as e:
    results["errors"].append(str(e))
    with open(OUT,"w",encoding="utf-8") as f: json.dump(results,f,indent=2,default=str)
    import ida_pro; ida_pro.qexit(1)

def disasm_range(start,end):
    lines=[]
    ea=start
    guard=0
    while ea<end and guard<1500:
        guard+=1
        d=idc.generate_disasm_line(ea,0) or ""
        b=ida_bytes.get_bytes(ea, idc.get_item_size(ea))
        lines.append((hex(ea), b.hex() if b else "", d))
        ea=idc.next_head(ea,end)
    return lines

FUNCS={
 "tickinputmove":0x142257210,
 "moveforward":0x1422455d0,
 "moveright":0x1422456b0,
 "cockpit_setinputmoveforward":0x142223510,
 "cockpit_beginplay":0x142122b60,
 "setinputtype":0x141dd9850,
}
out={}
for k,ea in FUNCS.items():
    f=ida_funcs.get_func(ea)
    if not f:
        out[k]={"start":hex(ea),"end":None,"error":"no func"}
        continue
    out[k]={"start":hex(f.start_ea),"end":hex(f.end_ea),"lines":disasm_range(f.start_ea,f.end_ea)}
results["funcs"]=out
with open(OUT,"w",encoding="utf-8") as fd:
    json.dump(results,fd,indent=2,default=str)
print("G76F_DONE errs=%d"%len(results["errors"]))
import ida_pro; ida_pro.qexit(0)
