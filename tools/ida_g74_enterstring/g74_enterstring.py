import idaapi
import idautils
import idc
import ida_name

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


try:
    targets = ["readCardMode", "ACPP_ReadCardMain::EnterPressed", "SetReadCardMode [%s]"]
    for t in targets:
        log("### SEARCH STRING: %s" % t)
        found = []
        for s in idautils.Strings():
            st = str(s)
            if t in st:
                found.append((s.ea, st))
        log("  hits: %d" % len(found))
        for ea, st in found[:60]:
            xrefs = list(idautils.XrefsTo(ea))
            log("    str @0x%X '%s' xrefs=%d" % (ea, st, len(xrefs)))
            for x in xrefs[:12]:
                f = idaapi.get_func(x.frm)
                log("      xref 0x%X func=%s" % (x.frm, ida_name.get_name(f.start_ea) if f else "?"))
except Exception as e:
    log("EXC:", repr(e))
finally:
    OUT.close()
    idc.qexit(0)