import idautils
import idaapi
import ida_funcs
import ida_name
import ida_hexrays
import json
import sys


def main():
    out = {}
    out["sections"] = {}
    out["sections"]["names"] = []
    wanted = set()
    readnames = {}
    for ea, name in idautils.Names():
        if "RoboPreset" in name or "MechaPreset" in name or "UserCharCustom" in name:
            readnames[ea] = name
            out["sections"]["names"].append({"ea": hex(ea), "name": name})
            if "RoboPreset@FCPP" in name or "RoboPresetPartList@FCPP" in name or "SaveDataToJsonObject" in name and "RoboPreset" in name or "ReceiveHttpGameDataLoadDelegate_UserCharCustom" in name or "MechaPresetInfoList" in name or "MechaPresetPartInfoList" in name:
                wanted.add(ea)
    out["sections"]["decompiled"] = []
    if idaapi.IDA_SDK_VERSION < 900:
        for ea in sorted(wanted):
            fn = ida_funcs.get_func(ea)
            if not fn:
                continue
            decomp = ida_hexrays.decompile(fn.start_ea)
            text = str(decomp) if decomp else None
            out["sections"]["decompiled"].append({"name": name_for(ea, readnames), "ea": hex(ea), "decompiled": text, "len": len(text) if text else 0})
    else:
        for ea in sorted(wanted):
            fn = ida_funcs.get_func(ea)
            if not fn:
                continue
            try:
                cfunc = ida_hexrays.decompile(fn.start_ea)
                sv = cfunc.get_pseudocode()
                text = "\n".join(l.line for l in sv)
            except Exception as excp:
                text = None
            out["sections"]["decompiled"].append({"name": name_for(ea, readnames), "ea": hex(ea), "decompiled": text, "len": len(text) if text else 0})
    open_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g77e_robopreset_serialize.json"
    json.dump(out, open(open_path, "w", encoding="utf-8"), indent=1)


def name_for(ea, readnames):
    nm = ida_name.get_name(ea)
    if nm:
        return nm
    return readnames.get(ea, hex(ea))


main()