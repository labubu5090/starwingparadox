import idautils, idc, ida_search, ida_bytes, ida_name, ida_funcs, ida_xref

# Script 1: Find the SetReadCardMode logging function via the string.
# Uses idautils.Strings() for fast iteration.

results = []

found_ea = idc.BADADDR
matches = []
for s in idautils.Strings():
    if b"SetReadCardMode" in s.text:
        matches.append((s.ea, s.text))
        results.append("String at 0x%X: %s" % (s.ea, s.text.decode('ascii', errors='replace')))

if not matches:
    results.append("NO SetReadCardMode strings found via idautils.Strings()")
    # Fallback: targeted scan near 0x14781BE60
    for ea in range(0x14781BE00, 0x14781C200, 1):
        if ea % 16 == 0:
            t = idc.get_strlit_contents(ea)
            if t and b"SetReadCardMode" in t:
                matches.append((ea, t))
                results.append("(fallback) String at 0x%X: %s" % (ea, t.decode('ascii', errors='replace')))
    if not matches:
        for ea in range(0x14781BE00, 0x14781C200, 1):
            buf = idc.get_bytes(ea, 24)
            if buf and b"SetReadCardMode" in buf:
                results.append("Raw bytes at 0x%X contain 'SetReadCardMode': %s" % (ea, buf))
else:
    found_ea = matches[0][0]

results.append("---")
results.append("Found %d matching string(s)" % len(matches))

log_funcs = set()
for ea, t in matches:
    results.append("")
    results.append("=== Xrefs to string 0x%X ===" % ea)
    cnt = 0
    for xref in idautils.XrefsTo(ea):
        cnt += 1
        func_ea = ida_funcs.get_func_attr(xref.frm, idc.FUNCATTR_START)
        fname = idc.get_func_name(func_ea) if func_ea != idc.BADADDR else "<none>"
        results.append("  Xref from 0x%X (type=%d) => func 0x%X %s" % (xref.frm, xref.type, func_ea, fname))
        if func_ea != idc.BADADDR:
            log_funcs.add(func_ea)
    if cnt == 0:
        results.append("  No direct xrefs. Scanning code for refs to 0x%X..." % ea)
        tgt = ea
        for seg_ea in idautils.Segments():
            seg_name = idc.get_segm_name(seg_ea).lower()
            seg_end = idc.get_segm_end(seg_ea)
            if not ('code' in seg_name or 'text' in seg_name):
                continue
            ea2 = seg_ea
            while ea2 < seg_end and ea2 != idc.BADADDR:
                d = idc.GetDisasm(ea2)
                if ("%X" % tgt) in d.replace("0x", "").lower() or (hex(tgt) in d.lower()):
                    func_ea = ida_funcs.get_func_attr(ea2, idc.FUNCATTR_START)
                    fname = idc.get_func_name(func_ea) if func_ea != idc.BADADDR else "<none>"
                    results.append("  REF at 0x%X: %s => func 0x%X %s" % (ea2, d, func_ea, fname))
                    if func_ea != idc.BADADDR:
                        log_funcs.add(func_ea)
                ea2 = idc.next_head(ea2, seg_end)

results.append("")
results.append("=== Logging function(s): %d ===" % len(log_funcs))
for f in sorted(log_funcs):
    fname = idc.get_func_name(f) or "<unnamed>"
    results.append("  0x%X %s" % (f, fname))

results.append("")
results.append("=== Xrefs TO logging function(s) ===")
for f in sorted(log_funcs):
    fname = idc.get_func_name(f) or "<unnamed>"
    callers = []
    for xref in idautils.XrefsTo(f):
        cf = ida_funcs.get_func_attr(xref.frm, idc.FUNCATTR_START)
        cn = idc.get_func_name(cf) if cf != idc.BADADDR else "<none>"
        callers.append((xref.frm, cf, cn))
    results.append("")
    results.append("  Func 0x%X %s : %d callers" % (f, fname, len(callers)))
    for ca, cf, cn in callers:
        results.append("    call 0x%X from 0x%X %s" % (ca, cf, cn))

with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_rpl_shop.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(results))

print("Script 1 done. See ida_rpl_shop.txt")
for m in matches:
    print("  String at 0x%X: %s" % (m[0], m[1]))