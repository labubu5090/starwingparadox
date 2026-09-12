import idaapi, idc, idautils, ida_funcs, ida_xref
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_recept.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

# IsNesicaReceptionTime @ 0x1427FF360
ea = 0x1427FF360
func = ida_funcs.get_func(ea)
w("FUNC", hex(func.start_ea), hex(func.end_ea), ida_funcs.get_func_name(ea))
cur = func.start_ea
for i in range(80):
    w("  ", hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    if cur == 0xFFFFFFFFFFFFFFFF or cur > func.end_ea:
        break
w("--- xrefs TO IsNesicaReceptionTime ---")
for x in idautils.XrefsTo(ea, 0):
    w("  xref", hex(x.frm), "from func", ida_funcs.get_func_name(x.frm))
# GetShopMinutes @ 0x1427F7490
w("--- GetShopMinutes 0x1427F7490 ---")
ea2 = 0x1427F7490
f2 = ida_funcs.get_func(ea2)
w("FUNC", hex(f2.start_ea), hex(f2.end_ea), ida_funcs.get_func_name(ea2))
cur = f2.start_ea
for i in range(40):
    w("  ", hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, f2.end_ea)
    if cur == 0xFFFFFFFFFFFFFFFF or cur > f2.end_ea:
        break
# GetNowMinutes @ 0x1427F6480
w("--- GetNowMinutes 0x1427F6480 ---")
ea3 = 0x1427F6480
f3 = ida_funcs.get_func(ea3)
w("FUNC", hex(f3.start_ea), hex(f3.end_ea), ida_funcs.get_func_name(ea3))
cur = f3.start_ea
for i in range(20):
    w("  ", hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, f3.end_ea)
    if cur == 0xFFFFFFFFFFFFFFFF or cur > f3.end_ea:
        break
f.close()
print("done")