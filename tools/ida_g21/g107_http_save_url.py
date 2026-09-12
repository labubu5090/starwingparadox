"""g107_http_save_url.py - trace the game-data-save HTTP flow:
which URL/path the client builds for the end-of-battle GameDataSave
(UCPP_EndBattleSequenceComponent::BindHttpGameDataSaveData -> UHttpRequestTickable),
and what function produces MessageId 20 (UPlayingGameOnDedicatedServerWork error).
"""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g107_http_save_url.json"
TARGETS = [
    ("OnGameDataSaveMission_str", 0x146969228),
    ("BindHttpGameDataSave_str", 0x146ac4aa0),
    ("HttpGameData_str", 0x146af61cc),
    ("GameDataSave_str2", 0x146af6318),
]

import ida_funcs, ida_hexrays, idautils, idc, ida_bytes  # noqa

res = {"status": "RUNNING", "xref_sites": {}, "funcs": {}, "errors": []}


def fname(ea):
    return ida_funcs.get_func_name(ea) or hex(ea)


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        return str(cf) if cf else None
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e


def collect_strings(func_start, func_end):
    """Collect ascii string literals referenced from within a function."""
    out = {}
    addr = func_start
    while addr < func_end:
        nxt = idc.next_head(addr, func_end)
        if nxt == idc.BADADDR:
            nxt = func_end
        for dref in idautils.DataRefsFrom(addr):
            if dref in out:
                continue
            s = ida_bytes.get_strlit_contents(dref)
            if s:
                try:
                    out[dref] = s.decode("utf-8", "replace")
                except Exception:
                    out[dref] = repr(s)
        addr = nxt
    return out


def dump_window(site, label, before=0x40, after=0x80):
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
    f = ida_funcs.get_func(site)
    return {
        "site": hex(site), "func": fname(site),
        "func_start": hex(f.start_ea) if f else None,
        "func_end": hex(f.end_ea) if f else None,
        "window": ins,
        "decompile": decompile(f.start_ea) if f else None,
        "strings": collect_strings(f.start_ea, f.end_ea) if f else {},
    }


for label, ea in TARGETS:
    xs = []
    for x in idautils.XrefsTo(ea, 0):
        xs.append(x)  # keep raw ids for func lookup
    res["xref_sites"][label] = {
        "ea": hex(ea),
        "content": "%r" % ida_bytes.get_bytes(ea, 64),
        "xrefs": [[hex(x.frm), hex(x.to), x.type, x.iscode] for x in xs],
    }
    func, ctx = None, None
    for x in xs:
        if not isinstance(x.frm, int):
            continue
        f = ida_funcs.get_func(x.frm)
        if f:
            func = f.start_ea
            ctx = dump_window(x.frm, "x_%s_%x" % (label, x.frm))
            break
    if func:
        res["funcs"][label] = {
            "func": hex(func),
            "func_name": fname(func),
            "decompile": decompile(func),
            "strings": collect_strings(func, ida_funcs.get_func(func).end_ea),
            "context": ctx,
        }

res["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("ANALYSIS_COMPLETE out=%s" % OUT)
import ida_pro  # noqa
ida_pro.qexit(0)