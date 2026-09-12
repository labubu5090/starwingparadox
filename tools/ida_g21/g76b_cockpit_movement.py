import json
import traceback
import re

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76b_cockpit_movement.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_funcs
    import ida_name
    import ida_hexrays
    import idc
    import idautils
    import ida_bytes
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e)})
    results["status"] = "FATAL_IMPORT_ERROR"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    import ida_pro
    ida_pro.qexit(1)


def fname(ea):
    try:
        return ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or hex(ea)
    except Exception:
        return hex(ea)


def short(name):
    m = re.search(r"\?([^@]+)@", name or "")
    return m.group(1) if m else name


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


def callers(ea):
    out = []
    try:
        for x in idautils.XrefsTo(ea, 0):
            out.append({
                "from": hex(x.frm), "type": x.type,
                "func": hex(x.func_ea) if x.func_ea else None,
                "name": short(fname(x.func_ea if x.func_ea else x.frm)),
            })
    except Exception as e:
        out.append({"error": str(e)})
    return out


def get_addr(name_frag):
    for ea, nm in idautils.Names():
        if name_frag in nm:
            return ea, nm
    return None, None


TARGETS = [
    ("cockpit_tickcomponent", "UCPP_CockpitComponent::TickComponent", "0x142227bf0"),
    ("setinputmoveforward", "SetInputMoveForward", "0x142223510"),
    ("setinputmoveright", "SetInputMoveRight", "0x142223520"),
    ("moveinputmoveforward", "MoveInputMoveForward", "0x1422455d0"),
    ("moveinputmoveright", "MoveInputMoveRight", "0x1422456b0"),
    ("tickinputmove", "TickInputMove", "0x142257210"),
    ("setcameratype", "SetCameraType", "0x142082450"),
    ("setcameramode_engine", "APlayerCameraManager::SetCameraMode", "0x14447f340"),
    ("tickcheckchangeviewtarget", "TickCheckChangeViewTarget", "0x14201b280"),
    ("possess_battle", "Possess(battle controller)", "0x141f41e60"),
    ("onpossess", "PossessedBy", "0x144132ba0"),
    ("receivepossessed", "ReceivePossessed", "0x14465ce30"),
    ("setinputtype", "SetInputType(PlayerControllerAcr)", "0x141dd9850"),
    ("client_setcameramode", "ClientSetCameraMode_Implementation", "0x144466e70"),
    ("updateviewtarget", "UpdateViewTarget", "0x144484ab0"),
    ("assignviewtarget", "AssignViewTarget", "0x1444645c0"),
    ("moveinputmoveforward_2", "ButtonInputMove(controller?)", "0x1427dce20"),
    ("setinputmovefowardaxis", "SetInputMoveFowardAxis(controller)", "0x142018250"),
    ("setinputmoverightaxis", "SetInputMoveRightAxis(controller)", "0x142018260"),
    ("spawnplayercameramanager", "SpawnPlayerCameraManager", "0x144481010"),
]

sec = {}
for label, desc, ea_str in TARGETS:
    ea = int(ea_str, 16)
    entry = {
        "label": label, "desc": desc, "ea": ea_str,
        "name": short(fname(ea)),
        "callers": callers(ea),
        "decompiled": decompile(ea),
    }
    sec[label] = entry

results["sections"]["analysis"] = sec
results["sections"]["count"] = len(TARGETS)
results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("G76B_DONE status=%s count=%d errs=%d" % (results["status"], len(TARGETS), len(results["errors"])))
import ida_pro
ida_pro.qexit(0)
