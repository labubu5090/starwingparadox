"""Tutorial-related function search in AcrGame-Win64-Shipping.exe IDA database.

Searches for:
1. Functions with names containing Tutorial, tutorial, GameData, game_data, Save, save
2. Functions with names containing BindHttp
3. String xrefs for IsTutorialProgress, Result_Timeover
4. Functions with names containing UserDataCheck

For each found function: address, name, basic block count, key string references.
"""
import json
import os
import traceback
from datetime import datetime, timezone

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g21_tutorial_search.json")

# Function name search patterns (case-insensitive substring match)
FUNC_NAME_PATTERNS = [
    "Tutorial", "tutorial",
    "GameData", "game_data", "Game_Data",
    "Save", "save",
    "BindHttp",
    "UserDataCheck", "user_data_check", "UserdataCheck",
]

# String xref search patterns (find strings containing these, trace xrefs)
STRING_XREF_PATTERNS = [
    "IsTutorialProgress",
    "Result_Timeover",
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
        "image_base": hex(ida_nalt.get_imagebase()),
        "functions_total": 0,
        "strings_total": 0,
        "func_name_matches": [],
        "string_xref_matches": [],
        "tutorial_functions": [],
        "gamedata_save_functions": [],
        "errors": [],
    }

    def log(msg):
        try:
            with open(os.path.join(OUT_DIR, "g21_tutorial_search.log"), "a", encoding="utf-8") as f:
                f.write(_utcnow() + "  " + str(msg) + "\n")
                f.flush()
        except Exception:
            pass

    image_base = ida_nalt.get_imagebase()

    log("waiting for auto-analysis...")
    ida_auto.auto_wait()
    log("auto-analysis complete")

    record["functions_total"] = len(list(idautils.Functions()))
    record["strings_total"] = len(list(idautils.Strings()))
    log("functions=%d strings=%d" % (record["functions_total"], record["strings_total"]))

    # Helper: get basic block count for a function via FlowChart
    def get_basic_block_count(func_ea):
        try:
            f = ida_funcs.get_func(func_ea)
            if not f:
                return 0
            count = 0
            for _ in idautils.FlowChart(f):
                count += 1
            return count
        except Exception:
            return 0

    # Helper: get string references within a function
    def get_func_string_refs(func_ea):
        refs = []
        try:
            f = ida_funcs.get_func(func_ea)
            if not f:
                return refs
            head = f.start_ea
            while head < f.end_ea:
                try:
                    for op_idx in range(2):
                        try:
                            op_val = idc.get_operand_value(head, op_idx)
                            if op_val and op_val != head and op_val > 0x1000:
                                s = idc.get_strlit_contents(op_val)
                                if s:
                                    decoded = s.decode('utf-8', errors='ignore')
                                    if 1 < len(decoded) < 500:
                                        refs.append({"ea": hex(op_val), "str": decoded[:200]})
                        except Exception:
                            pass
                except Exception:
                    pass
                head = idc.next_head(head, f.end_ea)
                if head == idc.BADADDR:
                    break
        except Exception:
            pass
        # Deduplicate
        seen = set()
        unique = []
        for r in refs:
            key = r["ea"]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique[:20]

    # =================================================================
    # PART 1: Search function names by pattern
    # =================================================================
    log("PART 1: searching function names...")
    func_count = 0
    for func_ea in idautils.Functions():
        fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
        fname_lower = fname.lower()
        matched_pattern = None
        for pat in FUNC_NAME_PATTERNS:
            if pat.lower() in fname_lower:
                matched_pattern = pat
                break
        if matched_pattern is None:
            continue

        func_count += 1
        rva = func_ea - image_base if func_ea >= image_base else 0
        bb_count = get_basic_block_count(func_ea)
        str_refs = get_func_string_refs(func_ea)
        f = ida_funcs.get_func(func_ea)
        fsize = f.size() if f else 0

        entry = {
            "address": hex(func_ea),
            "rva": hex(rva),
            "function_name": fname,
            "matched_pattern": matched_pattern,
            "basic_block_count": bb_count,
            "function_size": fsize,
            "key_string_refs": str_refs,
        }
        record["func_name_matches"].append(entry)
        log("  FUNC[%d]: %s @ %s bb=%d str_refs=%d" % (func_count, fname, hex(func_ea), bb_count, len(str_refs)))

    log("PART 1 complete: %d function name matches" % func_count)

    # =================================================================
    # PART 2: Search string xrefs for IsTutorialProgress and Result_Timeover
    # =================================================================
    log("PART 2: searching string xrefs...")
    xref_match_count = 0
    total_xrefs = 0
    for s_ea in idautils.Strings():
        try:
            s_raw = idc.get_strlit_contents(s_ea)
            if not s_raw:
                continue
            s = s_raw.decode('utf-8', errors='ignore')
        except Exception:
            continue

        matched_pattern = None
        for pat in STRING_XREF_PATTERNS:
            if pat.lower() in s.lower():
                matched_pattern = pat
                break
        if matched_pattern is None:
            continue

        # Found matching string, trace xrefs
        xrefs_to_string = []
        try:
            for xr in idautils.XrefsTo(s_ea):
                xref_ea = xr.frm
                func_ea = None
                try:
                    ff = ida_funcs.get_func(xref_ea)
                    if ff:
                        func_ea = ff.start_ea
                except Exception:
                    pass
                if func_ea is None:
                    try:
                        func_ea = idc.get_func_attr(xref_ea, idc.FUNCATTR_START)
                    except Exception:
                        pass

                func_name = ""
                func_rva = None
                bb_count = 0
                func_str_refs = []
                if func_ea and func_ea != idc.BADADDR:
                    func_name = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
                    func_rva = func_ea - image_base if func_ea >= image_base else None
                    bb_count = get_basic_block_count(func_ea)
                    func_str_refs = get_func_string_refs(func_ea)

                disasm = ""
                try:
                    disasm = idc.GetDisasm(xref_ea)
                except Exception:
                    pass

                xrefs_to_string.append({
                    "xref_ea": hex(xref_ea),
                    "xref_rva": hex(xref_ea - image_base) if xref_ea >= image_base else None,
                    "xref_type": xr.type,
                    "disasm": disasm,
                    "containing_function": func_name,
                    "function_start": hex(func_ea) if func_ea and func_ea != idc.BADADDR else None,
                    "function_rva": hex(func_rva) if func_rva is not None else None,
                    "basic_block_count": bb_count,
                    "key_string_refs": func_str_refs,
                })
                total_xrefs += 1
                if len(xrefs_to_string) >= 20:
                    break
        except Exception as e:
            log("  xref error: %s" % str(e))

        xref_match_count += 1
        record["string_xref_matches"].append({
            "matched_pattern": matched_pattern,
            "string_address": hex(s_ea),
            "string_rva": hex(s_ea - image_base) if s_ea >= image_base else None,
            "string_value": s[:500],
            "xref_count": len(xrefs_to_string),
            "xrefs": xrefs_to_string,
        })
        log("  XREF[%d]: pattern='%s' string='%s' xrefs=%d" % (xref_match_count, matched_pattern, s[:60], len(xrefs_to_string)))

    log("PART 2 complete: %d string matches, %d total xrefs" % (xref_match_count, total_xrefs))

    # =================================================================
    # PART 3: All tutorial-named functions
    # =================================================================
    log("PART 3: tutorial-named functions...")
    tutorial_names = []
    for func_ea in idautils.Functions():
        fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
        if "tutorial" in fname.lower():
            rva = func_ea - image_base if func_ea >= image_base else 0
            bb_count = get_basic_block_count(func_ea)
            f = ida_funcs.get_func(func_ea)
            fsize = f.size() if f else 0
            tutorial_names.append({
                "address": hex(func_ea),
                "rva": hex(rva),
                "function_name": fname,
                "basic_block_count": bb_count,
                "function_size": fsize,
            })
    record["tutorial_functions"] = tutorial_names
    log("PART 3: %d tutorial-named functions" % len(tutorial_names))

    # =================================================================
    # PART 4: GameData/Save/UserData/BindHttp in function names
    # =================================================================
    log("PART 4: GameData/Save/UserData/BindHttp functions...")
    gs_funcs = []
    for func_ea in idautils.Functions():
        fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
        fl = fname.lower()
        if any(kw in fl for kw in ["gamedata", "game_data", "save", "userdata", "user_data", "bindhttp"]):
            rva = func_ea - image_base if func_ea >= image_base else 0
            bb_count = get_basic_block_count(func_ea)
            f = ida_funcs.get_func(func_ea)
            fsize = f.size() if f else 0
            str_refs = get_func_string_refs(func_ea)
            gs_funcs.append({
                "address": hex(func_ea),
                "rva": hex(rva),
                "function_name": fname,
                "basic_block_count": bb_count,
                "function_size": fsize,
                "key_string_refs": str_refs[:10],
            })
    record["gamedata_save_functions"] = gs_funcs
    log("PART 4: %d GameData/Save/UserData/BindHttp functions" % len(gs_funcs))

    record["status"] = "SUCCESS"
    record["end_utc"] = _utcnow()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str, ensure_ascii=False)

    log("DONE; output=%s" % OUT_JSON)
    print("SEARCH_COMPLETE: %s" % OUT_JSON)
    print("FUNC_NAME_MATCHES: %d" % len(record["func_name_matches"]))
    print("STRING_XREF_MATCHES: %d" % len(record["string_xref_matches"]))
    print("TUTORIAL_FUNCTIONS: %d" % len(record["tutorial_functions"]))
    print("GAMEDATA_SAVE_FUNCTIONS: %d" % len(record["gamedata_save_functions"]))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:
        rec = {"status": "FATAL", "error": str(e), "traceback": traceback.format_exc(), "end_utc": _utcnow()}
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, default=str)
        code = 1
        print("FATAL: %s" % str(e))
    try:
        import ida_pro
        ida_pro.qexit(code)
    except Exception:
        pass