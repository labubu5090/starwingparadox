# IDAPython: find bUseNesys BeginPlay string, its xrefs, and disassemble writers.
import json
import ida_funcs
import ida_ua
import ida_bytes
import ida_pro
import ida_search
import idautils
import ida_name
import idc

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g48_busenys_beginplay.json"
results = {"status": "RUNNING", "found_strings": [], "xrefs": [], "errors": []}

# The value shown in the log: "ACPP_ReadCardMain::BeginPlay / bUseNesys[%d]"
# Search for the distinctive substring "bUseNesys" in the binary listing.
TARGETS = [
    "ACPP_ReadCardMain::BeginPlay / bUseNesys[%d]",
    "bUseNesys[%d]",
    "ACPP_ReadCardMain::BeginPlay",
    "ACPP_ReadCardMain::SetReadCardMode [%s]",
]

try:
    import ida_strlist

    def name_of_ea(ea):
        return ida_name.get_name(ea) or ""

    for t in TARGETS:
        try:
            found = []
            # Walk all string items
            for s in idautils.Strings():
                try:
                    text = str(s)
                except Exception:
                    text = ""
                if t in text:
                    ea = s.ea
                    found.append({"ea": ea, "text": text[:200]})
            results["found_strings"].append({"target": t, "addrs": found})
        except Exception as e:
            results["errors"].append({"stage": "strings_"+t, "error": str(e)})

    # For each found string ea, gather code xrefs and disassemble functions
    seen_funcs = set()
    for grp in results["found_strings"]:
        for item in grp["addrs"]:
            ea = item["ea"]
            try:
                for xref in idautils.XrefsTo(ea):
                    frm = xref.frm
                    ftype = xref.type
                    f = ida_funcs.get_func(frm)
                    faddr = f.start_ea if f else None
                    xr = {"to": ea, "from": frm, "type": ftype,
                          "func_start": faddr,
                          "func_name": name_of_ea(faddr) if faddr else ""}
                    results["xrefs"].append(xr)
                    if faddr and faddr not in seen_funcs:
                        seen_funcs.add(faddr)
            except Exception as e:
                results["errors"].append({"stage": "xref_"+str(item["ea"]), "error": str(e)})

    # Disassemble each writer function
    funcs_out = {}
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
        funcs_out[str(hex(faddr))] = {"name": name_of_ea(faddr), "faddr": faddr,
                                      "fstart": f.start_ea, "fend": f.end_ea, "lines": lines}
    results["functions"] = funcs_out
    results["status"] = "SUCCESS"
except Exception as e:
    import traceback
    results["status"] = "ERROR"
    results["errors"].append({"error": str(e), "tb": traceback.format_exc()})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE")
ida_pro.qexit(0)
