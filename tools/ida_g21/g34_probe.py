"""IDA database probe - check if analysis is available."""
import json
import os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g34_probe.json"

import ida_ida
import ida_auto
import ida_nalt
import idautils
import idc

probe = {"status": "RUNNING"}

try:
    probe["min_ea"] = hex(ida_ida.inf_get_min_ea())
    probe["max_ea"] = hex(ida_ida.inf_get_max_ea())
    probe["is_64"] = ida_ida.inf_is_64bit()
    probe["input_path"] = ida_nalt.get_input_file_path()
except Exception as e:
    probe["ida_info_error"] = str(e)

try:
    func_count = len(list(idautils.Functions()))
    probe["function_count"] = func_count
except Exception as e:
    probe["function_count_error"] = str(e)

try:
    str_count = len(list(idautils.Strings()))
    probe["string_count"] = str_count
except Exception as e:
    probe["string_count_error"] = str(e)

# Try auto_wait with timeout
try:
    probe["auto_wait_starting"] = True
    r = ida_auto.auto_wait()
    probe["auto_wait_result"] = repr(r)
    probe["auto_wait_complete"] = True
    
    # Now recount
    probe["functions_after_auto"] = len(list(idautils.Functions()))
    probe["strings_after_auto"] = len(list(idautils.Strings()))
except Exception as e:
    probe["auto_wait_error"] = str(e)

# If strings available, try to find key ones
if probe.get("strings_after_auto", 0) > 0:
    found = []
    for s_ea in idautils.Strings():
        try:
            s = idc.get_strlit_contents(s_ea)
            if s:
                s = s.decode('utf-8', errors='ignore')
                if any(kw in s for kw in ["MatchingServer", "IsOnline", "CertError", "nesys_games", "RequestNetworkInfo"]):
                    found.append({"ea": hex(s_ea), "value": s[:100]})
                    if len(found) >= 20:
                        break
        except:
            pass
    probe["key_strings_found"] = found

probe["status"] = "SUCCESS"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(probe, f, indent=2, default=str)

print(json.dumps(probe, indent=2, default=str))

try:
    import ida_pro
    ida_pro.qexit(0)
except: pass
