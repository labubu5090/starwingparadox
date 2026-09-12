import idaapi
import idautils
import idc
import ida_name
import ida_ida
import ida_segment
import ida_bytes

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74b_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


def find_bytes_in_rodata(needle):
    hits = []
    seg = ida_segment.get_segm_by_name(".rdata")
    if not seg:
        return hits
    start = seg.start_ea
    end = seg.end_ea
    size = end - start
    data = ida_bytes.get_bytes(start, size)
    if data is None:
        return hits
    idx = data.find(needle)
    while idx != -1:
        hits.append(start + idx)
        idx = data.find(needle, idx + 1)
    return hits


try:
    needles = {
        "readCardMode": b"readCardMode",
        "EnterPressed": b"EnterPressed",
        "SetReadCardMode": b"SetReadCardMode",
        "isNesysOnline": b"isNesysOnline",
        "RequestPlayerLogin": b"RequestPlayerLogin",
        "PremissionOfflineNesys": b"PremissionOfflineNesys",
        "CardError": b"CardError",
    }
    for label, ndl in needles.items():
        hits = find_bytes_in_rodata(ndl)
        log("## %s : %d hits in .rdata" % (label, len(hits)))
        for ea in hits[:50]:
            xrefs = list(idautils.XrefsTo(ea))
            log("   data @0x%X xrefs=%d" % (ea, len(xrefs)))
            for x in xrefs[:8]:
                f = idaapi.get_func(x.frm)
                log("     xref 0x%X func=%s" % (x.frm, ida_name.get_name(f.start_ea) if f else "?"))
except Exception as e:
    log("EXC:", repr(e))
finally:
    OUT.close()
    idc.qexit(0)