import idc, idaapi, ida_funcs, ida_bytes, idautils, traceback, os, time

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

def ensure_strlit(ea, length, stype):
    # create string item if not already
    cur = idc.get_str_type(ea)
    if cur in (None, idc.BADADDR):
        ida_bytes.create_strlit(ea, length, stype)

if os.path.exists(LOG):
    os.remove(LOG)
log("=== SCRIPT 1+2 (UTF-16 aware): SetReadCardMode log fn + callers ===")

try:
    rd_start = 0x1463FECF8
    dt_end = 0x149524000

    # ---- find target strings (UTF-16LE) ----
    pat_srcm = "SetReadCardMode [%s]".encode("utf-16le")
    pat_enter = "EnterPressed / readCardMode".encode("utf-16le")
    loc_srcm = scan_for(rd_start, dt_end, pat_srcm)
    loc_enter = scan_for(rd_start, dt_end, pat_enter)
    log("UTF16 'SetReadCardMode [%%s]' hits: %d" % len(loc_srcm))
    for ea in loc_srcm:
        log("  str 0x%X" % ea)
    log("UTF16 'EnterPressed / readCardMode' hits: %d" % len(loc_enter))
    for ea in loc_enter:
        log("  str 0x%X" % ea)

    targets = set(loc_srcm) | set(loc_enter)

    # ---- create string items so xref subsystem can resolve refs ----
    for ea in targets:
        ensure_strlit(ea, len(pat_srcm) if ea in loc_srcm else len(pat_enter), idc.STRTYPE_C_16)

    # ---- xrefs to each string -> logging functions (the SetReadCardMode body) ----
    log_funcs = {}
    for ea in sorted(targets):
        xr = list(idautils.XrefsTo(ea))
        log("Xrefs to string 0x%X: %d" % (ea, len(xr)))
        for x in xr:
            fs = func_start(x.frm)
            log("  frm=0x%X type=%d -> func 0x%X %s" % (x.frm, x.type, fs, func_name(fs)))
            if fs != idc.BADADDR:
                log_funcs[fs] = log_funcs.get(fs, 0) + 1

    if not log_funcs:
        log("No xrefs resolved from strings. Brute-force code scan for LEA refs...")
        t0 = time.time()
        # brute force: iterate all instructions in .text, check operand values
        ct = 0
        seg_ea = 0x140001000
        seg_end = 0x1463FD000
        ea = seg_ea
        while ea < seg_end and ea != idc.BADADDR:
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if v in targets:
                    fs = func_start(ea)
                    log("  0x%X('%s') operand%d = 0x%X (in func 0x%X %s)" % (
                        ea, idc.GetDisasm(ea)[:70], i, v, fs, func_name(fs)))
                    if fs != idc.BADADDR:
                        log_funcs[fs] = log_funcs.get(fs, 0) + 1
            ea = idc.next_head(ea, seg_end)
            ct += 1
        log("brute-force scanned %d insn in %.1fs" % (ct, time.time() - t0))

    log("")
    log("=== Logging function(s): %d ===" % len(log_funcs))
    for f in sorted(log_funcs):
        log("  0x%X %s" % (f, func_name(f)))

    # ---- disassemble logging function around the SRCm string ref to confirm ----
    log("")
    log("=== Disasm of logging funcs (confirm 'SetReadCardMode [%%s]' usage) ===")
    for f in sorted(log_funcs):
        fname = func_name(f)
        ce = ida_funcs.get_func(f)
        fend = ce.end_ea if ce else f + 0x200
        # find the instruction that loads 0x1478049D6 within this function
        ref_insn = None
        ea = f
        while ea < fend and ea != idc.BADADDR:
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if v in targets or v in loc_srcm:
                    ref_insn = ea
                    break
            if ref_insn:
                break
            ea = idc.next_head(ea, fend)
        log("  Func 0x%X %s ; string-ref insn: 0x%X" % (f, fname, ref_insn if ref_insn else 0))
        # disasm window: 8 before ref, 25 after
        win = []
        if ref_insn:
            e = ref_insn
            b = 0
            fs = func_start(ref_insn)
            while e > fs and b < 8:
                e = idc.prev_head(e, fs)
                if e == idc.BADADDR:
                    break
                win.append(e)
                b += 1
            win.reverse()
            win.append(ref_insn)
            e = ref_insn
            a = 0
            while e < fend and a < 30:
                e = idc.next_head(e, fend)
                if e == idc.BADADDR:
                    break
                win.append(e)
                a += 1
        for ea in win:
            log("    0x%X: %s" % (ea, idc.GetDisasm(ea)))

    # ---- xrefs TO logging function(s) = callers ----
    all_callers = []  # (call_ea, type, caller_func, caller_name, logfunc_f)
    for f in sorted(log_funcs):
        callers = [(x.frm, x.type) for x in idautils.XrefsTo(f)]
        log("")
        log("=== Xrefs to logging func 0x%X %s : %d ===" % (f, func_name(f), len(callers)))
        for cfa, xt in callers:
            cf = func_start(cfa)
            log("  call 0x%X type=%d from 0x%X %s" % (cfa, xt, cf, func_name(cf)))
            all_callers.append((cfa, xt, cf, func_name(cf), f))

    log("")
    log("=== Disasm windows around each call site ===")
    processed = 0
    for cfa, xt, cf, cn, lf in all_callers:
        if processed >= 40:
            log("...cap 40 reached")
            break
        log("")
        log("--- CALL 0x%X in func 0x%X %s (mode set = value passed to SetReadCardMode) ---" % (cfa, cf, cn))
        fs = func_start(cfa)
        ce = ida_funcs.get_func(cf)
        fend = ce.end_ea if ce else cfa + 0x300
        win = []
        e = cfa
        b = 0
        while e > fs and b < 60:
            e = idc.prev_head(e, fs)
            if e == idc.BADADDR:
                break
            win.append(e)
            b += 1
        win.reverse()
        win.append(cfa)
        e = cfa
        a = 0
        while e < fend and a < 20:
            e = idc.next_head(e, fend)
            if e == idc.BADADDR:
                break
            win.append(e)
            a += 1
        for ea in win:
            d = idc.GetDisasm(ea)
            m = idc.print_insn_mnem(ea)
            star = ""
            if ea == cfa:
                star = "   <<<< CALL"
            log("    0x%X: %s%s" % (ea, d, star))
            # annotate mode value going into dl / edx / dl if immediate
            for i in range(3):
                v = idc.get_operand_value(ea, i)[0] if isinstance(idc.get_operand_value(ea, i), tuple) else idc.get_operand_value(ea, i)
                if m in ("mov", "lea") and v == 0x16:
                    log("      ^^ mode=0x16 (PremissionOfflineNesys)")
                if m in ("mov", "lea") and v == 3:
                    log("      ^^ mode=3 (RequestPlayerLogin)")
        processed += 1

    log("")
    log("=== DONE ===")
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())