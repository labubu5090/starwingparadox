import idc, idaapi, traceback, time

out = []
def A(fmt, *a):
    out.append(fmt % a if a else fmt)

def scan_range(start, end, pattern, label):
    t0 = time.time()
    results = []
    pos = start
    chunk = 0x200000  # 2MB
    while pos < end:
        size = min(chunk, end - pos)
        data = idc.get_bytes(pos, size)
        if data:
            off = 0
            while True:
                idx = data.find(pattern, off)
                if idx < 0:
                    break
                results.append(pos + idx)
                off = idx + 1
        pos += size
    A("%s: %d match(es) in %.1fs" % (label, len(results), time.time() - t0))
    for ea in results[:40]:
        A("  0x%X" % ea)
    if len(results) > 40:
        A("  ... +%d more" % (len(results) - 40))
    return results

try:
    text_end = 0x1463FD000
    rdata_start = 0x1463FECF8
    data_end = 0x149524000
    # ASCII patterns
    A("== Scanning .rdata+.data for ASCII 'SetReadCardMode' ==")
    scan_range(rdata_start, data_end, b"SetReadCardMode", "rdata+data ASCII")
    A("")
    A("== Scanning .text for ASCII 'SetReadCardMode' ==")
    scan_range(0x140001000, text_end, b"SetReadCardMode", ".text ASCII")
    A("")
    # UTF-16LE patterns
    pat16 = "SetReadCardMode".encode("utf-16le")
    A("== Scanning .rdata+.data for UTF-16 'SetReadCardMode' ==")
    scan_range(rdata_start, data_end, pat16, "rdata+data UTF16")
    A("")
    A("== Nearby printable ASCII in 0x14781BE00-0x14781BF00 ==")
    for pos in range(0x14781BE00, 0x14781BF00, 16):
        data = idc.get_bytes(pos, 16)
        if data:
            A("  %08X: %s" % (pos, data))
except Exception:
    A("EXCEPTION: %s", traceback.format_exc())

with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_test.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(out))