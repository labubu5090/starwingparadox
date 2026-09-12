import idc, traceback
out = []
def A(fmt, *a):
    out.append(fmt % a if a else fmt)
try:
    # dump raw UTF16 bytes before the hits to find full string start
    for base in (0x1478049D6, 0x14781BE86):
        A("== Before string hit 0x%X ==" % base)
        start = base - 0x40
        data = idc.get_bytes(start, 0x40 + 0x60)
        if data:
            # render as printable or escaped
            s = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
            A("  raw: %s" % s)
            # find true string start (align before base where bytes form a null-terminated wide string)
            tstart = base
            for i in range(base-2, start-1, -2):
                hi = data[i - start + 1] if (i - start + 1) < len(data) else 0
                lo = data[i - start]
                ch = (hi << 8) | lo
                if ch == 0:
                    tstart = i + 2
                    break
            A("  approx string start: 0x%X" % tstart)
            A("  full target after start/decoded: %s" % "".join(
                chr(0x100*data[j+1-start]+data[j-start]) if data[j+1-start] < 0x80 else '?' for j in range(tstart, base+60, 2)))
    A("")
    # test get_operand_value on known snippet EnterPressed 0x142ADCE40
    A("== EnterPressed snippet operand values ==")
    ea = 0x142ADCE40
    for k in range(20):
        d = idc.GetDisasm(ea)
        vals = [idc.get_operand_value(ea, i) for i in range(6)]
        A("  0x%X: %-60s opvalues=%s" % (ea, d, vals))
        ea = idc.next_head(ea, ea + 0x20000)
        if ea == idc.BADADDR:
            break
    A("")
    # check if get_bytes of .text near a known LEA... scan for old-style 'mov rdx' near string? test strtype
    A("strtype at 0x1478049D6: %s" % (idc.get_str_type(0x1478049D6)))
    A("strtype at 0x14781BE86: %s" % (idc.get_str_type(0x14781BE86)))
    # what does get_strlit_contents return now?
    A("get_strlit_contents(0x1478049D6): %r" % idc.get_strlit_contents(0x1478049D6))
    A("get_strlit_contents(0x14781BE86): %r" % idc.get_strlit_contents(0x14781BE86))
except Exception:
    A("EXCEPTION: %s", traceback.format_exc())
with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_test.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(out))