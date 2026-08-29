"""Minimal IDA string search - fast targeted analysis."""
import json
import os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_strings.json"

import idautils
import idc
import ida_funcs
import ida_name
import ida_auto

def get_func_name(ea):
    try:
        f = ida_funcs.get_func(ea)
        if f: return ida_funcs.get_func_name(f.start_ea) or ida_name.get_name(f.start_ea) or hex(f.start_ea)
    except: pass
    return hex(ea)

def get_str(ea):
    try:
        s = idc.get_strlit_contents(ea)
        if s: return s.decode('utf-8', errors='ignore')
    except: pass
    return None

# Search keywords (all at once in single pass)
KEYWORDS = [
    "MatchingServer", "matching_server", "IsOnline", "UseConfigMatchingServer",
    "DefaultMatchingServerAddress", "Decide connect", "address from Config",
    "address from NESYS", "initialize Nesys before", "Error No Matching",
    "nesys_games", "pipe", "LCOMMAND", "SCOMMAND", "CLIENT_START",
    "CERT_ERROR", "CERT_INIT", "LOCALNW_INFO", "RequestNetworkInfo",
    "NetworkInfo", "UCPP_NesysControl", "NesysControl", "GameModeBoot",
    "NesysControlErrorMessage", "NesysRequest", "certificate", "CertError",
    "OpenKey", "SystemDataCheck", "CheckVersion", "UseConfigHttpServer",
    "HttpServerAddress", "MatchingServerType", "commandLine value",
]

results = {}
for s_ea in idautils.Strings():
    s = get_str(s_ea)
    if not s: continue
    for kw in KEYWORDS:
        if kw in s:
            xrefs = []
            for xref in idautils.XrefsTo(s_ea):
                fn = get_func_name(xref.frm)
                xrefs.append({"ea": hex(xref.frm), "fn": fn})
            results[s[:120]] = {"ea": hex(s_ea), "xrefs": xrefs[:5]}
            break

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("FOUND %d strings" % len(results))

try:
    import ida_pro
    ida_pro.qexit(0)
except: pass
