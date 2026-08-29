"""G21 IDA offline diagnostics script (corrected for IDA 9.3 API + local binding).

Runs inside IDA batch/autonomous mode. Writes JSON diagnostics + a text
diagnostic log to absolute project-controlled paths. Every metadata field
is collected with independent exception handling; non-critical failures are
recorded, not fatal. Required-module unavailability and auto-analysis
failure are fatal.

NO network access. Does NOT execute or debug the target. Run with
process-local symbol env pointing only at a local symbols directory.
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone

OUT_JSON = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\ida_diagnostics.json"
OUT_TXT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\ida_diagnostics.txt"
MARKER = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\ida_diagnostics.complete"


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def _fmt_exc(exc):
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def main():
    record = {
        "status": "RUNNING",
        "script": os.path.basename(__file__),
        "out_json": OUT_JSON,
        "out_txt": OUT_TXT,
        "start_utc": _utcnow(),
        "fatal": None,
        "nonfatal_errors": {},
    }

    def log(msg, data=None):
        line = _utcnow() + "  " + str(msg) + ("  " + str(data) if data is not None else "")
        with open(OUT_TXT, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()

    def rec_nonfatal(key, exc):
        record.setdefault("nonfatal_errors", {})[key] = _fmt_exc(exc)
        log("nonfatal", key)

    log("script start")

    # ---- Local module-map import binding (no globals()) ----
    required_modules = [
        "ida_auto", "ida_bytes", "ida_entry", "ida_funcs", "ida_ida",
        "ida_idaapi", "ida_kernwin", "ida_loader", "ida_nalt", "ida_segment",
        "ida_ua", "ida_xref", "idautils", "idc",
    ]
    optional_modules = ["ida_hexrays"]

    modules = {}
    import_errors = []
    for m in required_modules + optional_modules:
        try:
            modules[m] = __import__(m)
        except Exception as exc:  # noqa: BLE001
            modules[m] = None
            import_errors.append({
                "module": m,
                "required": m in required_modules,
                "exception_type": type(exc).__name__,
                "message": str(exc),
            })
    # Bind local short names
    ida_auto = modules["ida_auto"]
    ida_bytes = modules["ida_bytes"]
    ida_entry = modules["ida_entry"]
    ida_funcs = modules["ida_funcs"]
    ida_ida = modules["ida_ida"]
    ida_idaapi = modules["ida_idaapi"]
    ida_kernwin = modules["ida_kernwin"]
    ida_loader = modules["ida_loader"]
    ida_nalt = modules["ida_nalt"]
    ida_segment = modules["ida_segment"]
    ida_ua = modules["ida_ua"]
    ida_xref = modules["ida_xref"]
    idautils = modules["idautils"]
    idc = modules["idc"]
    ida_hexrays = modules["ida_hexrays"]

    record["idapython_available"] = ida_idaapi is not None
    record["import_errors"] = import_errors
    # required-module gate
    missing_required = [e["module"] for e in import_errors if e["required"]]
    if missing_required:
        record["fatal"] = "REQUIRED_IMPORT_UNAVAILABLE: " + ",".join(missing_required)
    log("import binding complete; idapython=%s" % record["idapython_available"])

    # ---- Version (independent fallback) ----
    kernel_version = None
    sdk_version = None
    try:
        getter = getattr(ida_kernwin, "get_kernel_version", None) if ida_kernwin else None
        if callable(getter):
            kernel_version = str(getter())
    except Exception as exc:  # noqa: BLE001
        rec_nonfatal("kernel_version", exc)
    try:
        sdk_version = getattr(ida_idaapi, "IDA_SDK_VERSION", None) if ida_idaapi else None
        if sdk_version is None and ida_ida is not None:
            sdk_version = getattr(ida_ida, "IDA_SDK_VERSION", None)
    except Exception as exc:  # noqa: BLE001
        rec_nonfatal("sdk_version", exc)
    record["ida_kernel_version"] = kernel_version or "unavailable"
    record["ida_sdk_version"] = sdk_version or "unavailable"
    log("version", record["ida_kernel_version"])

    # ---- Targets / database / processor ----
    def get(fn):
        try:
            return None, fn()
        except Exception as exc:  # noqa: BLE001
            return exc, None

    _e, _v = get(lambda: ida_nalt.get_input_file_path())
    record["input_path_reported_by_ida"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("input_path", _e)
    _e, _v = get(lambda: ida_nalt.get_root_filename())
    record["root_filename"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("root_filename", _e)
    _e, _v = get(lambda: hex(ida_nalt.get_imagebase()))
    record["image_base"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("image_base", _e)
    _e, _v = get(lambda: hex(ida_ida.inf_get_min_ea()))
    record["min_ea"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("min_ea", _e)
    _e, _v = get(lambda: hex(ida_ida.inf_get_max_ea()))
    record["max_ea"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("max_ea", _e)
    _e, _v = get(lambda: ida_ida.inf_get_procname())
    record["processor_name"] = _v if _e is None else None
    if _e is not None:
        rec_nonfatal("processor_name", _e)
    _e, _v = get(lambda: ida_ida.inf_is_64bit())
    record["bits"] = (64 if _v else 32) if _e is None else "unknown"
    if _e is not None:
        rec_nonfatal("bits", _e)

    # database path via idc (primary) - do not fabricate from filename
    db_path_reported = None
    try:
        getter = getattr(idc, "get_idb_path", None)
        if callable(getter):
            db_path_reported = str(getter())
    except Exception as exc:  # noqa: BLE001
        rec_nonfatal("database_path", exc)
    record["database_path_reported_by_ida"] = db_path_reported
    record["database_exists"] = False  # verified by runner on disk

    # ---- Auto-analysis ----
    auto_wait_return_repr = None
    auto_wait_exception = None
    fc_after = 0
    try:
        r = ida_auto.auto_wait()
        auto_wait_return_repr = repr(r)
        fc_after = len(list(idautils.Functions()))
    except Exception as exc:  # noqa: BLE001
        auto_wait_exception = _fmt_exc(exc)
    record["auto_wait_called"] = ida_auto is not None
    record["auto_wait_return_repr"] = auto_wait_return_repr
    record["auto_wait_exception"] = auto_wait_exception
    record["function_count_after_auto_wait"] = fc_after
    if auto_wait_exception:
        record["analysis_completion_classification"] = "FAILED"
        record["fatal"] = record["fatal"] or "AUTO_ANALYSIS_FAILED"
    elif fc_after > 0:
        record["analysis_completion_classification"] = "COMPLETE"
    else:
        record["analysis_completion_classification"] = "INDETERMINATE"
    log("auto analysis", record["analysis_completion_classification"])

    # ---- Counts using verified iterators ----
    def funclist():
        return list(idautils.Functions())

    def named_count():
        n = 0
        for f in idautils.Functions():
            try:
                nm = ida_funcs.get_func_name(f) or ida_name_get(f)
                if nm:
                    n += 1
            except Exception:  # noqa: BLE001
                pass
        return n

    def ida_name_get(ea):
        try:
            return ida_funcs.get_func_name(ea)
        except Exception:  # noqa: BLE001
            return None

    funcs = []
    _e, _v = get(funclist)
    if _e is not None:
        rec_nonfatal("functions", _e)
    elif isinstance(_v, Exception):
        rec_nonfatal("functions", _v)
    else:
        funcs = _v if isinstance(_v, list) else (list(_v) if _v else [])
    record["function_count"] = len(funcs)
    try:
        record["named_function_count"] = len([f for f in funcs if ida_funcs.get_func_name(f)])
    except Exception as exc:  # noqa: BLE001
        record["named_function_count"] = None
        rec_nonfatal("named_function_count", exc)
    _e, _v = get(lambda: len(list(idautils.Segments())))
    if _e is not None:
        record["segment_count"] = None
        rec_nonfatal("segments", _e)
    else:
        record["segment_count"] = _v
    _e, _v = get(lambda: len(list(idautils.Strings())))
    if _e is not None:
        record["string_count"] = None
        rec_nonfatal("strings", _e)
    else:
        record["string_count"] = _v
    _e, _v = get(lambda: len(list(idautils.Entries())))
    if _e is not None:
        record["entry_count"] = None
        rec_nonfatal("entries", _e)
    else:
        record["entry_count"] = _v
    _e, _v = get(lambda: ida_nalt.get_import_module_qty())
    if _e is not None:
        record["import_module_qty"] = None
        rec_nonfatal("import_module_qty", _e)
    else:
        record["import_module_qty"] = _v

    # ---- Decompiler (optional) ----
    decomp_avail = False
    if ida_hexrays is not None:
        try:
            decomp_avail = bool(ida_hexrays.init_hexrays_plugin())
        except Exception as exc:  # noqa: BLE001
            rec_nonfatal("hexrays_initialization", exc)
    record["decompiler_available"] = decomp_avail
    log("decompiler", decomp_avail)

    record["end_utc"] = _utcnow()
    record["status"] = "SUCCESS" if not record.get("fatal") else "FATAL"
    if not record["fatal"]:
        if not record.get("function_count") or not record.get("segment_count"):
            record["fatal"] = "NO_ANALYSIS_EVIDENCE"
            record["status"] = "FATAL"
    log("final status", record["status"])

    with open(OUT_TXT, "a", encoding="utf-8") as f:
        f.write("=== SUMMARY ===\n")
        for k, v in record.items():
            f.write("%-40s %s\n" % (k, str(v)[:200]))
        f.flush()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str)
        f.flush()
    try:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"status": record["status"], "end_utc": record["end_utc"]}, f)
            f.flush()
    except Exception as exc:  # noqa: BLE001
        record["marker_error"] = str(exc)
    return 1 if record["status"] == "FATAL" else 0


if __name__ == "__main__":
    code = main()
    try:
        import ida_pro
        ida_pro.qexit(code)
    except Exception:  # noqa: BLE001
        try:
            import ida_kernwin
            ida_kernwin.close_database(False)
        except Exception:  # noqa: BLE001
            pass
