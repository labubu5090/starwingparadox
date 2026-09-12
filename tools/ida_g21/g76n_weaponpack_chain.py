"""From patch site 0x243CF50 (WeaponManager::InitalizeWeapon) walk calls to InitWeaponPack -> CreateWeaponBody."""
import json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76n_weaponpack_chain.json"

try:
    import ida_funcs
    import ida_hexrays
    import ida_name
    import ida_idaapi
    import idautils
    import idc
except ImportError as e:
    import ida_pro
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
    ida_pro.qexit(1)

res = {"chain": {}, "errors": []}
BAD = ida_idaapi.BADADDR
ANCHOR = 0x140000000 + 0x243CF50  # InitalizeWeapon patch site

def add(ea, label, depth=0):
    f = ida_funcs.get_func(ea)
    if not f:
        res["errors"].append("%s: no func at %x" % (label, ea))
        return
    en = f.start_ea
    res["chain"][label] = {"start_ea": hex(en)}
    try:
        cfg = ida_hexrays.decompile(en)
        res["chain"][label]["code"] = str(cfg) if cfg else None
    except Exception as e:
        res["errors"].append("%s: %r" % (label, e))

add(ANCHOR, "WeaponManager_InitalizeWeapon")

# Walk every call target within the decompiler output and decompile it too.
code = (res["chain"].get("WeaponManager_InitalizeWeapon", {}) or {}).get("code") or ""
import re
call_targets = set()
for m in re.finditer(r"sub_([0-9A-Fa-f]{6,})", code):
    try:
        ea = int(m.group(1), 16)
    except ValueError:
        continue
    if ida_funcs.get_func(ea):
        call_targets.add(ea)

nice = {0x142C04E00: "container_handler", }
for i, ea in enumerate(sorted(call_targets)):
    add(ea, "call_%d_%x" % (i, ea))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
import ida_pro
ida_pro.qexit(0)