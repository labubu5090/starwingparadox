import json, ida_hexrays, ida_funcs, idc, idautils
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\sd_aux.json"
res = {}
for name, ea in [("sub_142F500E0_setup", 0x142F500E0), ("sub_142F419B0_getter", 0x142F419B0)]:
    try:
        p = ida_hexrays.decompile(ea)
        res[name] = str(p)
    except Exception as e:
        res[name] = "ERR " + str(e)
# dump bytes at patch site 0x142b00346..0x142b003c0
res["patch_site"] = {}
a = 0x142b00346
for i in range(12):
    x = ida_funcs.get_func(a)
    ins = idc.GetDisasm(a)
    bts = []
    for j in range(8):
        b = idc.get_wide_byte(a+j)
        if ida_funcs.get_func(a+j) and x and ida_funcs.get_func(a+j).start_ea == x.start_ea:
            bts.append(b)
    res["patch_site"][hex(a)] = {"bytes": [hex(b) for b in idc.get_bytes(a, 8)] , "disasm": ins}
    a = idc.next_head(a)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("DONE")