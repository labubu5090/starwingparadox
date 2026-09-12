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

RD = 0x1463FECF8
DT = 0x149524000
TXS = 0x140001000
TXE = 0x1463FD000

def find_prefix(prefix, label, cap=50):
    hits = scan_for(RD, DT, prefix, cap)
    log("[str] %s: %d raw hit(s)" % (label, len(hits)))
    for ea in hits[:20]:
        nm = idc.get_name(ea)
        log("   start 0x%X name='%s'" % (ea, nm if nm else ""))
    return hits

def create_string(ea, size):
    if idc.get_str_type(ea) in (None, idc.BADADDR) or idc.get_str_type(ea) is None:
        ida_bytes.create_strlit(ea, size, idc.STRTYPE_C_16)

def resolve_refs(ea, label, create_len=80):
    # create string item so xrefs register; if name exists already it may be auto
    if create_len:
        create_string(ea, create_len)
    nm = idc.get_name(ea)
    xr = list(idautils.XrefsTo(ea))
    log("== refs to %s 0x%X (name='%s'): %d ==" % (label, ea, nm if nm else "", len(xr)))
    for x in xr:
        fs = func_start(x.frm)
        log("   frm=0x%X type=%d -> func 0x%X %s" % (x.frm, x.type, fs, func_name(fs)))
    return xr

def disasm_window(center, back=70, fwd=25):
    fs = func_start(center)
    ce = ida_funcs.get_func(center)
    fend = ce.end_ea if ce else center + 0x300
    win = []
    e = center
    b = 0
    while e > fs and b < back:
        e = idc.prev_head(e, fs)
        if e == idc.BADADDR:
            break
        win.append(e)
        b += 1
    win.reverse()
    win.append(center)
    e = center
    a = 0
    while e < fend and a < fwd:
        e = idc.next_head(e, fend)
        if e == idc.BADADDR:
            break
        win.append(e)
        a += 1
    return win

def disasm_call_site(call_ea):
    cf = func_start(call_ea)
    log("--- call 0x%X in func 0x%X %s ---" % (call_ea, cf, func_name(cf)))
    if cf == idc.BADADDR:
        return
    win = disasm_window(call_ea, 60, 20)
    for ea in win:
        d = idc.GetDisasm(ea)
        m = idc.print_insn_mnem(ea)
        star = "  <<<< CALL" if ea == call_ea else ""
        log("    0x%X: %s%s" % (ea, d, star))
        if m in ("mov", "lea"):
            for i in range(3):
                v = idc.get_operand_value(ea, i)
                if v == 0x16:
                    log("        ^ mode=0x16 (PremissionOfflineNesys)")
                if v == 3:
                    log("        ^ mode=3 (RequestPlayerLogin)")
                if v == 1:
                    log("        ^ mode=1")
                if v == 5:
                    log("        ^ mode=5")

if os.path.exists(LOG):
    os.remove(LOG)
t0 = time.time()
log("=== SCRIPT 2: exact string starts -> logging functions -> callers ===")
A16 = lambda s: s.encode("utf-16le")
A = lambda s: s.encode("ascii")

try:
    # ---- 1) find exact string starts ----
    log ("")
    log ("######## STEP 1: find exact string starts ########")
    srcm_hits = find_prefix(A16("ACPP_ReadCardMain::SetReadCardMode"), "ACPP_ReadCardMain::SetReadCardMode", 50)
    setn_hits = find_prefix(A16("ACPP_ReadCardMain::SetNextMode"), "ACPP_ReadCardMain::SetNextMode", 50)
    enter_hits = find_prefix(A16("ACPP_ReadCardMain::EnterPressed / readCardMode"), "ACPP_ReadCardMain::EnterPressed / readCardMode", 50)

    targets = {}
    if srcm_hits:
        targets["SetReadCardMode_fmt"] = srcm_hits[0]
    if setn_hits:
        targets["SetNextMode_fmt"] = setn_hits[0]

    # ---- 2) resolve refs to the two format strings ----
    log("")
    log("######## STEP 2: code refs to format strings -> SetReadCardMode / SetNextMode functions ########")
    res = {}
    for k, ea in list(targets.items()):
        xr = resolve_refs(ea, k, create_len=None)
        res[k] = xr

    # SetReadCardMode function = func containing the format-string ref
    srcm_funcs = set()
    for x in res.get("SetReadCardMode_fmt", []):
        fs = func_start(x.frm)
        if fs != idc.BADADDR:
            srcm_funcs.add(fs)
    setn_funcs = set()
    for x in res.get("SetNextMode_fmt", []):
        fs = func_start(x.frm)
        if fs != idc.BADADDR:
            setn_funcs.add(fs)

    log("SetReadCardMode log-format funcs: %s" % ["0x%X %s" % (f, func_name(f)) for f in srcm_funcs])
    log("SetNextMode log-format funcs: %s" % ["0x%X %s" % (f, func_name(f)) for f in setn_funcs])

    # ---- 3) callers of SetReadCardMode func ----
    log("")
    log("######## STEP 3: callers of SetReadCardMode function(s) ########")
    for f in sorted(srcm_funcs):
        callers = [(x.frm, x.type) for x in idautils.XrefsTo(f)]
        log("=== Xrefs to SetReadCardMode func 0x%X %s : %d ===" % (f, func_name(f), len(callers)))
        for cfa, xt in callers:
            log("   call 0x%X type=%d from func 0x%X %s" % (cfa, xt, func_start(cfa), func_name(func_start(cfa))))

        # disassemble each call site window
        for cfa, xt in callers[:50]:
            log("")
            disasm_call_site(cfa)
        if len(callers) > 50:
            log("... %d more callers not disassembled" % (len(callers) - 50))

    # same shallow for SetNextMode func
    log("")
    log("######## STEP 3b: callers of SetNextMode function(s) ########")
    for f in sorted(setn_funcs):
        callers = [(x.frm, x.type) for x in idautils.XrefsTo(f)]
        log("=== Xrefs to SetNextMode func 0x%X %s : %d ===" % (f, func_name(f), len(callers)))
        for cfa, xt in callers[:60]:
            log("   call 0x%X type=%d from func 0x%X %s" % (cfa, xt, func_start(cfa), func_name(func_start(cfa))))

    # ---- 4) mode-name strings & CardError ----
    log("")
    log("######## STEP 4: CardError / mode name strings ########")
    for kw in ["CardError", "RequestPlayerLogin", "PremissionOfflineNesys", "CardRead", "ReadWait", "WaitCard"]:
        h16 = scan_for(RD, DT, A16(kw), 20)
        h8 = scan_for(RD, DT, A(kw), 20)
        log("[kw] %s : utf16=%d ascii=%d" % (kw, len(h16), len(h8)))
        for ea in (h16 + h8)[:8]:
            nm = idc.get_name(ea)
            log("   0x%X name='%s'" % (ea, nm if nm else ""))

    # ---- 5) shop strings ----
    log("")
    log("######## STEP 5: shop strings ########")
    shop_kws = ["shop", "Shop", "SHOP", "closed", "close", "time over", "営業", "閉店", "休止", "営業時間", "business"]
    for kw in shop_kws:
        h16 = scan_for(RD, DT, A16(kw), 30)
        h8 = scan_for(RD, DT, A(kw), 30)
        log("[shop] '%s' : utf16=%d ascii=%d" % (kw, len(h16), len(h8)))
        for ea in (h16 + h8)[:10]:
            nm = idc.get_name(ea)
            log("   0x%X name='%s'" % (ea, nm if nm else ""))
            if nm:
                # show resolved refs for named items
                xr = list(idautils.XrefsTo(ea))
                if xr:
                    log("     refs: %d" % len(xr))
                    for x in xr[:12]:
                        fs = func_start(x.frm)
                        log("       frm=0x%X func 0x%X %s" % (x.frm, fs, func_name(fs)))

    log("")
    log("=== DONE in %.1fs ===" % (time.time() - t0))
except Exception:
    log("EXCEPTION: %s" % traceback.format_exc())