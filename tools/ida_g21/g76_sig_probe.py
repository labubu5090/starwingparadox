import json, inspect
out = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76_sig_probe.json"
r = {}
try:
    import ida_bytes
    r["bin_search_doc"] = str(ida_bytes.bin_search.__doc__) if hasattr(ida_bytes.bin_search,"__doc__") else None
    r["find_bytes_doc"] = str(ida_bytes.find_bytes.__doc__) if hasattr(ida_bytes.find_bytes,"__doc__") else None
except Exception as e:
    r["err"] = str(e)
with open(out,"w",encoding="utf-8") as f:
    json.dump(r,f,indent=2)
print("SIG_DONE")
import ida_pro
ida_pro.qexit(0)
