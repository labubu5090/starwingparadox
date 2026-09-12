import idaapi, idc, idautils, ida_funcs
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_48xref.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

# UpdateNesicaTime @ 0x1428255a0 - dump it and its callers
ea = 0x1428255a0
func = ida_funcs.get_func(ea)
w("=== UpdateNesicaTime ===")
w("FUNC", hex(func.start_ea), hex(func.end_ea), ida_funcs.get_func_name(ea))
cur = func.start_ea
for i in range(50):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, func.end_ea)
    if cur > func.end_ea: break
w("--- xrefs to UpdateNesicaTime ---")
for x in idautils.XrefsTo(ea, 0):
    w("  xref", hex(x.frm), ida_funcs.get_func_name(x.frm))

# second caller of SetWorkNesicaTime at 0x1428255cf
ea2 = 0x1428255cf
w("\n=== context of 0x1428255cf (2nd SetWorkNesicaTime caller) ===")
for i in range(30):
    w(hex(ea2-15+i), idc.generate_disasm_line(ea2-15+i, 0))

# scan for writes to this+0x48 in the class - search a window around UTestModeWork member writes
# Look at all instructions writing to [reg+48h] - too broad. Instead disasm the function containing 0x1428255cf fully enough
ea3 = ida_funcs.get_func(ea2)
w("\n=== func containing 0x1428255cf ===")
w("FUNC", hex(ea3.start_ea), hex(ea3.end_ea), ida_funcs.get_func_name(ea3.start_ea))
cur = ea3.start_ea
for i in range(120):
    w(hex(cur), idc.generate_disasm_line(cur, 0))
    cur = idc.next_head(cur, ea3.end_ea)
    if cur > ea3.end_ea: break
f.close()