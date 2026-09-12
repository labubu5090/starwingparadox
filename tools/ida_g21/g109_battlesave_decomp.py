"""g109_battlesave_decomp.py - full decompile of the end-of-battle save host
and its callers, to find the IsSuccess==0 -> game-server-error branch.
"""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g109_battlesave_decomp.json"
SEEDS = [0x144B2B070, 0x141EF3A80]

import ida_funcs, ida_hexrays, idautils, idc, ida_bytes  # noqa

res = {"status": "RUNNING", "funcs": {}, "errors": []}


def fname(ea):
    return ida_funcs.get_func_name(ea) or hex(ea)


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        return str(cf) if cf else None
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e


def collect_strings(func_start, func_end):
    out = {}
    addr = func_start
    while addr < func_end:
        nxt = idc.next_head(addr, func_end)
        if nxt == idc.BADADDR:
            nxt = func_end
        for dref in idautils.DataRefsFrom(addr):
            if dref in out:
                continue
            raw = ida_bytes.get_bytes(dref, 64)
            if raw is None:
                continue
            s = raw.split(b"\x00")[0]
            if s and min(s) >= 0x20 and max(s) < 0x7f:
                try:
                    out[hex(dref)] = s.decode("ascii")
                except Exception:
                    pass
        addr = nxt
    return out


queue = [(ea, "seed") for ea in SEEDS]
seen = set()
for ea, tag in queue:
    if ea in seen:
        continue
    seen.add(ea)
    f = ida_funcs.get_func(ea)
    if not f:
        res["errors"].append("%s: no func" % hex(ea))
        continue
    entry = {
        "func": hex(f.start_ea),
        "func_end": hex(f.end_ea),
        "func_name": fname(f.start_ea),
        "tag": tag,
        "decompile": decompile(f.start_ea),
        "strings": collect_strings(f.start_ea, f.end_ea),
        "callers": [],
    }
    ins = []
    addr = f.start_ea
    while addr < f.end_ea:
        nxt = idc.next_head(addr, f.end_ea)
        if nxt == idc.BADADDR:
            nxt = f.end_ea
        ins.append((hex(addr), idc.generate_disasm_line(addr, 0)))
        addr = nxt
    entry["insn"] = ins
    for x in idautils.XrefsTo(f.start_ea, 0):
        entry["callers"].append([hex(x.frm), x.type, x.iscode])
        cf = ida_funcs.get_func(x.frm)
        if cf and cf.start_ea not in seen and len(seen) < 12:
            queue.append((cf.start_ea, "caller_of_%x" % f.start_ea))
    res["funcs"][hex(f.start_ea)] = entry

res["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("ANALYSIS_COMPLETE out=%s" % OUT)
import ida_pro  # noqa
ida_pro.qexit(0)