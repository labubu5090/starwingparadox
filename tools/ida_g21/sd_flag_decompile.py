import json, ida_hexrays, ida_funcs
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\sd_flag_decompile.json"
func_ea = 0x142AFF640
try:
    p = ida_hexrays.decompile(func_ea)
    txt = str(p)
except Exception as e:
    txt = "DECOMPILE_ERR " + str(e)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"func": hex(func_ea), "text": txt}, f, ensure_ascii=False, indent=1)
print("DONE", len(txt))