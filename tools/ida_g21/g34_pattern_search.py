"""IDA binary pattern search - finds string literals in .rdata without auto analysis."""
import json
import os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_pattern.json"

try:
    import ida_ida
    import ida_nalt
    import ida_bytes
    import ida_segment
    import ida_funcs
    import ida_name
    import ida_search
    import idc
    import idautils
except ImportError as e:
    with open(OUT, "w") as f:
        json.dump({"error": str(e)}, f)
    import ida_pro
    ida_pro.qexit(1)

results = {"status": "RUNNING", "found": {}, "errors": []}

SEARCH_TERMS = [
    b"MatchingServer",
    b"IsOnline",
    b"UseConfigMatchingServer",
    b"DefaultMatchingServerAddress",
    b"initialize Nesys before",
    b"Error No Matching",
    b"nesys_games",
    b"LCOMMAND",
    b"SCOMMAND",
    b"CLIENT_START",
    b"CERT_ERROR",
    b"LOCALNW_INFO",
    b"RequestNetworkInfo",
    b"UCPP_NesysControl",
    b"GameModeBoot",
    b"NesysControlErrorMessage",
    b"CertError",
    b"certificate",
    b"OpenKey",
    b"SystemDataCheck",
    b"CheckVersion",
    b"UseConfigHttpServer",
    b"HttpServerAddress",
    b"MatchingServerType",
    b"commandLine value",
    b"ConnectNamedPipe",
    b"CreateNamedPipe",
    b"pipe",
    b"address from Config",
    b"address from NESYS",
    b"Decide connect",
    b"NesysRequest",
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

# Find .rdata segment
rdata_start = None
rdata_end = None
for seg in idautils.Segments():
    seg_obj = ida_segment.getseg(seg)
    name = ida_segment.get_segm_name(seg_obj) or ""
    if ".rdata" in name:
        rdata_start = seg_obj.start_ea
        rdata_end = seg_obj.end_ea
        results["rdata"] = {"start": hex(rdata_start), "end": hex(rdata_end), "name": name}
        break

if rdata_start is None:
    # Try first segment
    for seg in idautils.Segments():
        seg_obj = ida_segment.getseg(seg)
        name = ida_segment.get_segm_name(seg_obj) or ""
        if "data" in name.lower() or "rdata" in name.lower():
            rdata_start = seg_obj.start_ea
            rdata_end = seg_obj.end_ea
            results["rdata"] = {"start": hex(rdata_start), "end": hex(rdata_end), "name": name}
            break

if rdata_start is None:
    results["errors"].append("No data segment found")
    results["status"] = "FAILED"
else:
    # Use ida_search for each term
    for term in SEARCH_TERMS:
        try:
            pattern = ida_search.char_array_t(len(term))
            for i, b in enumerate(term):
                pattern[i] = b

            ea = rdata_start
            found_count = 0
            max_find = 5
            while ea < rdata_end and found_count < max_find:
                result_ea = ida_search.find_binary(ea, rdata_end, term.hex(), 16, ida_search.SEARCH_DOWN)
                if result_ea == idc.BADADDR:
                    break
                # Found match - try to get the full string
                try:
                    s = idc.get_strlit_contents(result_ea)
                    if s:
                        s = s.decode('utf-8', errors='ignore')
                    else:
                        # Read raw bytes
                        raw = ida_bytes.get_bytes(result_ea, min(200, rdata_end - result_ea))
                        if raw:
                            # Try to find null terminator
                            null_pos = raw.find(b'\x00')
                            if null_pos > 0:
                                s = raw[:null_pos].decode('utf-8', errors='ignore')
                            else:
                                s = raw.decode('utf-8', errors='ignore')
                        else:
                            s = "(unreadable)"
                except:
                    s = "(error)"

                term_str = term.decode('utf-8', errors='ignore')
                if term_str not in results["found"]:
                    results["found"][term_str] = []
                results["found"][term_str].append({
                    "ea": hex(result_ea),
                    "string": s[:200] if s else "(none)",
                })
                found_count += 1
                ea = result_ea + 1
        except Exception as e:
            results["errors"].append("%s: %s" % (term.decode('utf-8', errors='ignore'), str(e)))

    results["status"] = "SUCCESS"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("STATUS: %s" % results["status"])
print("FOUND %d search terms" % len(results.get("found", {})))
for term, refs in results.get("found", {}).items():
    print("  %s: %d hits" % (term, len(refs)))
    for r in refs[:2]:
        print("    %s: %s" % (r["ea"], r["string"][:80]))

try:
    import ida_pro
    ida_pro.qexit(0)
except: pass
