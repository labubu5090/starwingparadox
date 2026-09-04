import json, idautils, idc, ida_funcs, ida_name
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\sd_flag_func_disasm.json"
func_ea = 0x142AFF640
from_ea1 = 0x142b00385
from_ea2 = 0x142b003f6
lines = []
a = func_ea
for i in range(1200):
    if a == idc.BADADDR:
        break
    ln = idc.GetDisasm(a)
    if a == from_ea1:
        ln = ln + "  <<<<<< XREF already_setup"
    if a == from_ea2:
        ln = ln + "  <<<<<< XREF not_setup"
    lines.append(hex(a) + ": " + ln)
    a = idc.next_head(a)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"func": hex(func_ea), "from1": hex(from_ea1), "from2": hex(from_ea2), "lines": lines}, f, ensure_ascii=False, indent=1)
print("DONE", len(lines))