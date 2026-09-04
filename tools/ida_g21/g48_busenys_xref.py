# IDAPython: xrefs to bUseNesys BeginPlay string + disassemble writer function
import json
import ida_funcs
import ida_ua
import ida_bytes
import ida_pro
import idautils
import ida_name
import idc

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g48_busenys_xref.json"
results = {"status": "RUNNING", "xrefs": [], "functions": {}, "errors": []}

TARGET_STRINGS = {
    "bUseNesys_full": 0x1477F0CE0,
    "bUseNesys_short": 0x1477F0D1E,
    "SetReadCardMode": 0x1478049D6,
    "SetReadCardMode_short": 0x1478049B0,
}

def name_of_ea(ea):
    return ida_name.get_name(ea) or ""

seen_funcs = set()
try:
    for label, ea in TARGET_STRINGS.items():
        xr_list = []
        try:
            for xref in idautils.XrefsTo(ea):
                frm = xref.frm
                f = ida_funcs.get_func(frm)
                faddr = f.start_ea if f else None
                xr_list.append({"to": ea, "from": frm, "type": xref.type,
                                "func_start": faddr, "func_name": name_of_ea(faddr) if faddr else ""})
                if faddr:
                    seen_funcs.add(faddr)
        except Exception as e:
            results["errors"].append({"stage": "xref_"+label, "error": str(e)})
        results["xrefs"].append({"label": label, "ea": ea, "xrefs": xr_list})

    for faddr in seen_funcs:
        f = ida_funcs.get_func(faddr)
        lines = []
        cur = f.start_ea
        while cur < f.end_ea:
            insn = ida_ua.insn_t()
            length = ida_ua.decode_insn(insn, cur)
            if length == 0:
                lines.append({"ea": cur, "len": 1, "bytes": "", "text": "<undecodable>"})
                cur += 1
                continue
            mnem = insn.get_canon_mnem()
            ops = []
            for i in range(8):
                op = idc.print_operand(cur, i)
                if op:
                    ops.append(op)
                else:
                    break
            raw = ida_bytes.get_bytes(cur, length)
            bts = " ".join("%02X" % b for b in raw) if raw else ""
            lines.append({"ea": cur, "len": length, "bytes": bts,
                          "text": (mnem + " " + ", ".join(ops)).strip()})
            cur += length
        results["functions"][str(hex(faddr))] = {"name": name_of_ea(faddr), "faddr": faddr,
                                                 "fstart": f.start_ea, "fend": f.end_ea, "lines": lines}
    results["status"] = "SUCCESS"
except Exception as e:
    import traceback
    results["status"] = "ERROR"
    results["errors"].append({"error": str(e), "tb": traceback.format_exc()})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("ANALYSIS_COMPLETE")
ida_pro.qexit(0)
