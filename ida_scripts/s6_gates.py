import idc, ida_funcs, idautils, traceback, time

LOG = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_rpl_shop.txt"

def log(msg=""):
    with open(LOG, "a", encoding="ascii", errors="replace") as f:
        f.write(msg + "\n")

def func_start(ea):
    f = ida_funcs.get_func(ea)
    return f.start_ea if f else idc.BADADDR

def func_name(ea):
    n = idc.get_func_name(ea)
    return n if n else "<unnamed>"

def disasm_full(fea, maxinsn=200, mark=None):
    ce = ida_funcs.get_func(fea)
    if not ce:
        log("  NO FUNC at 0x%X" % fea)
        return
    log("== func 0x%X %s (0x%X-0x%X) ==" % (ce.start_ea, func_name(fea), ce.start_ea, ce.end_ea))
    ea = ce.start_ea
    n = 0
    while ea < ce.end_ea and ea != idc.BADADDR and n < maxinsn:
        d = idc.GetDisasm(ea)
        tag = ""
        if mark and ea in mark:
            tag = "   <<<< MARK"
        log("    0x%X: %s%s" % (ea, d, tag))
        n += 1
        ea = idc.next_head(ea, ce.end_ea)

log("")
log("=== SCRIPT 6: DrawNesysMessage callers + IsNesicaReceptionTime/RemainClosedShopTime ===")
t0 = time.time()
try:
    DM = 0x142F3FB70
    log("### Xrefs to DrawNesysMessage 0x%X ###" % DM)
    xr = list(idautils.XrefsTo(DM))
    log("  %d xrefs" % len(xr))
    for x in xr:
        fs = func_start(x.frm)
        log("   frm 0x%X type=%d -> func 0x%X %s" % (x.frm, x.type, fs, func_name(fs)))
    # also include data xrefs into vtable
    log("")
    log("### look for names: IsNesicaReceptionTime / RemainClosedShopTime ###")
    gate1 = None
    gate2 = None
    clo = 0x142F3FE40
    for ea, nm in idautils.Names():
        if not nm:
            continue
        low = nm.lower()
        if "isnesicareceptiontime" in low:
            log("  FOUND %s 0x%X" % (nm, ea))
            gate1 = ea
        if "remainclosedshoptime" in low:
            log("  FOUND %s 0x%X" % (nm, ea))
            gate2 = ea
    if gate1:
        disasm_full(gate1, 60)
    if gate2:
        disasm_full(gate2, 60)

    log("")
    log("### branch trigger into the closed-shop block (0x142F3FE00-0x142F3FE45) ###")
    ea = 0x142F3FE10
    while ea < 0x142F3FE50 and ea != idc.BADADDR:
        log("  0x%X: %s" % (ea, idc.GetDisasm(ea)))
        ea = idc.next_head(ea, 0x142F3FE50)

    log("")
    log("### a short look at DrawNesysMessage tail (0x142F40130-0x142F40160) ###")
    ea = 0x142F40130
    while ea < 0x142F40170 and ea != idc.BADADDR:
        log("  0x%X: %s" % (ea, idc.GetDisasm(ea)))
        ea = idc.next_head(ea, 0x142F40170)

    log("=== DONE SCRIPT 6 in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())