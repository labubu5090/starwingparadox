import idc, ida_funcs, idautils, traceback, time

LOG = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_rpl_shop.txt"

def log(msg=""):
    with open(LOG, "a", encoding="ascii", errors="replace") as f:
        f.write(msg + "\n")

def decode_wide_escape(ea, max=200):
    out = []
    for i in range(0, max, 2):
        b0 = idc.get_wide_byte(ea + i)
        b1 = idc.get_wide_byte(ea + i + 1)
        if b0 == 0 and b1 == 0:
            break
        ch = b0 | (b1 << 8)
        if 32 <= ch < 127:
            out.append(chr(ch))
        else:
            out.append("\\u%04X" % ch)
    return "".join(out)

def func_start(ea):
    f = ida_funcs.get_func(ea)
    return f.start_ea if f else idc.BADADDR

def func_name(ea):
    n = idc.get_func_name(ea)
    return n if n else "<unnamed>"

log("")
log("=== SCRIPT 5: DrawNesysMessage + ChangeWidgetReadCard + shop string decode ===")
t0 = time.time()
try:
    log("### decode shop strings at 0x147B5AC18 / 0x147B5AFB0 ###")
    for ea in (0x147B5AC18, 0x147B5AFB0):
        log("  0x%X :: %s" % (ea, decode_wide_escape(ea, 140)))

    log("")
    log("### UCPP_ErrorMessageManager::DrawNesysMessage 0x142F3FB70 full ###")
    ce = ida_funcs.get_func(0x142F3FB70)
    if ce:
        ea = ce.start_ea
        n = 0
        while ea < ce.end_ea and ea != idc.BADADDR and n < 220:
            d = idc.GetDisasm(ea)
            tag = ""
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if v in (0x147B5AC18, 0x147B5AFB0):
                    tag = "   <<<< SHOP STRING"
            log("  0x%X: %s%s" % (ea, d, tag))
            n += 1
            ea = idc.next_head(ea, ce.end_ea)

    log("")
    log("### ACPP_ReadCardMain::ChangeWidgetReadCard 0x142AD75E0 full ###")
    ce = ida_funcs.get_func(0x142AD75E0)
    if ce:
        ea = ce.start_ea
        n = 0
        while ea < ce.end_ea and ea != idc.BADADDR and n < 260:
            d = idc.GetDisasm(ea)
            tag = ""
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if 0x140000000 < v < 0x149CB2000 and v != ce.start_ea:
                    pass
            if "Ret" in d or "case" in d:
                pass
            log("  0x%X: %s" % (ea, d))
            n += 1
            ea = idc.next_head(ea, ce.end_ea)

    # symbols scan (fixed)
    log("")
    log("### D2) symbols Tenpo/ShopTime/Business/OpenTime ###")
    cnt = 0
    for ea, nm in idautils.Names():
        if not nm:
            continue
        low = nm.lower()
        if any(k in low for k in ["tenpo", "shoptime", "businesstime", "biztime", "openhour", "timeup", "opentime", "closetime", "businesshour"]):
            fs = idc.BADADDR
            f = ida_funcs.get_func(ea)
            if f:
                fs = f.start_ea
            log("  name 0x%X %s func=%s" % (ea, nm, ("0x%X %s" % (fs, func_name(fs))) if fs != idc.BADADDR else "-"))
            cnt += 1
    log("  (%d symbols)" % cnt)

    log("=== DONE SCRIPT 5 in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())