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

def disasm(fea, a, b, mark=None):
    ce = ida_funcs.get_func(fea)
    fend = ce.end_ea if ce else fea + b
    ea = fea
    n = 0
    while ea < fend and ea != idc.BADADDR and n < b:
        d = idc.GetDisasm(ea)
        tag = "   <<<< MARK" if (mark and ea in mark) else ""
        log("    0x%X: %s%s" % (ea, d, tag))
        n += 1
        ea = idc.next_head(ea, fend)

log("")
log("=== SCRIPT 7: GetShopMinutes/GetNowMinutes + ErrorMessageManager::Tick + ReadCardMode enum ===")
t0 = time.time()
try:
    for nmq in ["getshopminutes", "getnowminutes"]:
        for ea, nm in idautils.Names():
            if not nm:
                continue
            if nmq in nm.lower():
                log("FOUND %s 0x%X" % (nm, ea))
                disasm(ea, 0, 90)
                log("")

    log("### UCPP_ErrorMessageManager::Tick 0x142F53640 (first 90) ###")
    disasm(0x142F53640, 0, 90)
    log("")

    log("### ReadCardMode UEnum names (from 0x142B17C00 Z_Construct_UEnum_OutGameModule_ReadCardMode) ###")
    ce = ida_funcs.get_func(0x142B17C00)
    if ce:
        seen = set()
        ea = ce.start_ea
        n = 0
        while ea < ce.end_ea and ea != idc.BADADDR and n < 400:
            d = idc.GetDisasm(ea)
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if 0x1463FECF8 < v < 0x148957000:
                    nm = idc.get_name(v)
                    if nm and v not in seen and ("ReadCardMa" in idc.get_strlit_contents(v).decode('ascii','replace') if idc.get_strlit_contents(v) else False):
                        seen.add(v)
                        log("  0x%X -> str 0x%X name='%s'" % (ea, v, nm))
            n += 1
            ea = idc.next_head(ea, ce.end_ea)

    log("=== DONE SCRIPT 7 in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())