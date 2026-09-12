import idaapi, idc, idautils, ida_funcs
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_setnesica.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

# SetWorkNesicaTime @ 0x142819dc0 - to see where start/end get stored
ea = 0x142819dc0
func = ida_funcs.get_func(ea)
w("=== SetWorkNesicaTime ===")
w("FUNC", hex(func.start_ea), hex(func.end_ea), ida_funcs.get_func_name(ea))
cur = func.start_ea
for i in range(60):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    if cur > func.end_ea: break

# FTestModeWorkNesicaTime::Set @ 0x142815990
ea2 = 0x142815990
func2 = ida_funcs.get_func(ea2)
w("\n=== FTestModeWorkNesicaTime::Set ===")
w("FUNC", hex(func2.start_ea), hex(func2.end_ea), ida_funcs.get_func_name(ea2))
cur = func2.start_ea
for i in range(40):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func2.end_ea)
    if cur > func2.end_ea: break

# ParseWorkJson around 0x14280da9c
ea3 = 0x14280da9c
w("\n=== ParseWorkJson caller (NesicaTime xref) ===")
for i in range(30):
    w(hex(ea3), idc.generate_disasm_line(ea3, 0))
    ea3 = idc.next_head(ea3)

f.close()