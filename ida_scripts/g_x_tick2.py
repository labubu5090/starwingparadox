import idaapi, idc, ida_funcs
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_x_tick2.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

ea = 0x142AE8A40
for i in range(70):
    w(hex(ea), idc.generate_disasm_line(ea, 0))
    ea = idc.next_head(ea)
f.close()