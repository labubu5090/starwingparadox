"""IDAPython script: Analyze AcrGame.exe launcher behavior."""
import json
import idautils
import idc
import ida_nalt


def search_strings():
    """Extract all strings from the launcher."""
    strings = []
    
    for s in idautils.Strings():
        entry = {
            "ea": hex(s.ea),
            "value": str(s),
            "length": s.length,
        }
        strings.append(entry)
    
    return strings


def search_launcher_references():
    """Search for launcher-specific patterns."""
    results = []
    
    launcher_patterns = [
        "acrgame",
        "shipping",
        "launch",
        "start",
        "exec",
        "command",
        "argument",
        "parameter",
        "working",
        "directory",
        "path",
        "exe",
        "process",
        "create",
        "spawn",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in launcher_patterns:
            if pattern.lower() in value.lower():
                results.append({
                    "ea": hex(s.ea),
                    "value": value,
                    "pattern_matched": pattern,
                    "length": s.length,
                })
                break
    
    return results


def search_process_references():
    """Search for process creation patterns."""
    results = []
    
    process_patterns = [
        "CreateProcess",
        "ShellExecute",
        "WinExec",
        "system(",
        "exec(",
        "spawn(",
        "CreateProcessA",
        "CreateProcessW",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in process_patterns:
            if pattern in value:
                results.append({
                    "ea": hex(s.ea),
                    "value": value,
                    "pattern_matched": pattern,
                    "length": s.length,
                })
                break
    
    return results


def search_command_line_references():
    """Search for command line construction patterns."""
    results = []
    
    cmdline_patterns = [
        "command",
        "line",
        "arg",
        "param",
        "option",
        "flag",
        "/",
        "-",
        "--",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in cmdline_patterns:
            if pattern in value:
                results.append({
                    "ea": hex(s.ea),
                    "value": value,
                    "pattern_matched": pattern,
                    "length": s.length,
                })
                break
    
    return results


def get_imports():
    """Extract all imported functions."""
    imports = {}
    
    nimps = idaapi.get_import_module_qty()
    
    for i in range(nimps):
        mod = idaapi.import_module_t()
        if idaapi.get_import_module_info(mod, i):
            mod_name = idaapi.get_import_module_name(i)
            if not mod_name:
                mod_name = f"module_{i}"
            
            entries = []
            
            def imp_cb(ea, ord, name, param):
                entry = {}
                if name:
                    entry["name"] = name
                if ord:
                    entry["ordinal"] = ord
                entry["ea"] = hex(ea)
                entries.append(entry)
                return True
            
            idaapi.enum_import_names(i, imp_cb)
            
            if entries:
                imports[mod_name] = entries
    
    return imports


def get_exports():
    """Extract all exported functions."""
    exports = []
    
    for i in range(idaapi.get_export_module_qty()):
        ordinal = i
        entry = idaapi.get_export_entry(ordinal)
        if entry:
            exp = {}
            if entry.name:
                exp["name"] = entry.name
            exp["ordinal"] = ordinal
            exp["ea"] = hex(entry.ea)
            exports.append(exp)
    
    return exports


def main():
    result = {
        "file": ida_nalt.get_input_file_path(),
        "image_base": hex(ida_nalt.get_imagebase()),
        "all_strings": search_strings(),
        "launcher_references": search_launcher_references(),
        "process_references": search_process_references(),
        "command_line_references": search_command_line_references(),
        "imports": get_imports(),
        "exports": get_exports(),
    }
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\acrgame_launcher_analysis.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Total strings: {len(result['all_strings'])}")
    print(f"Launcher references: {len(result['launcher_references'])}")
    print(f"Process references: {len(result['process_references'])}")
    print(f"Command line references: {len(result['command_line_references'])}")
    print(f"Imports: {sum(len(v) for v in result['imports'].values())} from {len(result['imports'])} modules")
    print(f"Exports: {len(result['exports'])}")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
