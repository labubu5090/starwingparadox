"""IDA fast string search without auto_wait - uses existing analysis."""
import json
import os
import sys

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_strings_v2.json"

try:
    import ida_ida
    import ida_nalt
    import ida_bytes
    import ida_funcs
    import ida_name
    import ida_segment
    import idautils
    import idc
except ImportError as e:
    with open(OUT, "w") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"status": "RUNNING", "strings": {}, "errors": []}

# Check database state
try:
    results["min_ea"] = hex(ida_ida.inf_get_min_ea())
    results["max_ea"] = hex(ida_ida.inf_get_max_ea())
    results["input"] = ida_nalt.get_input_file_path()
except Exception as e:
    results["errors"].append(str(e))

KEYWORDS = [
    "MatchingServer", "matching_server", "IsOnline", "UseConfigMatchingServer",
    "DefaultMatchingServerAddress", "Decide connect", "address from Config",
    "address from NESYS", "initialize Nesys before", "Error No Matching",
    "nesys_games", "LCOMMAND", "SCOMMAND", "CLIENT_START",
    "CERT_ERROR", "CERT_INIT", "LOCALNW_INFO", "RequestNetworkInfo",
    "NetworkInfo", "UCPP_NesysControl", "NesysControl", "GameModeBoot",
    "NesysControlErrorMessage", "NesysRequest", "certificate", "CertError",
    "OpenKey", "SystemDataCheck", "CheckVersion", "UseConfigHttpServer",
    "HttpServerAddress", "MatchingServerType", "commandLine value",
    "pipe", "CreateNamedPipe", "ConnectNamedPipe",
]

def get_func_name(ea):
    try:
        f = ida_funcs.get_func(ea)
        if f:
            nm = ida_funcs.get_func_name(f.start_ea)
            if nm: return nm
            nm = ida_name.get_name(f.start_ea)
            if nm: return nm
            return hex(f.start_ea)
    except: pass
    return hex(ea)

# First try idautils.Strings (needs analysis)
try:
    count = 0
    for s_ea in idautils.Strings():
        try:
            s = idc.get_strlit_contents(s_ea)
            if s:
                s = s.decode('utf-8', errors='ignore')
                for kw in KEYWORDS:
                    if kw in s:
                        xrefs = []
                        for xref in idautils.XrefsTo(s_ea):
                            xrefs.append({"ea": hex(xref.frm), "fn": get_func_name(xref.frm)})
                        results["strings"][s[:120]] = {"ea": hex(s_ea), "xrefs": xrefs[:5]}
                        count += 1
                        break
        except:
            pass
        if count >= 50:
            break
    results["string_scan_count"] = count
except Exception as e:
    results["errors"].append("string_scan: " + str(e))

# If no strings found, try byte pattern search for key string literals
if count == 0:
    results["byte_search"] = "attempting"
    # Search for "MatchingServer" as bytes in .rdata
    try:
        for seg in idautils.Segments():
            seg_obj = ida_segment.getseg(seg)
            name = ida_segment.get_segm_name(seg_obj) or ""
            if ".rdata" in name or ".data" in name:
                ea = seg_obj.start_ea
                end = min(seg_obj.end_ea, seg_obj.start_ea + 0x10000000)  # limit scan
                while ea < end:
                    try:
                        s = idc.get_strlit_contents(ea)
                        if s:
                            s_decoded = s.decode('utf-8', errors='ignore')
                            for kw in KEYWORDS:
                                if kw in s_decoded:
                                    results["strings"][s_decoded[:120]] = {"ea": hex(ea), "segment": name}
                                    break
                            ea += len(s) + 1
                        else:
                            ea = idc.next_head(ea)
                            if ea == idc.BADADDR:
                                break
                    except:
                        ea += 1
                break
    except Exception as e:
        results["errors"].append("byte_search: " + str(e))

results["status"] = "SUCCESS"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("FOUND %d strings" % len(results.get("strings", {})))
for k, v in list(results.get("strings", {}).items())[:10]:
    print("  %s: %s" % (v.get("ea", "?"), k))

try:
    import ida_pro
    ida_pro.qexit(0)
except: pass
