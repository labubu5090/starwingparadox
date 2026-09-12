import json, re, traceback
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76d_final.json"
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

sec={}
sec["tickinputmove_callers"]={"desc":"callers of TickInputMove","ea":"0x142257210","callers":callers(0x142257210)}

# name search for Chair/Demo/ChairOption/AgingFlag related across DB
namehits=[]
for ea,nm in idautils.Names():
    low=nm.lower()
    if any(k in low for k in ["chair","demoactor","getoption","agingflag","m_aging","sortiedash","seqaction","seqwait","demostate","attract"]):
        # only interesting class methods (contains '::' via mangled @)
        if "@" in nm or "chair" in low or "demoactor" in low or "aging" in low:
            namehits.append({"ea":hex(ea),"name":short(nm)})
sec["name_hits"]=namehits
results["sections"]["analysis"]=sec
results["status"]="SUCCESS"
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(results,f,indent=2,default=str)
print("G76D_DONE hits=%d errs=%d"%(len(namehits),len(results["errors"])))
import ida_pro; ida_pro.qexit(0)
