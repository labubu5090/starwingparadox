import idaapi
import idautils
import idc
import ida_name
import ida_segment
import ida_bytes

OUT = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\g74d_out.txt", "w", encoding="utf-8")


def log(*args):
    OUT.write(" ".join(str(a) for a in args) + "\n")


def scan_seg_chunked(seg, needle):
    hits = []
    start = seg.start_ea
    end = seg.end_ea
    CH = 0x400000
    buf = b""
    prev_end = None
    while start < end:
        size = min(CH, end - start)
        d = ida_bytes.get_bytes(start, size)
        if d is None:
            start += size
            continue
        buf += d
        if len(buf) >= len(needle):
            # consume buf in windows to find all needle occurrences
            idx = buf.find(needle)
            while idx != -1:
                hits.append((start - (len(buf) - size)) + idx
                            if False else start - (len(buf) - size) + idx)
                # track absolute address carefully
                idx = buf.find(needle, idx + 1)
        # keep only tail
        keep = min(len(buf), len(needle) + 4096)
        buf = buf[-keep:]
        abs_base = start - (len(buf))
        start += size
    return hits


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
            trim = len(data) - CH + 4096
            keep = (len(needle) + 4096) if False else (CH)
            # keep last CH bytes aligned to absolute addr
            drop = len(data) - CH
            data = data[drop:]
            base += drop
    return hits


try:
    needles = [
        b"ACPP_ReadCardMain::EnterPressed",
        b"SetReadCardMode",
        b"readCardMode",
        b"isNesysOnline",
        b"RequestPlayerLogin",
        b"PremissionOfflineNesys",
        b"CardError",
        b"EnterPressed",
    ]
    segs = list(idautils.Segments())
    for ndl in needles:
        total = []
        for s in segs:
            seg = ida_segment.getseg(s)
            if seg.end_ea - seg.start_ea > 0x5000:
                total += scan_seg2(seg, ndl)
        log("## %s : %d hits" % (ndl.decode(), len(total)))
        for ea in total[:120]:
            xrefs = list(idautils.XrefsTo(ea))
            f = None
            n = "?"
            for x in xrefs[:1]:
                f = idaapi.get_func(x.frm)
                n = ida_name.get_name(f.start_ea) if f else "?"
            log("   data @0x%X xrefs=%d first=%s" % (ea, len(xrefs), n))
except Exception as e:
    log("EXC:", repr(e))
finally:
    OUT.close()
    idc.qexit(0)