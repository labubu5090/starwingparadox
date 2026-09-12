"""G68: understand PremissionOfflineNesys (mode 22) handling and the ReturnTitle path.
Find all callers of SetReadCardMode with mode 22 and the ReturnTitle enum; decompile
the mode-22 tick handling in the state machine (sub_142AD75E0 already have) and
sub_142AD58E0 fully, plus find where 22 / ReturnTitle constants are referenced."""
import traceback

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g68_mode22.txt"

lines = []

def add(s):
    lines.append(s)

# Mode enum guess from logs:
#  22 (0x16) = PremissionOfflineNesys
#  ReturnTitle appears as a SetReadCardMode label. Find the numeric enum.
# Search strings for the mode names to get the enum->name mapping table.
try:
    import ida_hexrays, ida_name, ida_bytes, idautils, idc

    add("### Mode-name strings found near 'ReadCardMode' usage")
    for s in idautils.Strings():
        val = str(s)
        if val in ("ReadCardMode",) or ("Premission" in val) or ("ReturnTitle" in val) or ("ReadCardExec" in val) or ("ReadCardModeEnd" in val):
            add("  @0x%X: %r" % (s.ea, val))

    add("")
    add("### XREFs to sub_142AD58E0 (Tick) - see callers")
    for x in idautils.XrefsTo(0x142AD58E0):
        add("  from 0x%X %s" % (x.frm, idc.get_func_name(x.frm) or "?"))

    add("")
    add("### Where is 0x16 (22) set through SetReadCardMode? Search code for call patterns")
    # decompile sub_142AE2680 (a helper called in BeginPlay after) and sub_142AD9FC0
    for ea, lab in [(0x142AE2680, "sub_142AE2680 (after-beginplay helper)"),
                    (0x142AD9FC0, "sub_142AD9FC0 (beginplay helper)"),
                    (0x142A5D7F0, "sub_142A5D7F0 (offline check)"),
                    (0x142A61920, "sub_142A61920 (sub display getter)")]:
        add("")
        add("### %s  ea=0x%X" % (lab, ea))
        try:
            cfunc = ida_hexrays.decompile(ea)
            add(str(cfunc))
        except Exception as e:
            add("failed: %r" % e)
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