import json
import os
import sys
import traceback

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g47_game_server_info.json"
results = {"status": "RUNNING", "sections": {}, "errors": []}

try:
    import ida_ida
    import ida_funcs
    import ida_bytes
    import ida_segment
    import ida_name
    import ida_xref
    import ida_ua
    import ida_hexrays
    import idc
    import idautils
except Exception as e:
    results["errors"].append({"name": "import", "error": str(e)})
    results["status"] = "FATAL_IMPORT_ERROR"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    try:
        import ida_pro
        ida_pro.qexit(1)
    except Exception:
        pass
    sys.exit(1)


def fname(ea):
    try:
        return ida_funcs.get_func_name(ea) or ida_name.get_name(ea) or hex(ea)
    except Exception:
        return hex(ea)


def get_string_at(ea):
    try:
        s = idc.get_strlit_contents(ea)
        if s:
            return s.decode("utf-8", errors="ignore")
    except Exception:
        pass
    return None


def func_of(ea):
    try:
        f = ida_funcs.get_func(ea)
        if f:
            return f.start_ea, f.end_ea
    except Exception:
        pass
    return None, None


def find_string_xrefs(search_str):
    refs = []
    for s_ea in idautils.Strings():
        s = get_string_at(s_ea)
        if s and search_str in s:
            for xref in idautils.XrefsTo(s_ea):
                refs.append({"string_ea": hex(s_ea), "string_value": s[:200],
                             "xref_ea": hex(xref.frm), "xref_type": xref.type,
                             "function": fname(func_of(xref.frm)[0] or xref.frm)})
    return refs


def scan_calls(func_start, func_end, out_list, limit=40, keyword=None):
    ea = func_start
    n = 0
    while ea < func_end and n < limit:
        mnem = idc.print_insn_mnem(ea)
        if mnem in ("call", "jmp"):
            target = idc.get_operand_value(ea, 0)
            if target:
                tname = fname(target)
                if keyword is None or keyword.lower() in tname.lower():
                    out_list.append({"ea": hex(ea), "callee": tname})
                    n += 1
        ea = idc.next_head(ea)
        if ea == idc.BADADDR:
            break


def decompile(func_start):
    try:
        cf = ida_hexrays.decompile(func_start)
        if cf:
            return str(cf)
    except Exception as e:
        return "DECOMPILE_ERR: %s" % e
    return None


def log(name, data):
    results["sections"][name] = data


def err(name, e):
    results["errors"].append({"name": name, "error": str(e), "traceback": traceback.format_exc()})


# ---------------------------------------------------------------------------
# 1. Find callers of SetNesysGameServerInfo
# ---------------------------------------------------------------------------
try:
    for kw in ["SetNesysGameServerInfo", "ResetNesysGameServerInfo",
               "GetNesysGameServerHttpIP", "GetNesysGameServerTcpIP",
               "SetNesysGameServerHttpIP", "SetNesysGameServerTcpIP",
               "GetNesysGameServerInfo"]:
        refs = find_string_xrefs(kw)
        log("1_xrefs_" + kw, {"total": len(refs), "refs": refs})
except Exception as e:
    err("1_xrefs", e)

# ---------------------------------------------------------------------------
# 2. Find functions whose names contain NesysGameServer or GameServerInfo
# ---------------------------------------------------------------------------
try:
    funcs = []
    for func_ea in idautils.Functions():
        name = fname(func_ea)
        if any(k in name for k in ["NesysGameServer", "GameServerInfo",
                                    "GetGameServerInfo", "SetGameServerInfo"]):
            funcs.append({"ea": hex(func_ea), "name": name})
    log("2_game_server_info_funcs", {"total": len(funcs), "functions": funcs})
except Exception as e:
    err("2_game_server_info_funcs", e)

# ---------------------------------------------------------------------------
# 3. Find the function containing "Use GetNesysInfo address" and decompile it
# ---------------------------------------------------------------------------
try:
    refs = find_string_xrefs("Use GetNesysInfo address")
    log("3_use_getnesysinfo_refs", refs)
    decompiled = []
    seen = set()
    for r in refs:
        fs, fe = func_of(int(r["xref_ea"], 16))
        if fs and fs not in seen:
            seen.add(fs)
            body = decompile(fs)
            decompiled.append({"function_ea": hex(fs), "function_name": fname(fs),
                               "calls": [], "decompiled": body})
            # collect interesting calls inside
            scan_calls(fs, fe, decompiled[-1]["calls"], limit=60)
    log("3_use_getnesysinfo_decompiled", {"count": len(decompiled),
                                          "functions": decompiled})
except Exception as e:
    err("3_use_getnesysinfo", e)

# ---------------------------------------------------------------------------
# 4. Find the function containing "GetNesysGameServerHttpIP is empty"
#    (that is UCPP_HttpRequester::GetHostAddress) and decompile it
# ---------------------------------------------------------------------------
try:
    for kw in ["GetNesysGameServerHttpIP is empty"]:
        refs = find_string_xrefs(kw)
        log("4_gethostaddr_refs_" + kw, refs)
        decompiled = []
        seen = set()
        for r in refs:
            fs, fe = func_of(int(r["xref_ea"], 16))
            if fs and fs not in seen:
                seen.add(fs)
                body = decompile(fs)
                decompiled.append({"function_ea": hex(fs), "function_name": fname(fs),
                                   "decompiled": body})
        log("4_gethostaddr_decompiled_" + kw, {"count": len(decompiled),
                                               "functions": decompiled})
except Exception as e:
    err("4_gethostaddr", e)

# ---------------------------------------------------------------------------
# 5. Find where MatchingServerType / ENesysGameServerType decision is made
#    and the strings that indicate the GetNesysInfo branch
# ---------------------------------------------------------------------------
try:
    kw_list = ["Use GetNesysInfo", "ENesysGameServerType::GetNesysInfo",
               "ENesysGameServerType::GetNetworkConfig",
               "ENesysGameServerType::None", "GetNetworkConfig"]
    data = {}
    for kw in kw_list:
        data[kw] = find_string_xrefs(kw)
    log("5_gameservertype_refs", data)
except Exception as e:
    err("5_gameservertype", e)

# ---------------------------------------------------------------------------
# 6. Find SetNesysGameServerInfo function definition and decompile
# ---------------------------------------------------------------------------
try:
    # find func named SetNesysGameServerInfo
    setfunc = None
    for func_ea in idautils.Functions():
        if fname(func_ea) == "SetNesysGameServerInfo":
            setfunc = func_ea
            break
    if setfunc:
        body = decompile(setfunc)
        log("6_setnesysgameserverinfo_decompiled",
            {"function_ea": hex(setfunc), "name": "SetNesysGameServerInfo",
             "decompiled": body})
    else:
        # fall back: find callers via string refs and find proximate functions
        log("6_setnesysgameserverinfo_decompiled",
            {"error": "no named function; see section 1"})
except Exception as e:
    err("6_setnesysgameserverinfo", e)

results["status"] = "SUCCESS"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("ANALYSIS_COMPLETE: %s" % OUT)
print("STATUS: %s" % results["status"])
print("SECTIONS: %d" % len(results["sections"]))
print("ERRORS: %d" % len(results["errors"]))
try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass
