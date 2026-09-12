import idaapi, idc, idautils, ida_nalt, ida_bytes, ida_funcs, ida_name, ida_segment
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_x_tick.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

ea = 0x142AE8A97
func = ida_funcs.get_func(ea)
w("func start", hex(func.start_ea), "end", hex(func.end_ea), "name", ida_funcs.get_func_name(func.start_ea))
w("--- disasm around Tick's RPL setter (start 0x142AE8A40) ---")
cur = func.start_ea
count = 0
while cur < func.end_ea and count < 90:
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    count += 1
f.close()