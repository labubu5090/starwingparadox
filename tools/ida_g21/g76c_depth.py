import json
import traceback
import re

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76c_depth.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs, ida_name, ida_hexrays, idc, idautils, ida_bytes
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e)})
    with open(OUT,"w",encoding="utf-8") as f:
        json.dump(results,f,indent=2,default=str)
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
            out.append({"func":hex(x.func_ea) if x.func_ea else None,
                        "name":short(fname(ea2)),"from":hex(x.frm)})
    except Exception as e: out.append({"error":str(e)})
    return out

TARGETS=[
 ("cockpit_tickcomponent","UCPP_CockpitComponent::TickComponent","0x142227bf0"),
 ("controller_tickcomponent","TickComponent(0x141f44ec0)","0x141f44ec0"),
 ("updateaging","UpdateAging","0x1423c0c20"),
 ("move_respawn_sequence","MoveRespawnSequence","0x142038760"),
 ("move_ai_respawn_sequence","MoveAiRespawnSequence","0x142035590"),
 ("spawn_aging_ai","SpawnAgingAiController","0x1422550c0"),
 ("buttoninputmove","ButtonInputMove","0x1427dce20"),
 ("setinputmovefowardaxis","SetInputMoveFowardAxis(CameraComponent)","0x142018250"),
 ("setinputtypecallers","SetInputType callers","0x141dd9850"),
 ("possess_battle","Possess(controller)","0x141f41e60"),
 ("receivepossessed","PossessedBy","0x144132ba0"),
 ("characterinit_possess","ACPP_CharacterEvent possessed?","0x1420c5210"),
]
sec={}
for label,desc,a in TARGETS:
    ea=int(a,16)
    sec[label]={"label":label,"desc":desc,"ea":a,"name":short(fname(ea)),
                "callers":callers(ea),"decompiled":decompile(ea)}
results["sections"]["analysis"]=sec
results["status"]="SUCCESS"
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(results,f,indent=2,default=str)
print("G76C_DONE count=%d errs=%d"%(len(TARGETS),len(results["errors"])))
import ida_pro; ida_pro.qexit(0)
