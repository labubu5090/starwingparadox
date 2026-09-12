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

def scan_for(start, end, pat, cap=200):
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

def disasm_full(fea, maxinsn=1200):
    ce = ida_funcs.get_func(fea)
    if not ce:
        log("  NO FUNC at 0x%X" % fea)
        return
    log("== full func 0x%X %s (0x%X-0x%X) ==" % (ce.start_ea, func_name(fea), ce.start_ea, ce.end_ea))
    ea = ce.start_ea
    n = 0
    while ea < ce.end_ea and ea != idc.BADADDR and n < maxinsn:
        d = idc.GetDisasm(ea)
        m = idc.print_insn_mnem(ea)
        tag = ""
        if m == "call":
            tgt = idc.get_operand_value(ea, 0)
            nm = idc.get_name(tgt, 0)
            if nm and "SetNextMode" in nm:
                tag = "    <<<< SETMODE CALL"
            elif nm and "SetReadCardMode" in nm:
                tag = "    <<<< SETREADMODE CALL"
        # annotate immediate mode setup right before setmode calls
        if m == "mov" and tag == "":
            for i in range(2):
                v = idc.get_operand_value(ea, i)
                disp = idc.print_operand(ea, i)
                if "dl" in disp or "edx" in disp or "rcx" in disp:
                    if 0 <= v <= 0x20 and "mov" in d:
                        log("    0x%X: %s    [mode=%X]" % (ea, d, v))
                        tag = "~"
                        break
        log("    0x%X: %s%s" % (ea, d, tag))
        n += 1
        ea = idc.next_head(ea, ce.end_ea)

def show_mode(call_ea):
    # walk back ~12 instrs to find last mov dl/edx <imm>
    fs = func_start(call_ea)
    e = call_ea
    b = 0
    while e > fs and b < 12:
        e = idc.prev_head(e, fs)
        if e == idc.BADADDR:
            break
        m = idc.print_insn_mnem(e)
        if m == "mov":
            for i in range(2):
                disp = idc.print_operand(e, i)
                if disp in ("dl", "edx", "cl", "ecx", "r8d"):
                    v = idc.get_operand_value(e, i)
                    if 0 <= v <= 0x30:
                        return (e, m, idc.GetDisasm(e), v)
        b += 1
    return None

log("")
log("")
log("=== SCRIPT 3: inspect OnNesys* handlers + mode values at SetNextMode call sites ===")
t0 = time.time()

try:
    targets = [
        0x142AE0030,  # OnNesysCompleteCardIncert
        0x142AE03D0,  # OnNesysCompleteCardReissue
        0x142AE0760,  # OnNesysCompleteCardReissueTest
        0x142AE0B00,  # OnNesysCompleteCardStatus
        0x142AE1BF0,  # OnReceivePlayerProfileLoad
    ]
    for t in targets:
        log("")
        disasm_full(t)

    log("")
    log("### Summary: SetNextMode call-site modes in OnNesys* handlers ###")
    # find all SetNextMode calls inside each target function and print the module const
    snm = 0x142AE4190
    for t in targets:
        ce = ida_funcs.get_func(t)
        if not ce:
            continue
        log("")
        log("Func 0x%X %s:" % (t, func_name(t)))
        xr = [x.frm for x in idautils.XrefsTo(snm)]
        for ca in xr:
            if ca >= ce.start_ea and ca < ce.end_ea:
                info = show_mode(ca)
                if info:
                    e, m, d, v = info
                    log("  call 0x%X  mode-reg set at 0x%X: %s  -> mode=%s" % (ca, e, d, v))
                else:
                    log("  call 0x%X  mode-reg: <not found in last 12 instrs>" % ca)

    log("")
    log("### Shop strings (UTF-16 only) + CardError context ###")
    for kw in ["営業時間", "閉店", "休止", "営業", "SHOP", "shop time over", "ShopClose", "TimeUp", "timeover"]:
        h16 = scan_for(RD, DT, A16(kw), 40)
        log("[kw] '%s' utf16=%d" % (kw, len(h16)))
        for ea in h16[:15]:
            nm = idc.get_name(ea)
            ctx = idc.get_bytes(ea - 8, 80)
            disp = "".join(chr(b) if 32 <= b < 127 else "." for b in ctx) if ctx else ""
            log("    0x%X name='%s' ctx='%s'" % (ea, nm if nm else "", disp))
            xr = list(idautils.XrefsTo(ea))
            if xr:
                log("      xrefs=%d" % len(xr))
                for x in xr[:10]:
                    fs = func_start(x.frm)
                    log("        frm 0x%X -> func 0x%X %s" % (x.frm, fs, func_name(fs)))
    log("")
    log("### CardError enum-name strings context ###")
    for ea in scan_for(RD, DT, A16("CardError"), 60):
        nm = idc.get_name(ea)
        ctx = idc.get_bytes(ea - 4, 96)
        disp = "".join(chr(b) if 32 <= b < 127 else "." for b in ctx) if ctx else ""
        xr = list(idautils.XrefsTo(ea))
        log("  CFG 0x%X name='%s' ctx='%s' xrefs=%d" % (ea, nm if nm else "", disp, len(xr)))
        for x in xr[:6]:
            fs = func_start(x.frm)
            log("      frm 0x%X func 0x%X %s" % (x.frm, fs, func_name(fs)))

    log("=== DONE in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())