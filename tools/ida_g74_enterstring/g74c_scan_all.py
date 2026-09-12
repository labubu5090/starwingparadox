import idaapi
import idautils
import idc
import ida_name
import ida_segment
import ida_bytes

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74c_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


def scan_seg(seg, needle):
    hits = []
    data = ida_bytes.get_bytes(seg.start_ea, seg.end_ea - seg.start_ea)
    if data is None:
        return hits
    idx = data.find(needle)
    while idx != -1:
        hits.append(seg.start_ea + idx)
        idx = data.find(needle, idx + 1)
    return hits


try:
    needles = [b"SetReadCardMode", b"readCardMode", b"EnterPressed / ", b"ContentsLog?",
               b"ACPP_ReadCardMain", b"isNesysOnline", b"RequestPlayerLogin", b"CardError"]
    segs = list(idautils.Segments())
    log("segments: %d" % len(segs))
    for s in segs:
        seg = ida_segment.getseg(s)
        log("  seg %s 0x%X..0x%X" % (idc.get_segm_name(s), s, seg.end_ea))
    for ndl in needles:
        total = []
        for s in segs:
            for ea in scan_seg(ida_segment.getseg(s), ndl):
                total.append(ea)
        log("## %s : %d hits" % (ndl.decode(), len(total)))
        for ea in total[:80]:
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