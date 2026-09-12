import idaapi, idc, idautils, ida_funcs, ida_bytes
OUT = r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_tickfull.txt"
f = open(OUT, "w")
def w(*a):
    f.write(" ".join(str(x) for x in a) + "\n")
    f.flush()

func = ida_funcs.get_func(0x142AE86F0)
w("=== FULL Tick disasm (0x142AE86F0 - 0x142AE9398) ===")
cur = func.start_ea
while cur <= func.end_ea:
    w("%s %s" % (hex(cur), idc.generate_disasm_line(cur, 0)))
    nxt = idc.next_head(cur, func.end_ea)
    if nxt == 0xFFFFFFFFFFFFFFFF or nxt <= cur: break
    cur = nxt

# jump table bytes
w("\n--- jump table jpt_142AE87A5 ---")
num = 26
jt = 0x142AE87A5
# jpt address is in the jumptable data section; read 26 dwords from the table
# The table pointer is ds:jpt_142AE87A5 - find its address via xref
for x in idautils.XrefsTo(0x142AE87A5, 1):
    w("data xref to jpt:", hex(x.frm))
w("\n--- mode names / SetReadCardMode function ---")
# find SetReadCardMode function: it logs 'SetReadCardMode'
# known string at 0x14781BE60 was 'EnterPressed'; find SetReadCardMode callers -> function
f.close()