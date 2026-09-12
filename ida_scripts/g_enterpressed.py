import idautils, ida_bytes, idc, ida_funcs, idc, idaapi

f = open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_enterpressed.txt", "w")
f.write("=== EnterPressed 0x142ADCE40 full ===" + "\n")

ea = 0x142ADCE40
end = 0x142ADD800
while ea < end:
    name = idc.get_func_name(ea)
    line = "0x%x %s" % (ea, idc.GetDisasm(ea))
    f.write(line + "\n")
    ea = idc.next_head(ea, end)
    if ea == idc.BADADDR or ea == 0:
        break
f.close()
print("done")
