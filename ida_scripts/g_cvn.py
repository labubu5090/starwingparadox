import idaapi, idc, idautils, ida_funcs
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_cvn.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

# CheckValidNESiCA @ caller 0x142ad8a51
ea = 0x142ad8a51
func = ida_funcs.get_func(ea)
w("FUNC", hex(func.start_ea), hex(func.end_ea), ida_funcs.get_func_name(func.start_ea))
# disasm 60 lines before and after the xref site
start = ea - 30
cur = func.start_ea
for i in range(120):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    if cur > func.end_ea: break

w("\n--- IsValidCreditTime @0x1427ff5?? (uses IsNesicaReceptionTime at 0x1427ff5c0) ---")
ea2 = 0x1427ff5c0 - 0x200
func2 = ida_funcs.get_func(ea2)
w("FUNC", hex(func2.start_ea), hex(func2.end_ea), ida_funcs.get_func_name(func2.start_ea))
cur = func2.start_ea
for i in range(60):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func2.end_ea)
    if cur > func2.end_ea: break
f.close()