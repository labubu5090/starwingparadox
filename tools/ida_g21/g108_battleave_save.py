"""g108_battleave_save.py - anchor the end-of-battle GameDataSave client logic.
Xrefs the FName-string EAs for BindHttpGameDataSaveData / OnGameDataSaveMission,
decompiles every referencing function, and dumps referenced string literals
(URL paths, error formats) to build a patch target for the -1000 failure path.
"""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g108_battleave_save.json"
ANCHORS = [
    ("BindHttpGameDataSaveData_a", 0x1494a2780),
    ("BindHttpGameDataSaveData_b", 0x1494d6290),
    ("OnGameDataSaveMission_a", 0x146969228),
    ("OnGameDataSaveMission_b", 0x14697e658),
]

import ida_funcs, ida_hexrays, idautils, idc, ida_bytes  # noqa

res = {"status": "RUNNING", "anchors": {}, "funcs": {}, "errors": []}


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


def dump_insn_window(site, before=0x40, after=0x80):
    ins = []
    start = site - before
    end = site + after
    addr = start
    while addr < end:
        nxt = idc.next_head(addr, end)
        if nxt == idc.BADADDR:
            nxt = end
        ins.append((hex(addr), idc.generate_disasm_line(addr, 0)))
        addr = nxt
    return ins


processed = set()
for label, ea in ANCHORS:
    if ea in processed:
        continue
    processed.add(ea)
    xs = []
    for x in idautils.XrefsTo(ea, 0):
        xs.append(x)
    res["anchors"][label] = {
        "ea": hex(ea),
        "content": "%r" % ida_bytes.get_bytes(ea, 96),
        "xrefs": [[hex(x.frm), hex(x.to), x.type, x.iscode] for x in xs],
    }
    func = None
    for x in xs:
        if not isinstance(x.frm, int):
            continue
        f = ida_funcs.get_func(x.frm)
        if f and f.start_ea not in processed:
            func = f.start_ea
            processed.add(func)
            res["funcs"]["x_%s_%x" % (label, x.frm)] = {
                "site": hex(x.frm),
                "func": hex(func),
                "func_end": hex(f.end_ea),
                "func_name": fname(func),
                "insn_window": dump_insn_window(x.frm),
                "decompile": decompile(func),
                "strings": collect_strings(func, f.end_ea),
            }

res["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("ANALYSIS_COMPLETE out=%s" % OUT)
import ida_pro  # noqa
ida_pro.qexit(0)