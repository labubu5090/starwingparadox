import idc, ida_funcs, idautils, traceback, time

LOG = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_rpl_shop.txt"

def log(msg=""):
    with open(LOG, "a", encoding="ascii", errors="replace") as f:
        f.write(msg + "\n")

def scan_bytes(start, end, pat, cap=100):
    res = []
    pos = start
    chunk = 0x200000
    while pos < end:
        size = min(chunk, end - pos)
        data = idc.get_bytes(pos, size)
        if data:
            off = 0
            while True:
                idx = data.find(pat, off)
                if idx < 0:
                    break
                res.append(pos + idx)
                if len(res) >= cap:
                    return res
                off = idx + 1
        pos += size
    return res

RD = 0x1463FECF8
DT = 0x149524000
A16 = lambda s: s.encode("utf-16le")

def func_start(ea):
    f = ida_funcs.get_func(ea)
    return f.start_ea if f else idc.BADADDR

def func_name(ea):
    n = idc.get_func_name(ea)
    return n if n else "<unnamed>"

def decode_wide(ea):
    out = []
    for i in range(0, 256, 2):
        b0 = idc.get_wide_byte(ea + i)
        b1 = idc.get_wide_byte(ea + i + 1)
        if b0 == 0 and b1 == 0:
            break
        ch = b0 | (b1 << 8)
        if 32 <= ch < 127 or ch in (0x3000,):
            out.append(chr(ch))
        else:
            out.append("?")
    return "".join(out)

log("")
log("")
log("=== SCRIPT 4: Tick switch map, CardError strings, shop strings, DrawNesysMessage ===")
t0 = time.time()
try:
    # ---- A) Tick dispatch map ----
    log("")
    log("### A) ACPP_ReadCardMain::Tick switch dispatch (from 0x142AE86F0) ###")
    ce = ida_funcs.get_func(0x142AE86F0)
    ea = ce.start_ea
    n = 0
    while ea < ce.end_ea and ea != idc.BADADDR and n < 180:
        d = idc.GetDisasm(ea)
        log("  0x%X: %s" % (ea, d))
        if "switch" in d.lower() and "cmp" in d:
            # dispatch value instruction
            pass
        if "jumptable" in d:
            break
        if ea > 0x142AE87A5 + 0x10:
            break
        n += 1
        ea = idc.next_head(ea, ce.end_ea)

    # ---- B) find CardError full strings & decode ----
    log("")
    log("### B) All UTF-16 strings containing 'CardError' (decoded) ###")
    seen = set()
    for ea in scan_bytes(RD, DT, A16("CardError"), 60):
        # find true start
        s = ea
        while s > RD + 4:
            b0 = idc.get_wide_byte(s - 2)
            b1 = idc.get_wide_byte(s - 1)
            if b0 == 0 and b1 == 0:
                break
            s -= 2
        if s in seen:
            continue
        seen.add(s)
        txt = decode_wide(s)
        nm = idc.get_name(s)
        xr = list(idautils.XrefsTo(s))
        log("  0x%X name='%s' xrefs=%d :: %s" % (s, nm if nm else "", len(xr), txt[:120]))
        for x in xr[:6]:
            fs = func_start(x.frm)
            log("      frm 0x%X func 0x%X %s" % (x.frm, fs, func_name(fs)))

    # ---- C) shop/business strings ----
    log("")
    log("### C) shop/business keyword strings (UTF-16 only) with full decode ###")
    kws = ["営業", "閉店", "休止", "営業時間", "店舗", "時間外", "start", "End"]
    for kw in kws:
        hits = scan_bytes(RD, DT, A16(kw), 40)
        log("[%s] hits=%d" % (kw, len(hits)))
        shown = 0
        for ea in hits:
            s = ea
            while s > RD + 4:
                b0 = idc.get_wide_byte(s - 2); b1 = idc.get_wide_byte(s - 1)
                if b0 == 0 and b1 == 0:
                    break
                s -= 2
            txt = decode_wide(s)
            nm = idc.get_name(s)
            xr = list(idautils.XrefsTo(s))
            log("    0x%X name='%s' xrefs=%d :: %s" % (s, nm if nm else "", len(xr), txt[:90]))
            for x in xr[:4]:
                fs = func_start(x.frm)
                log("        frm 0x%X func 0x%X %s" % (x.frm, fs, func_name(fs)))
            shown += 1
            if shown >= 8:
                log("    ... more")
                break

    # ---- D) symbols with Tenpo/ShopTime/Business/OpenTime/CloseTime ----
    log("")
    log("### D) symbols matching Tenpo/Shop/Business/Open/Close/TimeUp ###")
    cntn = 0
    for ea, nm in idautils.Names():
        if not nm:
            continue
        low = nm.lower()
        if any(k in low for k in ["tenpo", "shoptime", "businesstime", "biztime", "openhour", "closehour", "openhour", "timeup", "opentime", "closetime"]):
            fn = func_start(ea) if ida_funcs.get_func(ea) else idc.BADADDR
            log("  name 0x%X %s type=%s func=0x%X %s" % (ea, nm, idc.get_flags_name(idc.get_full_flags(ea)) if False else idc.get_flag(ea)>>0, fn, func_name(fn) if fn != idc.BADADDR else ""))
            cntn += 1
    log("  (%d symbols matched)" % cntn)

    # ---- E) DrawNesysMessage head ----
    log("")
    log("### E) UCPP_ErrorMessageManager::DrawNesysMessage 0x142F3FB70 (first 80 insn) ###")
    ce = ida_funcs.get_func(0x142F3FB70)
    if ce:
        ea = ce.start_ea
        n = 0
        while ea < ce.end_ea and ea != idc.BADADDR and n < 80:
            log("  0x%X: %s" % (ea, idc.GetDisasm(ea)))
            n += 1
            ea = idc.next_head(ea, ce.end_ea)

    log("=== DONE SCRIPT 4 in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())