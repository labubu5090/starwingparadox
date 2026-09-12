import idc, traceback, struct

out = []
def A(fmt, *a):
    out.append(fmt % a if a else fmt)

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

try:
    rdata_start = 0x1463FECF8
    dt_end = 0x149524000
    text_end = 0x1463FD000

    targets = {
        0x1478049D6: "SetReadCardMode [%s]",
        0x14781BE60: "EnterPressed / readCardMode [%s] -> [%s]",
        0x14781BE86: "EnterPressed readCardMode mid",
    }

    for tgt, label in targets.items():
        p8 = struct.pack("<Q", tgt)
        p4 = struct.pack("<I", tgt & 0xFFFFFFFF)
        log = []
        r = scan_for(rdata_start, dt_end, p8)
        log.append("  rdata+data 8B-ptr hits=%d" % len(r))
        for ea in r[:20]:
            log.append("    0x%X" % ea)
        r2 = scan_for(0x140001000, text_end, p4)
        log.append("  .text 4B-imm hits=%d" % len(r2))
        for ea in r2[:20]:
            log.append("    0x%X" % ea)
        r3 = scan_for(0x140001000, text_end, p8)
        log.append("  .text 8B-imm hits=%d" % len(r3))
        for ea in r3[:20]:
            log.append("    0x%X" % ea)
        A("== %s (0x%X) ==" % (label, tgt))
        A("\n".join(log))
        A("")
except Exception:
    A("EXCEPTION: %s", traceback.format_exc())

with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_test.txt", "w", encoding="ascii") as f:
    f.write("\n".join(out))