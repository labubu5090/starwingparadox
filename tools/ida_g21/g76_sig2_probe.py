import json, ida_bytes, idc, ida_idaapi
out = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76_sig2.json"
r = {}
pat = b"GALAXYIO"
res = {}
try:
    ea = idc.find_bytes(0, 0xFFFFFFFFFFFFFFFF, pat, ida_bytes.BIN_SEARCH_FORWARD|ida_bytes.BIN_SEARCH_CASE)
    res["idc_find_bytes"] = hex(ea) if ea not in (0xFFFFFFFFFFFFFFFF,None) else None
except Exception as e:
    res["idc_find_bytes_err"] = str(e)[:200]
try:
    mask = b"\xff"*len(pat)
    ea = ida_bytes.bin_search(0, 0xFFFFFFFFFFFFFFFF, pat, mask, len(pat), ida_bytes.BIN_SEARCH_FORWARD|ida_bytes.BIN_SEARCH_CASE)
    res["bin_search_mask"] = hex(ea) if ea not in (0xFFFFFFFFFFFFFFFF,None) else None
except Exception as e:
    res["bin_search_mask_err"] = str(e)[:200]
try:
    pv = ida_bytes.parse_binpat_str(idc.get_first_seg(), "EB 2F 02 00", 0)
    r["parse_probe"] = "ok"
except Exception as e:
    r["parse_probe"] = str(e)[:200]
r.update(res)
with open(out,"w",encoding="utf-8") as f:
    json.dump(r,f,indent=2)
print("DONE")
import ida_pro; ida_pro.qexit(0)
