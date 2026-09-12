import idaapi, idc, idautils, ida_funcs
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_gshopf.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

# Full GetShopMinutes @ 0x1427F7490
ea = 0x1427F7490
func = ida_funcs.get_func(ea)
w("=== GetShopMinutes full ===")
w("FUNC", hex(func.start_ea), hex(func.end_ea))
cur = func.start_ea
for i in range(40):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    if cur > func.end_ea: break

# Full IsNesicaReceptionTime @ 0x1427FF360
w("\n=== IsNesicaReceptionTime full ===")
ea2 = 0x1427FF360
func2 = ida_funcs.get_func(ea2)
w("FUNC", hex(func2.start_ea), hex(func2.end_ea))
cur = func2.start_ea
for i in range(30):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func2.end_ea)
    if cur > func2.end_ea: break

w("\n--- GetNowMinutes ending (58h normalization) ---")
ea3 = 0x1427F6480
func3 = ida_funcs.get_func(ea3)
cur = func3.start_ea
for i in range(26):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func3.end_ea)
    if cur > func3.end_ea: break
f.close()