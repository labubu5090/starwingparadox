import idc, ida_funcs, traceback

out = []
def A(fmt, *a):
    out.append(fmt % a if a else fmt)

try:
    f = ida_funcs.get_func(0x142ADCE40)
    if not f:
        A("no func at 0x142ADCE40")
    else:
        A("func 0x%X - 0x%X (len ~0x%X)" % (f.start_ea, f.end_ea, f.end_ea - f.start_ea))
        ea = f.start_ea
        n = 0
        while ea < f.end_ea and ea != idc.BADADDR and n < 400:
            d = idc.GetDisasm(ea)
            refs = []
            for i in range(6):
                v = idc.get_operand_value(ea, i)
                if 0x1463FECF8 <= v <= 0x148957000:
                    refs.append("op%d->0x%X" % (i, v))
            tag = ("   [%s]" % ",".join(refs)) if refs else ""
            A("  0x%X: %s%s" % (ea, d, tag))
            if idc.print_insn_mnem(ea) == "ret":
                n += 1
                if n > 2:
                    break
            n += 1
            ea = idc.next_head(ea, f.end_ea)
except Exception:
    A("EXCEPTION: %s", traceback.format_exc())

with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_test.txt", "w", encoding="ascii") as f:
    f.write("\n".join(out))