"""Deep tutorial/binding/save search - scans both IDA string table AND raw bytes."""
import json
import os
import traceback
from datetime import datetime, timezone

OUT_DIR = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out"
OUT_JSON = os.path.join(OUT_DIR, "g21_tutorial_deep.json")

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
        "start_utc": _utcnow(),
        "target": ida_nalt.get_input_file_path(),
        "image_base": hex(ida_nalt.get_imagebase()),
        "functions_total": 0,
        "strings_total": 0,
        "ida_string_matches": [],
        "func_name_matches": [],
        "xref_matches": [],
        "byte_scan_matches": [],
        "errors": [],
    }

    def log(msg):
        try:
            with open(os.path.join(OUT_DIR, "g21_tutorial_deep.log"), "a", encoding="utf-8") as f:
                f.write(_utcnow() + "  " + str(msg) + "\n")
                f.flush()
        except:
            pass

    image_base = ida_nalt.get_imagebase()

    # Force auto-analysis
    log("forcing auto_wait...")
    ida_auto.auto_wait()
    log("auto_wait done")

    record["functions_total"] = len(list(idautils.Functions()))
    record["strings_total"] = len(list(idautils.Strings()))
    log("functions=%d strings=%d" % (record["functions_total"], record["strings_total"]))

    # Search patterns for IDA string table
    SEARCH_KEYWORDS = [
        "Tutorial", "tutorial", "TUTORIAL",
        "GameData", "game_data", "Game_Data",
        "BindHttp", "bind_http",
        "UserDataCheck", "user_data_check",
        "IsTutorialProgress", "Result_Timeover",
        "SaveData", "save_data", "SaveGame", "save_game",
        "OptionSave", "option_save",
        "PlayerSave", "player_save",
        "TutorialProgress", "tutorial_progress",
        "TutorialResult", "tutorial_result",
        "Timeover", "time_over", "timeOver",
        "UserData", "user_data",
    ]

    # =================================================================
    # Search 1: IDA string table
    # =================================================================
    log("Search 1: IDA string table for all keywords...")
    for s_ea in idautils.Strings():
        try:
            s_raw = idc.get_strlit_contents(s_ea)
            if not s_raw:
                continue
            s = s_raw.decode('utf-8', errors='ignore')
        except:
            continue
        sl = s.lower()
        for kw in SEARCH_KEYWORDS:
            if kw.lower() in sl:
                # Get xrefs
                xrefs = []
                try:
                    for xr in idautils.XrefsTo(s_ea):
                        func_ea = None
                        fname = ""
                        try:
                            ff = ida_funcs.get_func(xr.frm)
                            if ff:
                                func_ea = ff.start_ea
                                fname = ida_funcs.get_func_name(ff.start_ea) or ida_name.get_name(ff.start_ea) or ""
                        except:
                            pass
                        xrefs.append({
                            "from": hex(xr.frm),
                            "type": xr.type,
                            "function": fname,
                            "func_start": hex(func_ea) if func_ea else None,
                        })
                        if len(xrefs) >= 10:
                            break
                except:
                    pass

                record["ida_string_matches"].append({
                    "keyword": kw,
                    "string_address": hex(s_ea),
                    "string_rva": hex(s_ea - image_base) if s_ea >= image_base else None,
                    "string_value": s[:300],
                    "xref_count": len(xrefs),
                    "xrefs": xrefs,
                })
                log("  STR: kw='%s' ea=%s xrefs=%d val='%s'" % (kw, hex(s_ea), len(xrefs), s[:80]))
                break  # one keyword per string

    log("IDA string matches: %d" % len(record["ida_string_matches"]))

    # =================================================================
    # Search 2: Function names (comprehensive)
    # =================================================================
    log("Search 2: function names...")
    for func_ea in idautils.Functions():
        fname = ida_funcs.get_func_name(func_ea) or ida_name.get_name(func_ea) or ""
        fl = fname.lower()
        matched_kw = None
        for kw in ["tutorial", "gamedata", "game_data", "save", "bindhttp",
                     "userdata", "user_data", "timeover"]:
            if kw in fl:
                matched_kw = kw
                break
        if matched_kw:
            rva = func_ea - image_base if func_ea >= image_base else 0
            f = ida_funcs.get_func(func_ea)
            fsize = f.size() if f else 0

            # Basic block count
            bb = 0
            try:
                for _ in idautils.FlowChart(f):
                    bb += 1
            except:
                pass

            record["func_name_matches"].append({
                "address": hex(func_ea),
                "rva": hex(rva),
                "function_name": fname,
                "matched_keyword": matched_kw,
                "basic_block_count": bb,
                "function_size": fsize,
            })
            if len(record["func_name_matches"]) < 30:
                log("  FN: kw='%s' %s @ %s bb=%d" % (matched_kw, fname, hex(func_ea), bb))

    log("Function name matches: %d" % len(record["func_name_matches"]))

    # =================================================================
    # Search 3: Raw byte scan in .rdata for specific target strings
    # =================================================================
    log("Search 3: raw byte scan for target strings...")
    TARGET_BYTE_STRINGS = [
        b"IsTutorialProgress",
        b"Result_Timeover",
        b"UserDataCheck",
        b"BindHttp",
        b"TutorialProgress",
        b"TutorialResult",
    ]

    # Find .rdata segment
    rdata_start = None
    rdata_end = None
    for seg_ea in idautils.Segments():
        seg_obj = ida_segment.getseg(seg_ea)
        name = ida_segment.get_segm_name(seg_obj) or ""
        if ".rdata" in name:
            rdata_start = seg_obj.start_ea
            rdata_end = seg_obj.end_ea
            log("  .rdata: %s - %s" % (hex(rdata_start), hex(rdata_end)))
            break

    if rdata_start is not None:
        for target_bytes in TARGET_BYTE_STRINGS:
            # Search in chunks to avoid huge reads
            pos = rdata_start
            found_count = 0
            while pos < rdata_end and found_count < 10:
                chunk_size = min(0x100000, rdata_end - pos)
                try:
                    chunk = ida_bytes.get_bytes(pos, chunk_size)
                    if not chunk:
                        pos += chunk_size
                        continue
                    idx = chunk.find(target_bytes)
                    if idx < 0:
                        pos += chunk_size
                        continue
                    while idx >= 0 and found_count < 10:
                        ea = pos + idx
                        # Read the full string
                        full_str = ""
                        try:
                            raw = ida_bytes.get_bytes(ea, min(256, rdata_end - ea))
                            if raw:
                                null_pos = raw.find(b'\x00')
                                if null_pos > 0:
                                    full_str = raw[:null_pos].decode('utf-8', errors='ignore')
                                else:
                                    full_str = raw.decode('utf-8', errors='ignore')[:200]
                        except:
                            pass

                        # Get xrefs
                        xrefs = []
                        try:
                            for xr in idautils.XrefsTo(ea):
                                func_ea = None
                                fname = ""
                                try:
                                    ff = ida_funcs.get_func(xr.frm)
                                    if ff:
                                        func_ea = ff.start_ea
                                        fname = ida_funcs.get_func_name(ff.start_ea) or ida_name.get_name(ff.start_ea) or ""
                                except:
                                    pass
                                xrefs.append({
                                    "from": hex(xr.frm),
                                    "function": fname,
                                    "func_start": hex(func_ea) if func_ea else None,
                                })
                                if len(xrefs) >= 10:
                                    break
                        except:
                            pass

                        record["byte_scan_matches"].append({
                            "target": target_bytes.decode('utf-8'),
                            "address": hex(ea),
                            "rva": hex(ea - image_base) if ea >= image_base else None,
                            "full_string": full_str[:300],
                            "xref_count": len(xrefs),
                            "xrefs": xrefs,
                        })
                        log("  BYTE: '%s' at %s xrefs=%d str='%s'" % (
                            target_bytes.decode('utf-8'), hex(ea), len(xrefs), full_str[:60]))
                        found_count += 1

                        # Continue search after this match
                        next_idx = chunk.find(target_bytes, idx + 1)
                        if next_idx < 0:
                            pos += chunk_size
                            break
                        idx = next_idx
                except Exception as e:
                    log("  byte scan error at %s: %s" % (hex(pos), str(e)))
                    pos += chunk_size

    log("Byte scan matches: %d" % len(record["byte_scan_matches"]))

    # =================================================================
    # Search 4: Also scan .text (code) for direct string references
    # =================================================================
    log("Search 4: wide string patterns in .data segments...")
    WIDE_PATTERNS = [
        b"T\x00u\x00t\x00o\x00r\x00i\x00a\x00l",  # "Tutorial" in UTF-16LE
        b"B\x00i\x00n\x00d\x00H\x00t\x00t\x00p",   # "BindHttp" in UTF-16LE
        b"S\x00a\x00v\x00e\x00D\x00a\x00t\x00a",    # "SaveData" in UTF-16LE
    ]

    for seg_ea in idautils.Segments():
        seg_obj = ida_segment.getseg(seg_ea)
        name = ida_segment.get_segm_name(seg_obj) or ""
        if ".rdata" not in name and ".data" not in name:
            continue
        seg_start = seg_obj.start_ea
        seg_end = seg_obj.end_ea
        seg_size = seg_end - seg_start
        if seg_size > 0x20000000:  # skip huge segments
            continue

        for wp in WIDE_PATTERNS:
            pos = seg_start
            while pos < seg_end:
                chunk_size = min(0x1000000, seg_end - pos)
                try:
                    chunk = ida_bytes.get_bytes(pos, chunk_size)
                    if not chunk:
                        pos += chunk_size
                        continue
                    idx = chunk.find(wp)
                    if idx < 0:
                        pos += chunk_size
                        continue
                    ea = pos + idx
                    # Read full string
                    full_str = ""
                    try:
                        raw = ida_bytes.get_bytes(ea, min(256, seg_end - ea))
                        if raw:
                            # Decode as UTF-16LE
                            decoded = raw.decode('utf-16-le', errors='ignore')
                            null_pos = decoded.find('\x00')
                            if null_pos > 0:
                                full_str = decoded[:null_pos]
                            else:
                                full_str = decoded[:100]
                    except:
                        pass

                    record["byte_scan_matches"].append({
                        "target": wp.decode('utf-16-le'),
                        "encoding": "UTF-16LE",
                        "segment": name,
                        "address": hex(ea),
                        "rva": hex(ea - image_base) if ea >= image_base else None,
                        "full_string": full_str[:300],
                        "xref_count": 0,
                        "xrefs": [],
                    })
                    log("  WIDE: '%s' at %s in %s" % (wp.decode('utf-16-le'), hex(ea), name))
                    pos = ea + len(wp)
                except Exception as e:
                    pos += chunk_size

    log("Wide pattern scan complete")

    record["status"] = "SUCCESS"
    record["end_utc"] = _utcnow()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str, ensure_ascii=False)

    log("DONE; output=%s" % OUT_JSON)
    print("DEEP_SEARCH_COMPLETE")
    print("IDA_STRING_MATCHES: %d" % len(record["ida_string_matches"]))
    print("FUNC_NAME_MATCHES: %d" % len(record["func_name_matches"]))
    print("BYTE_SCAN_MATCHES: %d" % len(record["byte_scan_matches"]))
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