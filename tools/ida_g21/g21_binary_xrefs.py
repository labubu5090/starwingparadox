"""G21 targeted xref extraction with pre-computed VAs from PE headers.

Uses the correct file-offset-to-RVA mapping computed from the PE section
headers. All VAs are pre-validated against the raw binary.
"""
import json
import os
import traceback
from datetime import datetime, timezone

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g21_function_xrefs.json")

# (label, va, string_value) — pre-computed from PE section mapping
# Image base = 0x140000000, RVA = VA - image_base
TARGETS = [
    ("BindHttpBoot",        0x146AC3EE8, "BindHttpBoot"),
    ("BindHttpVersion",     0x146AC6C78, "BindHttpVersion"),
    ("BindHttpResource",    0x146AC62A8, "BindHttpResource"),
    ("BindHttpGameData",    0x146AC4950, "BindHttpGameData"),
    ("HttpJsonSerialize",   0x147961815, "HttpJsonSerialize"),
    ("HttpJsonDifference",  0x14795EAC5, "HttpJsonDifference"),
    ("SystemDataCheck",     0x14782FA21, "SystemDataCheck"),
    ("PlayerData",          0x1471E1D01, "PlayerData"),
    ("GameMode",            0x14681AB0F, "GameMode"),
    ("BuddyId",             0x1472C03C8, "BuddyId"),
    ("CharacterCustomize",  0x14699D669, "CharacterCustomize"),
    ("PlayerID",            0x14699AEB9, "PlayerID"),
    ("application_json",    0x14851AFE8, "application/json"),
    ("route_matching_gen",  0x14797F788, "/matching/match_id/generate"),
    ("route_option_save",   0x147980300, "/option/save"),
    ("WinHttp",             0x1489539BA, "WinHttp"),
    ("WinInet",             0x147FDF582, "WinInet"),
]


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def main():
    import ida_bytes
    import ida_funcs
    import ida_ida
    import ida_kernwin
    import ida_name
    import ida_nalt
    import ida_segment
    import idautils
    import idc

    record = {
        "status": "RUNNING",
        "script": os.path.basename(__file__),
        "out_json": OUT_JSON,
        "start_utc": _utcnow(),
        "functions_total": 0,
        "strings_total": 0,
        "string_xrefs": [],
        "function_graphs": [],
        "errors": [],
    }

    target_path = None
    try:
        target_path = ida_nalt.get_input_path()
    except Exception:
        pass
    if not target_path or not os.path.isabs(target_path):
        target_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\targets\AcrGame-Win64-Shipping.exe"
    record["target"] = target_path

    def log(msg):
        with open(os.path.join(OUT_DIR, "g21_xref_log.txt"), "a", encoding="utf-8") as f:
            f.write(_utcnow() + "  " + str(msg) + "\n")
            f.flush()

    try:
        record["functions_total"] = len(list(idautils.Functions()))
    except Exception:
        pass
    try:
        record["strings_total"] = len(list(idautils.Strings()))
    except Exception:
        pass

    image_base = ida_nalt.get_imagebase()
    log("start; functions=%d strings=%d image_base=%s" % (record["functions_total"], record["strings_total"], hex(image_base)))

    # Process each target with pre-computed VA
    total_xrefs = 0
    for label, va, str_val in TARGETS:
        try:
            rva = va - image_base
            log("processing: %s va=0x%x rva=0x%x" % (label, va, rva))

            # Verify string exists at this VA
            verified = False
            try:
                raw = ida_bytes.get_bytes(va, min(len(str_val) + 4, 64))
                if raw:
                    decoded = raw.split(b'\x00')[0].decode('ascii', errors='replace')
                    log("  raw: %r" % decoded[:40])
                    if str_val[:8] in decoded:
                        log("  VERIFIED: string matches")
                        verified = True
                    else:
                        log("  WARNING: string may not match")
            except Exception as e:
                log("  verify error: %s" % str(e))

            # Find xrefs to this VA
            xrefs = []
            try:
                for xr in idautils.XrefsTo(va):
                    xref_func_ea = None
                    try:
                        f = ida_funcs.get_func(xr.frm)
                        if f:
                            xref_func_ea = f.start_ea
                    except Exception:
                        pass

                    func_name = ""
                    if xref_func_ea is not None:
                        try:
                            func_name = ida_funcs.get_func_name(xref_func_ea) or ida_name.get_name(xref_func_ea) or ""
                        except Exception:
                            pass

                    xrefs.append({
                        "from": hex(xr.frm),
                        "type": xr.type,
                        "containing_function": func_name,
                        "function_start": hex(xref_func_ea) if xref_func_ea else None,
                        "function_rva": hex(xref_func_ea - image_base) if xref_func_ea and xref_func_ea >= image_base else None,
                    })
                    total_xrefs += 1
                    if len(xrefs) >= 20:
                        break
            except Exception as e:
                log("  xref error: %s" % str(e))

            record["string_xrefs"].append({
                "label": label,
                "string_value": str_val,
                "virtual_address": hex(va),
                "rva": hex(rva),
                "verified": verified,
                "xrefs": xrefs,
                "xref_count": len(xrefs),
            })
            log("  xrefs: %d" % len(xrefs))

        except Exception as e:
            record["errors"].append({"label": label, "error": str(e)})
            log("ERROR %s: %s" % (label, str(e)))

    log("total xrefs: %d" % total_xrefs)

    # Build function graphs for functions with xrefs
    func_set = set()
    for xr in record["string_xrefs"]:
        for x in xr.get("xrefs", []):
            fs = x.get("function_start")
            if fs:
                func_set.add(int(fs, 16))

    for fea in list(func_set)[:20]:
        try:
            f = ida_funcs.get_func(fea)
            if not f:
                continue
            func_name = ida_funcs.get_func_name(fea) or ida_name.get_name(fea) or hex(fea)
            callees = []
            head = f.start_ea
            while head < f.end_ea and head != idc.BADADDR:
                mnem = idc.GetMnem(head)
                if mnem in ("call", "callq"):
                    target = idc.GetOperandValue(head, 0)
                    if target:
                        try:
                            cf = ida_funcs.get_func(target)
                            if cf:
                                cn = ida_funcs.get_func_name(target) or ida_name.get_name(target) or hex(target)
                                callees.append({"ea": hex(target), "name": cn})
                        except Exception:
                            pass
                head = idc.next_head(head, f.end_ea)
            callers = []
            for xr in idautils.XrefsTo(fea):
                try:
                    cf = ida_funcs.get_func(xr.frm)
                    if cf:
                        cn = ida_funcs.get_func_name(cf.start_ea) or ida_name.get_name(cf.start_ea) or hex(cf.start_ea)
                        callers.append({"ea": hex(cf.start_ea), "name": cn})
                except Exception:
                    pass
                if len(callers) >= 10:
                    break
            record["function_graphs"].append({
                "function": func_name,
                "rva": hex(fea - image_base),
                "size": f.size(),
                "callees": callees[:10],
                "callers": callers[:10],
            })
        except Exception as e:
            record["errors"].append({"function": hex(fea), "error": str(e)})

    log("function graphs: %d" % len(record["function_graphs"]))

    record["status"] = "SUCCESS"
    record["end_utc"] = _utcnow()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str, ensure_ascii=False)

    log("done; status=SUCCESS")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:
        rec = {"status": "FATAL", "error": str(e), "traceback": traceback.format_exc(), "end_utc": _utcnow()}
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, default=str)
        code = 1
    try:
        import ida_pro
        ida_pro.qexit(code)
    except Exception:
        pass
