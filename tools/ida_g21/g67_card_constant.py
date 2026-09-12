"""G67: dump the expected card-id constant (unk_147985918), find the fallback
validator (sub_1427F05B0/sub_1427FEA00 path), xrefs into sub_142A622C0 (shared
settings / debug table source), and how a1+1008 gets populated."""
import traceback

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g67_card_constant.txt"

lines = []

def add(s):
    lines.append(s)

try:
    import ida_bytes, ida_hexrays, idautils, idc

    add("### Dump unk_147985918 (expected card id constant)")
    ea = 0x147985918
    raw = ida_bytes.get_bytes(ea, 128)
    if raw:
        add("bytes: %s" % raw.hex())
        for fmt in ("latin-1",):
            try:
                s = raw.decode(fmt, errors="replace")
            except Exception:
                s = ""
            add("decoded(%s): %r" % (fmt, s))
        # try wide
        try:
            w = raw.decode("utf-16-le", errors="replace")
            add("utf16le: %r" % w)
        except Exception as e:
            add("utf16le err: %r" % e)
    else:
        add("no bytes at that address")

    for ea, lab in [(0x147985918, "card-id const"), (0x1427F05B0, "validator path 1"),
                    (0x1427FEA00, "validator path 2")]:
        add("")
        add("### %s ea=0x%X" % (lab, ea))
        try:
            cfunc = ida_hexrays.decompile(ea)
            add(str(cfunc))
        except Exception as e:
            add("decompile failed: %r" % e)

    add("")
    add("### XREFs to sub_142A622C0 (shared settings debug table copy)")
    for x in idautils.XrefsTo(0x142A622C0):
        fn = idc.get_func_name(x.frm) or "?"
        add("  from 0x%X  %s" % (x.frm, fn))

    add("")
    add("### XREFs to sub_142A622C0 result read a1+1008: references in roundabout")
    add("### look for string 'DebugNesica' or card-table related names")
    for s in idautils.Strings():
        val = str(s)
        if "esica" in val or "CardId" in val or "card_id" in val.lower() or "DebugNesica" in val:
            add("  string @0x%X: %r" % (s.ea, val))
except Exception:
    add("script failed")
    traceback.print_exc()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("WROTE %s (%d lines)" % (OUT, len(lines)))
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass