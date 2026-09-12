import json
out = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76_api_probe.json"
r = {}
try:
    import ida_search
    r["ida_search_attrs"] = [a for a in dir(ida_search) if "find" in a.lower() or "bin" in a.lower() or "search" in a.lower()]
except Exception as e:
    r["ida_search_err"] = str(e)
try:
    import ida_bytes
    r["ida_bytes_attrs"] = [a for a in dir(ida_bytes) if "find" in a.lower() or "bin" in a.lower() or "search" in a.lower()]
except Exception as e:
    r["ida_bytes_err"] = str(e)
try:
    import idc
    r["idc_attrs"] = [a for a in dir(idc) if "find" in a.lower()]
except Exception as e:
    r["idc_err"] = str(e)
with open(out, "w", encoding="utf-8") as f:
    json.dump(r, f, indent=2)
print("PROBE_DONE")
import ida_pro
ida_pro.qexit(0)
