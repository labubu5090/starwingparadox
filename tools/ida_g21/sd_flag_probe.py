import json, idautils, idc, ida_funcs, ida_name
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\sd_flag_probe.json"
TRG = {
  "log_already_setup": 0x147847c70,
  "log_not_setup": 0x147848460,
}
res = {}
for k, ea in TRG.items():
    xr_list = []
    for xref in idautils.XrefsTo(ea):
        frm = xref.frm
        f = ida_funcs.get_func(frm)
        faddr = f.start_ea if f else None
        fname = ida_funcs.get_func_name(faddr) if faddr else ""
        xr_list.append({"from": hex(frm), "func": fname, "func_ea": hex(faddr) if faddr else None})
    res[k] = xr_list

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("DONE")