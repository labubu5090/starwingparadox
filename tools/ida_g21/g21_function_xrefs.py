"""G21 function-level HTTP string-to-function xref extraction.

Runs inside IDA batch mode on the project-controlled shipping exe copy.
Extracts targeted evidence for HTTP startup contract recovery.
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g21_function_xrefs.json")

# Target strings to find and trace (case-insensitive partial match)
TARGET_STRINGS = [
    # HTTP binding functions
    "BindHttpBoot", "BindHttpVersion", "BindHttpResource", "BindHttpGameData",
    "HttpGameDataLoadData", "HttpGameDataLoadMissionData",
    "ACPP_SystemDataCheck", "HttpRequestWait",
    # JSON primitives
    "CPP_HttpJsonSerialize", "CPP_HttpJsonDifference",
    "FJsonObject", "FJsonSerializer", "TJsonWriter", "TJsonReader",
    "SetStringField", "SetNumberField", "SetBoolField", "SetObjectField",
    "SetArrayField", "GetStringField", "GetNumberField", "GetBoolField",
    "GetObjectField", "TryGetField", "TryGetString", "TryGetNumber",
    # Data types
    "OptionData", "PlayerData", "mechas",
    # Status/state
    "success", "error", "timeout", "reconnect", "IsSuccess",
    # Content type
    "application/json",
    # HTTP methods
    "POST", "GET", "PUT", "DELETE",
    # Route fragments
    "matching", "option", "save", "version", "resource", "boot",
    # Known literal routes
    "/matching/match_id/generate", "/option/save",
    # Log strings from G20
    "http:ResponseGameDataLoad:", "http:Response",
    # Network/client
    "WinHttp", "WinInet", "FHttpModule", "IHttpRequest",
    "ProcessResponse", "OnProcessComplete",
    # Startup state
    "SystemDataCheck", "GameDataLoad", "MissionDataLoad",
]


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def main():
    import ida_auto
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
        "target": ida_nalt.get_input_file_path(),
        "functions_total": len(list(idautils.Functions())),
        "strings_total": len(list(idautils.Strings())),
        "string_xrefs": [],
        "function_graphs": [],
        "http_routes": [],
        "json_primitives": [],
        "errors": [],
    }

    def log(msg):
        with open(os.path.join(OUT_DIR, "g21_xref_log.txt"), "a", encoding="utf-8") as f:
            f.write(_utcnow() + "  " + str(msg) + "\n")
            f.flush()

    log("script start; functions=%d strings=%d" % (record["functions_total"], record["strings_total"]))

    # Build string list with addresses
    str_list = []
    for s in idautils.Strings():
        try:
            str_list.append({"ea": s.ea, "str": str(s), "length": s.length})
        except Exception:
            pass
    log("string list built: %d entries" % len(str_list))

    # Find target strings and their xrefs
    target_set = set(TARGET_STRINGS)

    def match_target(s):
        sl = s.lower()
        for t in target_set:
            if t.lower() in sl:
                return t
        return None

    matched_count = 0
    for srec in str_list:
        matched = match_target(srec["str"])
        if matched is None:
            continue
        matched_count += 1
        ea = srec["ea"]
        # Get all xrefs to this string
        xrefs_to = []
        try:
            xr = idautils.XrefsTo(ea)
            for x in xr:
                xrefs_to.append({"from": x.frm, "type": x.type})
        except Exception:
            pass

        for xr in xrefs_to:
            xref_ea = xr["from"]
            # Find containing function
            func_ea = None
            try:
                func_ea = idc.get_func_attr(xref_ea, idc.FUNCATTR_START)
            except Exception:
                pass
            if not func_ea:
                try:
                    f = ida_funcs.get_func(xref_ea)
                    if f:
                        func_ea = f.start_ea
                except Exception:
                    pass
            if func_ea is None:
                func_ea = idc.prev_head(xref_ea, 0)

            # Get function name
            func_name = ""
            if func_ea is not None:
                try:
                    func_name = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
                except Exception:
                    pass

            # Calculate RVA
            image_base = ida_nalt.get_imagebase()
            rva = xref_ea - image_base if xref_ea >= image_base else None
            func_rva = func_ea - image_base if func_ea is not None and func_ea >= image_base else None

            # Function size
            func_size = 0
            if func_ea is not None:
                try:
                    f = ida_funcs.get_func(func_ea)
                    if f:
                        func_size = f.size()
                except Exception:
                    pass

            # Pseudocode availability
            has_pseudocode = False
            try:
                import ida_hexrays
                cfunc = ida_hexrays.decompile(func_ea) if func_ea else None
                has_pseudocode = cfunc is not None
            except Exception:
                has_pseudocode = False

            # Get disassembly at xref
            disasm = ""
            try:
                disasm = idc.GetDisasm(xref_ea)
            except Exception:
                pass

            # Get nearby strings (within 200 bytes)
            nearby_strings = []
            try:
                for ns in idautils.Strings():
                    if ns.ea != ea and abs(int(ns.ea) - int(xref_ea)) < 200:
                        nearby_strings.append({"ea": ns.ea, "str": str(ns)})
                        if len(nearby_strings) >= 5:
                            break
            except Exception:
                pass

            record["string_xrefs"].append({
                "target_match": matched,
                "string_address": hex(ea),
                "string_value": srec["str"],
                "xref_address": hex(xref_ea),
                "xref_type": xr["type"],
                "containing_function": func_name,
                "function_start": hex(func_ea) if func_ea else None,
                "function_rva": hex(func_rva) if func_rva is not None else None,
                "function_size": func_size,
                "rva": hex(rva) if rva is not None else None,
                "has_pseudocode": has_pseudocode,
                "disasm": disasm,
                "nearby_strings": nearby_strings,
            })

    log("matched %d target strings, %d xrefs total" % (matched_count, len(record["string_xrefs"])))

    # Build function graphs for functions containing HTTP xrefs
    http_func_eas = set()
    for xref in record["string_xrefs"]:
        if any(kw in xref["target_match"].lower() for kw in ["http", "json", "bind", "systemdatacheck"]):
            fs = xref.get("function_start")
            if fs:
                http_func_eas.add(int(fs, 16))

    for fea in list(http_func_eas)[:30]:  # limit to 30 functions
        try:
            callees = []
            callers = []
            f = ida_funcs.get_func(fea)
            if f:
                # Scan for call instructions
                head = f.start_ea
                while head < f.end_ea:
                    mnem = idc.GetMnem(head)
                    if mnem in ("call", "callq"):
                        target = idc.GetOperandValue(head, 0)
                        if target and ida_funcs.get_func(target):
                            callee_name = ida_funcs.get_func_name(target) or ida_name.get_name(target) or hex(target)
                            callees.append({"ea": hex(target), "name": callee_name})
                            if len(callees) >= 20:
                                break
                    head = idc.next_head(head, f.end_ea)
                # callers: functions that call this function
                for xref in idautils.XrefsTo(fea):
                    caller_func = ida_funcs.get_func(xref.frm)
                    if caller_func:
                        caller_name = ida_funcs.get_func_name(caller_func.start_ea) or ida_name.get_name(caller_func.start_ea) or hex(caller_func.start_ea)
                        callers.append({"ea": hex(caller_func.start_ea), "name": caller_name})
                        if len(callers) >= 20:
                            break

            func_name = ida_funcs.get_func_name(fea) or ida_name.get_name(fea) or hex(fea)
            image_base = ida_nalt.get_imagebase()
            record["function_graphs"].append({
                "function": func_name,
                "rva": hex(fea - image_base),
                "size": f.size() if f else 0,
                "callees": callees,
                "callers": callers,
            })
        except Exception as e:
            record["errors"].append({"function": hex(fea), "error": str(e)})

    log("function graphs: %d" % len(record["function_graphs"]))

    # Find JSON primitive patterns (SetStringField, GetStringField, etc.)
    json_apis = [
        "SetStringField", "SetNumberField", "SetBoolField", "SetObjectField",
        "GetStringField", "GetNumberField", "GetBoolField", "GetObjectField",
        "TryGetField", "TryGetString", "TryGetNumber",
        "FJsonObject::", "FJsonSerializer::", "TJsonWriter::",
    ]
    for srec in str_list:
        for api in json_apis:
            if api.lower() in srec["str"].lower():
                # Find callers
                callers = []
                for xr in idautils.XrefsTo(srec["ea"]):
                    caller_func = ida_funcs.get_func(xr.frm)
                    if caller_func:
                        cn = ida_funcs.get_func_name(caller_func.start_ea) or ida_name.get_name(caller_func.start_ea) or hex(caller_func.start_ea)
                        callers.append({"ea": hex(caller_func.start_ea), "name": cn})
                        if len(callers) >= 5:
                            break
                record["json_primitives"].append({
                    "api": srec["str"],
                    "address": hex(srec["ea"]),
                    "callers": callers,
                })
                break

    log("json primitives found: %d" % len(record["json_primitives"]))

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
        # Write error record
        rec = {"status": "FATAL", "error": str(e), "traceback": traceback.format_exc(), "end_utc": _utcnow()}
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, default=str)
        code = 1
    try:
        import ida_pro
        ida_pro.qexit(code)
    except Exception:
        pass
