import json, re, traceback
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76e_demo.json"
results={"status":"RUNNING","sections":{},"errors":[]}
try:
    import ida_funcs, ida_name, ida_hexrays, idc, idautils, ida_bytes
except Exception as e:
    results["errors"].append(str(e))
    import ida_pro; ida_pro.qexit(1)
def fname(ea):
    try: return ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or hex(ea)
    except Exception: return hex(ea)
def short(name):
    m=re.search(r"\?([^@]+)@",name or "")
    return m.group(1) if m else name
def decompile(ea):
    try:
        cf=ida_hexrays.decompile(ea)
        if cf: return str(cf)
    except Exception as e: return "DECOMPILE_ERR: %s"%e
    return None
def callers(ea):
    out=[]
    try:
        for x in idautils.XrefsTo(ea,0):
            ea2=x.func_ea if x.func_ea else x.frm
            out.append({"func":hex(x.func_ea) if x.func_ea else None,"name":short(fname(ea2)),"from":hex(x.frm)})
    except Exception as e: out.append({"error":str(e)})
    return out
TARGETS=[
 ("setdemoactor","ACPP_CharacterEvent::SetDemoActor","0x1421002a0"),
 ("resetdemostate","ResetDemoState","0x1442378a0"),
 ("getoption_chair","GetOption_Chair","0x142e6c750"),
 ("getoption","GetOption base","0x142e6c670"),
 ("seqaction","ACPP_CharacterEvent::SeqAction","0x1420e0ff0"),
 ("seqwait","ACPP_CharacterEvent::SeqWait","0x142324610"),
 ("demotick","ACPP_BumDemoActor::Tick","0x1429cb3a0"),
 ("changedemocamera","ACPP_BumDemoActor::ChangeDemoCamera","0x1429b73c0"),
]
sec={}
for label,desc,a in TARGETS:
    ea=int(a,16)
    sec[label]={"desc":desc,"ea":a,"name":short(fname(ea)),"callers":callers(ea),"decompiled":decompile(ea)}
results["sections"]["analysis"]=sec
results["status"]="SUCCESS"
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(results,f,indent=2,default=str)
print("G76E_DONE errs=%d"%len(results["errors"]))
import ida_pro; ida_pro.qexit(0)
