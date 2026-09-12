import json
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\probe.json"
import ida_ua, ida_bytes, ida_idp
d = {
    "insn_t_attrs": [x for x in dir(ida_ua.insn_t) if not x.startswith("__")],
    "ida_ua_attrs": [x for x in dir(ida_ua) if not x.startswith("__")],
    "idp_attrs": [x for x in dir(ida_idp) if not x.startswith("__")],
}
open(OUT, "w", encoding="utf-8").write(json.dumps(d, indent=1))
import ida_pro
ida_pro.qexit(0)