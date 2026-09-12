import idaapi
import idautils
import idc
import ida_name
import ida_xref
import ida_bytes
import ida_funcs

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74g_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


def readable(ea, n=64):
    data = ida_bytes.get_bytes(ea, n * 2)
    if not data:
        return "?"
    s = data.decode("utf-16-le", errors="replace")
    return repr(s[:n])


try:
    targets = [0x14781BE60, 0x14781BE86, 0x14781BEDC, 0x1478049B0, 0x1477C6A0C]
    for t in targets:
        log("### STRING @0x%X = %s" % (t, readable(t, 70)))
        xrefs = list(idautils.XrefsTo(t))
        log("  code xrefs: %d" % len(xrefs))
        for x in xrefs:
            f = idaapi.get_func(x.frm)
            fname = ida_name.get_name(f.start_ea) if f else "?"
            log("    xref 0x%X  func=0x%X %s  type=%s" % (x.frm, f.start_ea if f else 0, fname, x.type))
            if f:
                log("      disasm:" + idc.generate_disasm_line(f.start_ea, 0))
except Exception as e:
    log("EXC:", repr(e))
finally:
    OUT.close()
    idc.qexit(0)