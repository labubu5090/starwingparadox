# Find where [reg+594h] (bUseNesys field) is WRITTEN and find PremissionOfflineNesys string
import json, struct
import ida_pro

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g48_busenys_write.json"

def get_bytes_range(start, end):
    import ida_bytes
    return ida_bytes.get_bytes(start, end)

# approach: scan all functions for the byte pattern writing +594h within ACPP_ReadCardMain-related funcs
# Better: use grep of disasm. We'll do a targeted scan over the ReadCardMain function range and nearby.
import ida_ua, ida_funcs, idautils, ida_name, ida_bytes, idc

results = {"status":"RUNNING","writers":[],"errors":[]}

# function addresses we know exist from strings/context: sub_142AD4F90 BeginPlay
# Find all funcs that reference constant 0x594
# We'll scan every function's disassembly bytes for displacement 0x594 (94 05 00 00 with modrm)
# Patterns: 88 87 94 05 00 00 (mov [rdi+594h], al), etc. Easier: use IDA's operand to grep.
def scan_func_for_594(f):
    cur = f.start_ea
    while cur < f.end_ea:
        insn = ida_ua.insn_t()
        length = ida_ua.decode_insn(insn, cur)
        if length == 0:
            cur += 1
            continue
        mnem = insn.get_canon_mnem()
        # check operands for +594h / +0x594 / 594
        ops_txt = ""
        for i in range(8):
            op = idc.print_operand(cur, i)
            if op:
                ops_txt += " " + op
            else:
                break
        if ("594h" in ops_txt) or ("594" in ops_txt and "5A4" not in ops_txt):
            raw = ida_bytes.get_bytes(cur, length)
            bts = " ".join("%02X"%b for b in raw) if raw else ""
            results["writers"].append({"ea":cur,"f":ida_name.get_name(f.start_ea),"mnem":mnem,"ops":ops_txt.strip(),"bytes":bts})
        cur += length

cnt = 0
for f in idautils.Functions():
    try:
        scan_func_for_594(ida_funcs.get_func(f))
        cnt += 1
    except Exception:
        pass

results["funcs_scanned"] = cnt
results["status"] = "SUCCESS"
with open(OUT,"w",encoding="utf-8") as fh:
    json.dump(results,fh,indent=2,default=str)
print("COMPLETE scanned", cnt)
ida_pro.qexit(0)
