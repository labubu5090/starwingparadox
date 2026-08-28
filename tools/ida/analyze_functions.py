"""IDAPython script: Analyze function calls and control flow patterns."""
import json
import idautils
import idc
import ida_nalt
import ida_funcs
import ida_hexrays


def get_function_list():
    """Extract all functions with basic metadata."""
    functions = []
    
    for func_ea in idautils.Functions():
        func = ida_funcs.get_func(func_ea)
        if func:
            entry = {
                "ea": hex(func_ea),
                "name": idc.get_func_name(func_ea),
                "size": func.end_ea - func.start_ea,
                "is_entry": func.entry_point,
            }
            functions.append(entry)
    
    return functions


def get_call_graph():
    """Extract call graph relationships."""
    calls = []
    
    for func_ea in idautils.Functions():
        for xref in idautils.XrefsTo(func_ea):
            if xref.type == ida_xref.fl_CF:
                calls.append({
                    "caller": hex(xref.frm),
                    "callee": hex(func_ea),
                    "type": "call",
                })
    
    return calls


def search_comparisons(target_value):
    """Search for comparison instructions with a specific value."""
    results = []
    
    for seg_ea in idautils.Segments():
        seg = ida_segment.getseg(seg_ea)
        ea = seg.start_ea
        
        while ea < seg.end_ea:
            mnemonic = idc.print_insn_mnem(ea)
            if mnemonic in ["cmp", "test"]:
                op1 = idc.print_operand(ea, 0)
                op2 = idc.print_operand(ea, 1)
                if target_value in op2:
                    results.append({
                        "ea": hex(ea),
                        "mnemonic": mnemonic,
                        "operand": op2,
                        "context": idc.GetDisasm(ea),
                    })
            ea = idc.next_head(ea, seg.end_ea)
    
    return results


def main():
    result = {
        "file": ida_nalt.get_input_file_path(),
        "image_base": hex(ida_nalt.get_imagebase()),
        "functions": get_function_list(),
        "call_graph": get_call_graph(),
    }
    
    # Search for common command IDs (0x01-0x5B range based on protocol registry)
    command_ids = list(range(1, 92))
    comparison_results = {}
    
    for cmd_id in command_ids:
        comparisons = search_comparisons(hex(cmd_id))
        if comparisons:
            comparison_results[hex(cmd_id)] = comparisons
    
    result["command_id_comparisons"] = comparison_results
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\functions_result.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Extracted {len(result['functions'])} functions")
    print(f"Extracted {len(result['call_graph'])} call relationships")
    print(f"Found {len(comparison_results)} command ID comparisons")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
