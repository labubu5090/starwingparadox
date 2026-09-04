import idaapi
import ida_hexrays
import ida_name
import ida_bytes
import ida_funcs
import ida_nalt
import idautils
import json
import os

STRTYPE_C = ida_nalt.STRTYPE_C

def get_func_string_refs(func):
    refs = []
    visited = set()
    end_ea = func.end_ea
    for head in idautils.Heads(func.start_ea, end_ea):
        for dr in idautils.DataRefsFrom(head):
            if dr in visited:
                continue
            visited.add(dr)
            s = ida_bytes.get_strlit_contents(dr, -1, STRTYPE_C)
            if s:
                try:
                    decoded = s.decode("utf-8", errors="replace")
                except:
                    decoded = repr(s)
                refs.append({"address": "0x%X" % dr, "string": decoded})
    return refs

def decompile_function(ea):
    result = {}
    func = ida_funcs.get_func(ea)
    if not func:
        result["error"] = "No function found at 0x%X" % ea
        return result

    result["start_ea"] = "0x%X" % func.start_ea
    result["end_ea"] = "0x%X" % func.end_ea
    result["size"] = func.end_ea - func.start_ea

    bb_count = 0
    for block in idaapi.FlowChart(func):
        bb_count += 1
    result["basic_block_count"] = bb_count

    result["name"] = ida_name.get_name(ea)

    result["string_refs"] = get_func_string_refs(func)

    try:
        cfunc = ida_hexrays.decompile(ea)
    except Exception as ex:
        result["decompile_error"] = "Exception during decompile: %s" % str(ex)
        return result

    if not cfunc:
        result["decompile_error"] = "Decompilation returned None for 0x%X" % ea
        return result

    result["pseudocode"] = str(cfunc)

    params = []
    try:
        for i in range(cfunc.get_var_count()):
            var = cfunc.get_var(i)
            try:
                type_str = str(var.tif)
            except:
                type_str = "unknown"
            params.append({
                "name": var.name,
                "type": type_str,
                "is_arg": var.is_arg_var
            })
    except Exception as ex:
        result["param_error"] = str(ex)
    result["parameters"] = params

    # Get string refs from decompiled code via ctree walk
    hexrs_refs = []
    try:
        visitor = StringRefVisitor()
        cfunc.body.accept(visitor)
        hexrs_refs = visitor.refs
    except:
        pass

    if hexrs_refs:
        result["string_refs_from_decompiler"] = hexrs_refs

    all_refs = result.get("string_refs", []) + result.get("string_refs_from_decompiler", [])
    seen = set()
    merged = []
    for r in all_refs:
        key = r["address"]
        if key not in seen:
            seen.add(key)
            merged.append(r)
    result["string_refs_all"] = merged

    return result

class StringRefVisitor(ida_hexrays.ctree_visitor_t):
    def __init__(self):
        ida_hexrays.ctree_visitor_t.__init__(self, ida_hexrays.CV_FAST)
        self.refs = []

    def visit_expr(self, insn):
        if insn.opcode == ida_hexrays.cot_obj:
            target = insn.obj_ea
            if target != idaapi.BADADDR:
                s = ida_bytes.get_strlit_contents(target, -1, STRTYPE_C)
                if s:
                    try:
                        decoded = s.decode("utf-8", errors="replace")
                    except:
                        decoded = repr(s)
                    self.refs.append({"address": "0x%X" % target, "string": decoded})
        return 0

def main():
    funcs = {
        "sub_142456BB0_BindHttpTutorialRecord": 0x142456BB0,
        "sub_142B0A9D0_BindHttpTutorialSkipRecord": 0x142B0A9D0,
        "sub_1425540B0_BindHttpGameDataSaveData": 0x1425540B0,
        "sub_141F77DE0_BindHttpGameDataLoadSave": 0x141F77DE0,
    }

    output = {}
    for label, ea in funcs.items():
        print("[*] Decompiling %s at 0x%X..." % (label, ea))
        try:
            result = decompile_function(ea)
            result["label"] = label
            output[label] = result
            print("[+] Done: %s" % label)
        except Exception as ex:
            output[label] = {"error": str(ex), "label": label}
            print("[-] Error on %s: %s" % (label, str(ex)))

    out_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g40_tutorial_gamedata_decompile.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("[+] Results saved to %s" % out_path)

if __name__ == "__main__":
    main()
