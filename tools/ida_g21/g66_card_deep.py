"""G66: decompile card-register (sub_142AD6D60), validator (sub_142C64E10),
the parent getter (sub_142C61450), and xrefs into the debug-card table source.
Also decompile the NESYS card-insert completion handler (sub_142AE0030) and the
tick-mode-22 handling path to see what mode 22 (PremissionOfflineNesys) does."""
import traceback

OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\g66_card_deep.txt"

TARGETS = [
    (0x142AD6D60, "RegisterCard_SetNesicaID"),
    (0x142C64E10, "ValidateCardID"),
    (0x142C61450, "ReadCardParentGetter"),
    (0x142AE0030, "OnNesysCompleteCardIncert"),
    (0x142AD88F0, "ReadCard_bUseNesysDecider"),
    (0x142A622C0, "SharedSettings_DebugTable"),
]

lines = []
for ea, label in TARGETS:
    try:
        import ida_funcs, ida_name, ida_hexrays
        f = ida_funcs.get_func(ea)
        if f is None:
            lines.append("### %s ea=0x%X NO FUNC" % (label, ea))
            lines.append("")
            continue
        name = ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or "?"
        cfunc = ida_hexrays.decompile(ea)
        lines.append("=" * 80)
        lines.append("### %s  ea=0x%X name=%s" % (label, ea, name))
        lines.append("=" * 80)
        lines.append(str(cfunc))
        lines.append("")
    except Exception as e:
        lines.append("### %s ea=0x%X FAILED %r" % (label, ea, e))
        lines.append("")
        traceback.print_exc()

try:
    import idautils, idc
    lines.append("=" * 80)
    lines.append("### XREFS to sub_142AD6D60 (card register)")
    lines.append("=" * 80)
    for ea in sorted(idautils.DataRefsTo(0x142AD6D60)) | sorted(idautils.CodeRefsTo(0x142AD6D60)):
        lines.append("  ref 0x%X @ %s" % (ea, idc.get_func_name(ea) or "?"))
except Exception as e:
    lines.append("xref section failed: %r" % e)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("WROTE %s" % OUT)
for ea, label in TARGETS:
    print("  %s ok" % label)
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass