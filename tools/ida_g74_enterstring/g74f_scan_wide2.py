import idaapi
import idautils
import idc
import ida_name
import ida_segment
import ida_bytes

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74f_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


def scan_seg2(seg, needle):
    hits = []
    start = seg.start_ea
    end = seg.end_ea
    CH = 0x400000
    data = b""
    base = None
    while start < end:
        size = min(CH, end - start)
        d = ida_bytes.get_bytes(start, size)
        if d is None:
            data = b""
            base = None
            start += size
            continue
        if base is None:
            base = start
        data += d
        start += size
        idx = 0
        while True:
            idx = data.find(needle, idx)
            if idx == -1:
                break
            hits.append(base + idx)
            idx += 1
        if len(data) > CH:
            drop = len(data) - CH
            data = data[drop:]
            base += drop
    return hits


try:
    literals = [
        "ACPP_ReadCardMain::SetReadCardMode [%s]",
        "readCardMode [%s] -> [%s]",
        "EnterPressed / readCardMode",
        "ACPP_ReadCardMain::EnterPressed",
        "isNesysOnline[%d]",
        "ACPP_ReadCardMain::OnNesysCompleteCardIncert [%s]",
        "NOT FOUND",
    ]
    segs = list(idautils.Segments())
    for lit in literals:
        w = lit.encode("utf-16-le")
        total = []
        for s in segs:
            seg = ida_segment.getseg(s)
            if seg.end_ea - seg.start_ea > 0x5000:
                total += scan_seg2(seg, w)
        log("## WIDE %s : %d hits" % (lit, len(total)))
        for ea in total[:120]:
            xrefs = list(idautils.XrefsTo(ea))
            n = "?"
            for x in xrefs[:1]:
                f = idaapi.get_func(x.frm)
                n = ida_name.get_name(f.start_ea) if f else "?"
            log("   wide @0x%X xrefs=%d first=%s" % (ea, len(xrefs), n))
except Exception as e:
    log("EXC:", repr(e))
finally:
    OUT.close()
    idc.qexit(0)