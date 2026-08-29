"""G34 Comprehensive IDA Analysis Script.

Answers:
1. Exact caller of 'Error No MatchingServer so initialize Nesys before'
2. MatchingServer object constructor and allocation
3. Condition deciding whether MatchingServer is null
4. All reads and writes of IsOnline in this path
5. CPP_NesysControl-related initialization
6. \\.\pipe\nesys_games open path
7. LCOMMAND_CLIENT_START identifier and frame layout
8. SCOMMAND_CLIENT_START_REPLY identifier and parser
9. LCOMMAND_LOCALNW_INFO_REQUEST identifier and frame layout
10. Expected NetworkInfo reply parser
11. Whether any reply field asserts certificate/vendor trust
12. Whether Config path creates MatchingServer independently
13. Whether Shipping received Config command-line arguments
"""
import json
import os
import sys
import traceback

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g34_comprehensive_analysis.json")

results = {
    "status": "RUNNING",
    "sections": {},
    "errors": [],
}


def log_section(name, data):
    results["sections"][name] = data


def log_error(name, exc):
    results["errors"].append({"name": name, "error": str(exc), "traceback": traceback.format_exc()})


try:
    import ida_ida
    import ida_kernwin
    import ida_nalt
    import ida_bytes
    import ida_funcs
    import ida_segment
    import ida_name
    import ida_xref
    import ida_ua
    import idc
    import idautils
except ImportError as e:
    results["errors"].append({"name": "import", "error": str(e)})
    results["status"] = "FATAL_IMPORT_ERROR"
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    import ida_pro
    ida_pro.qexit(1)


def get_function_name(ea):
    try:
        return ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or hex(ea)
    except:
        return hex(ea)


def get_string_at(ea):
    try:
        s = idc.get_strlit_contents(ea)
        if s:
            return s.decode("utf-8", errors="ignore")
    except:
        pass
    return None


def find_string_xrefs(search_str):
    """Find all xrefs to a string."""
    refs = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and search_str in s:
            for xref in idautils.XrefsTo(s_ea):
                refs.append({
                    "string_ea": hex(s_ea),
                    "string_value": s[:200],
                    "xref_ea": hex(xref.frm),
                    "xref_type": xref.type,
                })
    return refs


def get_func_containing(ea):
    """Get the function containing an address."""
    try:
        func = ida_funcs.get_func(ea)
        if func:
            return func.start_ea, func.end_ea
    except:
        pass
    return None, None


def get_callee_name(ea):
    """Try to get the name of a function called at ea."""
    try:
        mnem = idc.print_insn_mnem(ea)
        if mnem in ("call", "CALL", "jmp", "JMP"):
            target = idc.get_operand_value(ea, 0)
            if target:
                return get_function_name(target)
    except:
        pass
    return None


# ===========================================================================
# Section 1: Find 'Error No MatchingServer so initialize Nesys before'
# ===========================================================================
try:
    refs = find_string_xrefs("Error No MatchingServer")
    callers = []
    for ref in refs:
        xref_ea = int(ref["xref_ea"], 16)
        func_start, func_end = get_func_containing(xref_ea)
        if func_start is not None:
            callers.append({
                **ref,
                "function_ea": hex(func_start),
                "function_name": get_function_name(func_start),
            })
    log_section("1_matching_server_error_callers", {
        "total_refs": len(refs),
        "callers": callers,
    })
except Exception as e:
    log_error("1_matching_server_error", e)


# ===========================================================================
# Section 2: Find MatchingServer-related strings and code
# ===========================================================================
try:
    matching_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s.lower() for kw in ["matchingserver", "matching_server", "matchingsvr"]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "type": xref.type,
                    "function": get_function_name(get_func_containing(xref.frm)[0] or xref.frm),
                })
            matching_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:10],
            })
    log_section("2_matching_server_strings", {
        "total": len(matching_strings),
        "strings": matching_strings[:30],
    })
except Exception as e:
    log_error("2_matching_server_strings", e)


# ===========================================================================
# Section 3: Find IsOnline reads/writes
# ===========================================================================
try:
    isonline_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in ["IsOnline", "isonline", "IsOnlineStatus"]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "type": xref.type,
                    "function": get_function_name(func_start or xref.frm),
                })
            isonline_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:10],
            })
    log_section("3_isonline_strings", {
        "total": len(isonline_strings),
        "strings": isonline_strings[:30],
    })
except Exception as e:
    log_error("3_isonline_strings", e)


# ===========================================================================
# Section 4: Find UseConfigMatchingServer and Config path
# ===========================================================================
try:
    config_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "UseConfigMatchingServer", "DefaultMatchingServerAddress",
            "MatchingServer address from Config",
            "UseConfigMatchingServer use commandLine",
            "HttpServerAddress", "UseConfigHttpServer",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "type": xref.type,
                    "function": get_function_name(func_start or xref.frm),
                })
            config_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:10],
            })
    log_section("4_config_path_strings", {
        "total": len(config_strings),
        "strings": config_strings,
    })
except Exception as e:
    log_error("4_config_path_strings", e)


# ===========================================================================
# Section 5: Find Connect MatchingServer address decision point
# ===========================================================================
try:
    connect_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "Decide connect MatchingServer",
            "Connect to MatchingServer address from NESYS",
            "MatchingServer address from Config",
            "UAcrProtocol::Connect",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "type": xref.type,
                    "function": get_function_name(func_start or xref.frm),
                })
            connect_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:10],
            })
    log_section("5_connect_decision_strings", {
        "total": len(connect_strings),
        "strings": connect_strings,
    })
except Exception as e:
    log_error("5_connect_decision_strings", e)


# ===========================================================================
# Section 6: Find NESYS pipe path
# ===========================================================================
try:
    pipe_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "nesys_games", "pipe", "\\\\.\\pipe",
            "CreateNamedPipe", "ConnectNamedPipe", "WaitNamedPipe",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "type": xref.type,
                    "function": get_function_name(func_start or xref.frm),
                })
            pipe_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:10],
            })
    log_section("6_pipe_strings", {
        "total": len(pipe_strings),
        "strings": pipe_strings[:30],
    })
except Exception as e:
    log_error("6_pipe_strings", e)


# ===========================================================================
# Section 7: Find LCOMMAND/SCOMMAND identifiers
# ===========================================================================
try:
    lcommand_strings = []
    scommand_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s:
            if any(kw in s for kw in ["LCOMMAND", "lcommand"]):
                lcommand_strings.append({"ea": hex(s_ea), "value": s[:200]})
            if any(kw in s for kw in ["SCOMMAND", "scommand"]):
                scommand_strings.append({"ea": hex(s_ea), "value": s[:200]})

    # Also search for numeric constants that might be command IDs
    # Search for 0x02, 0x0D, 0x15, 0x1B near relevant code
    command_id_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "CLIENT_START", "CERT_ERROR", "CERT_INIT",
            "LOCALNW_INFO", "HTTPACCESS", "RequestNetworkInfo",
            "NetworkInfo",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "function": get_function_name(func_start or xref.frm),
                })
            command_id_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:5],
            })

    log_section("7_command_id_strings", {
        "lcommand_total": len(lcommand_strings),
        "scommand_total": len(scommand_strings),
        "lcommand_samples": lcommand_strings[:20],
        "scommand_samples": scommand_strings[:20],
        "command_id_strings": command_id_strings[:30],
    })
except Exception as e:
    log_error("7_command_id_strings", e)


# ===========================================================================
# Section 8: Find RequestNetworkInfo
# ===========================================================================
try:
    network_info_refs = find_string_xrefs("RequestNetworkInfo")
    log_section("8_request_network_info", {
        "total_refs": len(network_info_refs),
        "refs": network_info_refs[:20],
    })
except Exception as e:
    log_error("8_request_network_info", e)


# ===========================================================================
# Section 9: Find certificate/trust-related strings
# ===========================================================================
try:
    trust_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s.lower() for kw in [
            "certificate", "cert_error", "certerror",
            "trust", "authenticate", "auth_status",
            "vendor", "taito", "nesica",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "function": get_function_name(func_start or xref.frm),
                })
            trust_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:5],
            })
    log_section("9_trust_strings", {
        "total": len(trust_strings),
        "strings": trust_strings[:30],
    })
except Exception as e:
    log_error("9_trust_strings", e)


# ===========================================================================
# Section 10: Find NesysControl class references
# ===========================================================================
try:
    nesys_control_refs = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "UCPP_NesysControl", "NesysControl",
            "CPP_NesysControl", "NesysClient",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "function": get_function_name(func_start or xref.frm),
                })
            nesys_control_refs.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:5],
            })
    log_section("10_nesys_control_refs", {
        "total": len(nesys_control_refs),
        "refs": nesys_control_refs[:30],
    })
except Exception as e:
    log_error("10_nesys_control_refs", e)


# ===========================================================================
# Section 11: Find all NetworkModule functions
# ===========================================================================
try:
    network_funcs = []
    for func_ea in idautils.Functions():
        name = get_function_name(func_ea)
        if name and any(kw in name for kw in [
            "Nesys", "nesys", "Matching", "matching",
            "AcrProtocol", "Protocol", "IsOnline",
            "NetworkInfo", "CertError", "Cert",
        ]):
            network_funcs.append({
                "ea": hex(func_ea),
                "name": name,
            })
    log_section("11_network_module_functions", {
        "total": len(network_funcs),
        "functions": network_funcs[:50],
    })
except Exception as e:
    log_error("11_network_module_functions", e)


# ===========================================================================
# Section 12: Cross-reference analysis for Config path
# ===========================================================================
try:
    # Find the function containing "UseConfigMatchingServer use commandLine"
    config_decision_refs = find_string_xrefs("UseConfigMatchingServer use commandLine")
    config_address_refs = find_string_xrefs("MatchingServer address from Config")

    config_path_analysis = {
        "decision_refs": config_decision_refs[:10],
        "address_refs": config_address_refs[:10],
    }

    # For each Config path function, try to decompile and find the MatchingServer creation
    for ref in config_decision_refs:
        xref_ea = int(ref["xref_ea"], 16)
        func_start, func_end = get_func_containing(xref_ea)
        if func_start is not None:
            # Look for calls within this function that might create MatchingServer
            ea = func_start
            calls_in_func = []
            while ea < func_end:
                callee = get_callee_name(ea)
                if callee:
                    calls_in_func.append({"ea": hex(ea), "callee": callee})
                ea = idc.next_head(ea)
                if ea == idc.BADADDR:
                    break
            config_path_analysis["config_function"] = {
                "ea": hex(func_start),
                "name": get_function_name(func_start),
                "calls": calls_in_func[:20],
            }
            break

    log_section("12_config_path_analysis", config_path_analysis)
except Exception as e:
    log_error("12_config_path_analysis", e)


# ===========================================================================
# Section 13: Find the GameModeBoot class and its methods
# ===========================================================================
try:
    boot_strings = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "ACPP_GameModeBoot", "GameModeBoot",
            "NesysControlErrorMessage", "NesysRequest",
            "SetupSystem", "NetworkInitialize",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "function": get_function_name(func_start or xref.frm),
                })
            boot_strings.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:5],
            })
    log_section("13_boot_mode_strings", {
        "total": len(boot_strings),
        "strings": boot_strings[:30],
    })
except Exception as e:
    log_error("13_boot_mode_strings", e)


# ===========================================================================
# Section 14: Find OpenKey and SystemDataCheck related code
# ===========================================================================
try:
    openkey_refs = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and any(kw in s for kw in [
            "OpenKey", "SystemDataCheck", "CheckVersion",
            "CheckPackage", "CheckMasterData",
        ]):
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                func_start, _ = get_func_containing(xref.frm)
                xrefs.append({
                    "xref_ea": hex(xref.frm),
                    "function": get_function_name(func_start or xref.frm),
                })
            openkey_refs.append({
                "ea": hex(s_ea),
                "value": s[:200],
                "xrefs": xrefs[:5],
            })
    log_section("14_openkey_systemdata_strings", {
        "total": len(openkey_refs),
        "strings": openkey_refs[:30],
    })
except Exception as e:
    log_error("14_openkey_systemdata_strings", e)


# ===========================================================================
# Section 15: Binary section info
# ===========================================================================
try:
    segments = []
    for seg in idautils.Segments():
        seg_obj = ida_segment.getseg(seg)
        if seg_obj:
            name = ida_segment.get_segm_name(seg_obj) or hex(seg)
            segments.append({
                "ea": hex(seg),
                "name": name,
                "start": hex(seg_obj.start_ea),
                "end": hex(seg_obj.end_ea),
                "size": seg_obj.end_ea - seg_obj.start_ea,
            })
    log_section("15_segments", {
        "total": len(segments),
        "segments": segments[:20],
    })
except Exception as e:
    log_error("15_segments", e)


# ===========================================================================
# Finalize
# ===========================================================================
results["status"] = "SUCCESS"
results["end_utc"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE: %s" % OUT_JSON)
print("STATUS: %s" % results["status"])
print("SECTIONS: %d" % len(results["sections"]))
print("ERRORS: %d" % len(results["errors"]))

try:
    import ida_pro
    ida_pro.qexit(0)
except:
    pass
