"""g106_ca80_callerctx.py - dump full sub_14243CA80 (pack-init dispatcher),
decompile it + its callers, and show how the return value is used at each of
the 4 code call sites. Also verifies candidate code caves for the null-guard
trampoline (rcx==NULL).

Call sites (from g105 xrefs): 0x142432044, 0x14243ced6, 0x14243cefd, 0x14243cf70
"""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g106_ca80_callerctx.json"
CALL_SITES = [0x142432044, 0x14243ced6, 0x14243cefd, 0x14243cf70]
CA80 = 0x14243ca80
CAVES = [
    ("text_tail_00", 0x1463fc89b, 357),
    ("early_cc_223", 0x14008f521, 223),
]

import ida_funcs, ida_hexrays, idautils, idc  # noqa

res = {"status": "RUNNING", "ca80": {}, "callers": {}, "caves": {}, "errors": []}


def fname(ea):
    return ida_funcs.get_func_name(ea) or hex(ea)


def decompile(ea):
    try:
        cf = ida_hexrays.decompile(ea)
        return str(cf) if cf else None
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e


def dump_func(ea, label):
    f = ida_funcs.get_func(ea)
    if not f:
        res["errors"].append("%s: no func" % hex(ea))
        return
    ins = []
    addr = f.start_ea
    while addr < f.end_ea:
        nxt = idc.next_head(addr, f.end_ea)
        if nxt == idc.BADADDR:
            nxt = f.end_ea
        txt = idc.generate_disasm_line(addr, 0)
        ins.append((hex(addr), txt))
        addr = nxt
    res[label] = {
        "start": hex(f.start_ea), "end": hex(f.end_ea),
        "name": fname(ea), "insn": ins,
    }


def dump_window(site, label, before=0x30, after=0x60):
    ins = []
    start = site - before
    end = site + after
    addr = start
    while addr < end:
        nxt = idc.next_head(addr, end)
        if nxt == idc.BADADDR:
            nxt = end
        txt = idc.generate_disasm_line(addr, 0)
        ins.append((hex(addr), txt))
        addr = nxt
    f = ida_funcs.get_func(site)
    res["callers"][label] = {
        "site": hex(site), "func": fname(site),
        "func_start": hex(f.start_ea) if f else None,
        "func_end": hex(f.end_ea) if f else None,
        "window": ins,
        "decompile": decompile(f.start_ea) if f else None,
    }


def check_cave(name, start, length):
    e = {"candidate": name, "start": hex(start), "length": length, "bytes": None,
         "func": None, "xrefs": [], "prev_insn": None, "next_insn": None}
    f = ida_funcs.get_func(start)
    if f:
        e["func"] = [hex(f.start_ea), hex(f.end_ea), fname(f.start_ea)]
    e["prev_insn"] = idc.generate_disasm_line(idc.prev_head(start, start - 0x40), 0)
    nxt = start
    for _ in range(length + 4):
        nxt = idc.next_head(nxt, start + length + 16)
        if nxt == idc.BADADDR:
            break
    e["next_insn"] = idc.generate_disasm_line(nxt, 0) if nxt != idc.BADADDR else None
    for probe in (start, start + 8, start + length // 2, start + length - 1):
        for x in idautils.XrefsTo(probe, 0):
            e["xrefs"].append([hex(x.frm), hex(x.to), x.type, x.iscode])
        for x in idautils.XrefsFrom(probe, 0):
            e["xrefs"].append(["from", hex(x.frm), hex(x.to), x.type, x.iscode])
    res["caves"][name] = e


dump_func(CA80, "ca80_disasm")
res["ca80"]["decompile"] = decompile(CA80)

for site in CALL_SITES:
    dump_window(site, "call_%x" % site)

for name, start, length in CAVES:
    check_cave(name, start, length)

res["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("ANALYSIS_COMPLETE out=%s" % OUT)
import ida_pro  # noqa
ida_pro.qexit(0)