"""Final comprehensive tutorial-related search.
Covers ALL BindHttp*, Tutorial*, GameData*, Save*, UserDataCheck strings,
plus xref resolution for IsTutorialProgress and Result_Timeover."""
import json
import os
import traceback
from datetime import datetime, timezone

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g21_tutorial_final.json")

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

    image_base = ida_nalt.get_imagebase()
    record = {
        "status": "RUNNING",
        "start_utc": _utcnow(),
        "target": ida_nalt.get_input_file_path(),
        "image_base": hex(image_base),
        "functions_total": 0,
        "strings_total": 0,
        "sections": {},
        "errors": [],
    }

    def log(msg):
        try:
            with open(os.path.join(OUT_DIR, "g21_tutorial_final.log"), "a", encoding="utf-8") as f:
                f.write(_utcnow() + "  " + str(msg) + "\n")
                f.flush()
        except:
            pass

    ida_auto.auto_wait()
    record["functions_total"] = len(list(idautils.Functions()))
    record["strings_total"] = len(list(idautils.Strings()))
    log("functions=%d strings=%d" % (record["functions_total"], record["strings_total"]))

    def resolve_xrefs(ea, max_refs=20):
        """Get xrefs to an address and resolve their containing functions."""
        refs = []
        try:
            for xr in idautils.XrefsTo(ea):
                from_ea = xr.frm
                func_ea = None
                fname = ""
                try:
                    ff = ida_funcs.get_func(from_ea)
                    if ff:
                        func_ea = ff.start_ea
                        fname = ida_funcs.get_func_name(ff.start_ea) or ida_name.get_name(ff.start_ea) or ""
                except:
                    pass
                if not fname and func_ea is None:
                    try:
                        fea = idc.get_func_attr(from_ea, idc.FUNCATTR_START)
                        if fea and fea != idc.BADADDR:
                            func_ea = fea
                            fname = ida_funcs.get_func_name(fea) or ida_name.get_name(fea) or ""
                    except:
                        pass
                disasm = ""
                try:
                    disasm = idc.GetDisasm(from_ea)
                except:
                    pass
                refs.append({
                    "from": hex(from_ea),
                    "from_rva": hex(from_ea - image_base) if from_ea >= image_base else None,
                    "type": xr.type,
                    "containing_function": fname,
                    "func_start": hex(func_ea) if func_ea else None,
                    "disasm": disasm[:120],
                })
                if len(refs) >= max_refs:
                    break
        except:
            pass
        return refs

    def get_func_bb_count(fea):
        try:
            f = ida_funcs.get_func(fea)
            if f:
                return sum(1 for _ in idautils.FlowChart(f))
        except:
            pass
        return 0

    def get_func_strings(fea, max_strs=15):
        """Get string references from code within a function."""
        strs = []
        seen = set()
        try:
            f = ida_funcs.get_func(fea)
            if not f:
                return strs
            head = f.start_ea
            while head < f.end_ea:
                try:
                    for op_idx in range(2):
                        try:
                            ov = idc.get_operand_value(head, op_idx)
                            if ov and ov != head and ov > 0x1000:
                                s = idc.get_strlit_contents(ov)
                                if s:
                                    d = s.decode('utf-8', errors='ignore')
                                    if 1 < len(d) < 500 and ov not in seen:
                                        seen.add(ov)
                                        strs.append({"ea": hex(ov), "str": d[:200]})
                        except:
                            pass
                except:
                    pass
                head = idc.next_head(head, f.end_ea)
                if head == idc.BADADDR:
                    break
        except:
            pass
        return strs[:max_strs]

    # ================================================================
    # SECTION A: Comprehensive raw byte scan for ALL target patterns
    # ================================================================
    log("SECTION A: comprehensive byte scan...")

    BYTE_SEARCH_GROUPS = {
        "BindHttp": [],       # Will hold ALL BindHttp* strings
        "Tutorial": [],       # All Tutorial* strings
        "GameData": [],       # All GameData* strings (including HttpGameData)
        "UserDataCheck": [],  # UserDataCheck strings
        "IsTutorialProgress": [],
        "Result_Timeover": [],
        "Save": [],           # Save-related strings
    }

    # Find .rdata
    rdata_start = None
    rdata_end = None
    for seg_ea in idautils.Segments():
        seg_obj = ida_segment.getseg(seg_ea)
        name = ida_segment.get_segm_name(seg_obj) or ""
        if ".rdata" in name:
            rdata_start = seg_obj.start_ea
            rdata_end = seg_obj.end_ea
            break

    if rdata_start is not None:
        log("Scanning .rdata: %s - %s" % (hex(rdata_start), hex(rdata_end)))
        # Scan .rdata in chunks for all target prefixes
        prefixes = {
            b"BindHttp": "BindHttp",
            b"HttpGameData": "GameData",
            b"Tutorial": "Tutorial",
            b"IsTutorialProgress": "IsTutorialProgress",
            b"Result_Timeover": "Result_Timeover",
            b"UserDataCheck": "UserDataCheck",
            b"Save": "Save",
            b"save": "Save",
        }
        pos = rdata_start
        chunk_num = 0
        while pos < rdata_end:
            chunk_size = min(0x1000000, rdata_end - pos)
            try:
                chunk = ida_bytes.get_bytes(pos, chunk_size)
                if not chunk:
                    pos += chunk_size
                    continue
                for prefix_bytes, group_name in prefixes.items():
                    idx = 0
                    while True:
                        idx = chunk.find(prefix_bytes, idx)
                        if idx < 0:
                            break
                        ea = pos + idx
                        # Read full null-terminated string
                        full_str = ""
                        try:
                            raw = ida_bytes.get_bytes(ea, min(512, rdata_end - ea))
                            if raw:
                                null_pos = raw.find(b'\x00')
                                if 0 < null_pos <= 500:
                                    full_str = raw[:null_pos].decode('utf-8', errors='ignore')
                                elif null_pos < 0:
                                    full_str = raw.decode('utf-8', errors='ignore')[:200]
                        except:
                            pass
                        if full_str:
                            BYTE_SEARCH_GROUPS[group_name].append({
                                "address": hex(ea),
                                "rva": hex(ea - image_base) if ea >= image_base else None,
                                "full_string": full_str,
                            })
                        idx += len(prefix_bytes)
            except Exception as e:
                log("Chunk error at %s: %s" % (hex(pos), str(e)))
            pos += chunk_size
            chunk_num += 1
            if chunk_num % 10 == 0:
                log("  scanned %d chunks, pos=%s" % (chunk_num, hex(pos)))

    for group_name, entries in BYTE_SEARCH_GROUPS.items():
        log("  %s: %d raw matches" % (group_name, len(entries)))

    record["sections"]["A_byte_scan"] = BYTE_SEARCH_GROUPS

    # ================================================================
    # SECTION B: For each unique BindHttp string, get xrefs
    # ================================================================
    log("SECTION B: BindHttp xrefs...")
    bindhttp_xrefs = []
    seen_addrs = set()
    for entry in BYTE_SEARCH_GROUPS.get("BindHttp", []):
        ea_str = entry["address"]
        if ea_str in seen_addrs:
            continue
        seen_addrs.add(ea_str)
        ea = int(ea_str, 16)
        xrefs = resolve_xrefs(ea)
        # Also try xrefs to nearby addresses (pointers)
        for offset in [-8, -4, 4, 8]:
            nearby = ea + offset
            if rdata_start and rdata_start <= nearby < rdata_end:
                xrefs += resolve_xrefs(nearby, 5)
        # Deduplicate xrefs
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        bindhttp_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
        })
    record["sections"]["B_bindhttp_xrefs"] = bindhttp_xrefs
    log("BindHttp xref entries: %d" % len(bindhttp_xrefs))

    # ================================================================
    # SECTION C: TutorialProgress / IsTutorialProgress xrefs
    # ================================================================
    log("SECTION C: TutorialProgress xrefs...")
    tutorial_xrefs = []
    for entry in BYTE_SEARCH_GROUPS.get("Tutorial", []):
        ea = int(entry["address"], 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        tutorial_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
        })
    for entry in BYTE_SEARCH_GROUPS.get("IsTutorialProgress", []):
        ea = int(entry["address"], 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        tutorial_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
            "is_exact_match": True,
        })
    record["sections"]["C_tutorial_xrefs"] = tutorial_xrefs
    log("Tutorial xref entries: %d" % len(tutorial_xrefs))

    # ================================================================
    # SECTION D: Result_Timeover xrefs
    # ================================================================
    log("SECTION D: Result_Timeover xrefs...")
    timeover_xrefs = []
    for entry in BYTE_SEARCH_GROUPS.get("Result_Timeover", []):
        ea = int(entry["address"], 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        timeover_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
        })
    record["sections"]["D_timeover_xrefs"] = timeover_xrefs
    log("Result_Timeover xref entries: %d" % len(timeover_xrefs))

    # ================================================================
    # SECTION E: UserDataCheck xrefs
    # ================================================================
    log("SECTION E: UserDataCheck xrefs...")
    userdata_xrefs = []
    for entry in BYTE_SEARCH_GROUPS.get("UserDataCheck", []):
        ea = int(entry["address"], 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        userdata_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
        })
    record["sections"]["E_userdata_xrefs"] = userdata_xrefs
    log("UserDataCheck xref entries: %d" % len(userdata_xrefs))

    # ================================================================
    # SECTION F: GameData xrefs
    # ================================================================
    log("SECTION F: GameData xrefs...")
    gamedata_xrefs = []
    seen_addrs = set()
    for entry in BYTE_SEARCH_GROUPS.get("GameData", []):
        ea_str = entry["address"]
        if ea_str in seen_addrs:
            continue
        seen_addrs.add(ea_str)
        ea = int(ea_str, 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        gamedata_xrefs.append({
            **entry,
            "xref_count": len(unique_xrefs),
            "xrefs": unique_xrefs[:15],
        })
    record["sections"]["F_gamedata_xrefs"] = gamedata_xrefs
    log("GameData xref entries: %d" % len(gamedata_xrefs))

    # ================================================================
    # SECTION G: Save-related xrefs
    # ================================================================
    log("SECTION G: Save xrefs...")
    save_xrefs = []
    seen_addrs = set()
    for entry in BYTE_SEARCH_GROUPS.get("Save", []):
        s = entry["full_string"]
        # Filter: only keep interesting Save strings (skip generic ones)
        sl = s.lower()
        if not any(kw in sl for kw in ["save", "option/save", "customizesave"]):
            continue
        ea_str = entry["address"]
        if ea_str in seen_addrs:
            continue
        seen_addrs.add(ea_str)
        ea = int(ea_str, 16)
        xrefs = resolve_xrefs(ea)
        seen_xrefs = set()
        unique_xrefs = []
        for x in xrefs:
            k = x["from"]
            if k not in seen_xrefs:
                seen_xrefs.add(k)
                unique_xrefs.append(x)
        if len(unique_xrefs) > 0:  # Only keep strings with xrefs
            save_xrefs.append({
                **entry,
                "xref_count": len(unique_xrefs),
                "xrefs": unique_xrefs[:15],
            })
    record["sections"]["G_save_xrefs"] = save_xrefs
    log("Save xref entries: %d" % len(save_xrefs))

    # ================================================================
    # SECTION H: For key xref-containing functions, gather details
    # ================================================================
    log("SECTION H: function details for key xrefs...")
    key_func_eas = set()
    for section_key in ["B_bindhttp_xrefs", "C_tutorial_xrefs", "D_timeover_xrefs",
                         "E_userdata_xrefs", "F_gamedata_xrefs"]:
        for entry in record["sections"].get(section_key, []):
            for xref in entry.get("xrefs", []):
                fs = xref.get("func_start")
                if fs:
                    try:
                        key_func_eas.add(int(fs, 16))
                    except:
                        pass

    func_details = {}
    for fea in list(key_func_eas)[:50]:
        fname = ida_funcs.get_func_name(fea) or ida_name.get_name(fea) or hex(fea)
        bb = get_func_bb_count(fea)
        f = ida_funcs.get_func(fea)
        fsize = f.size() if f else 0
        strs = get_func_strings(fea)
        func_details[hex(fea)] = {
            "name": fname,
            "rva": hex(fea - image_base) if fea >= image_base else None,
            "basic_block_count": bb,
            "function_size": fsize,
            "key_string_refs": strs,
        }
    record["sections"]["H_key_function_details"] = func_details
    log("Key function details: %d functions" % len(func_details))

    record["status"] = "SUCCESS"
    record["end_utc"] = _utcnow()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str, ensure_ascii=False)

    log("DONE; output=%s" % OUT_JSON)
    print("FINAL_SEARCH_COMPLETE")
    print("BINDHTTP_ENTRIES: %d" % len(bindhttp_xrefs))
    print("TUTORIAL_ENTRIES: %d" % len(tutorial_xrefs))
    print("TIMEOVER_ENTRIES: %d" % len(timeover_xrefs))
    print("USERDATA_ENTRIES: %d" % len(userdata_xrefs))
    print("GAMEDATA_ENTRIES: %d" % len(gamedata_xrefs))
    print("SAVE_ENTRIES: %d" % len(save_xrefs))
    print("KEY_FUNCTION_DETAILS: %d" % len(func_details))
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