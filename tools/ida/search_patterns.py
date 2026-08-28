"""IDAPython script: Search for game-specific patterns in the binary."""
import json
import idautils
import idc
import ida_nalt
import ida_search
import ida_bytes


def search_strings(pattern):
    """Search for strings matching a pattern."""
    results = []
    
    for s in idautils.Strings():
        value = str(s)
        if pattern.lower() in value.lower():
            results.append({
                "ea": hex(s.ea),
                "value": value,
                "length": s.length,
            })
    
    return results


def search_imports(pattern):
    """Search for imported functions matching a pattern."""
    results = []
    
    nimps = idaapi.get_import_module_qty()
    for i in range(nimps):
        mod = idaapi.import_module_t()
        if idaapi.get_import_module_info(mod, i):
            mod_name = idaapi.get_import_module_name(i)
            
            def imp_cb(ea, ord, name, param):
                if name and pattern.lower() in name.lower():
                    results.append({
                        "module": mod_name,
                        "name": name,
                        "ea": hex(ea),
                    })
                return True
            
            idaapi.enum_import_names(i, imp_cb)
    
    return results


def search_xrefs_to_string(target_str):
    """Find cross-references to a specific string."""
    results = []
    
    for s in idautils.Strings():
        if target_str in str(s):
            for xref in idautils.XrefsTo(s.ea):
                results.append({
                    "string_ea": hex(s.ea),
                    "string_value": str(s),
                    "xref_ea": hex(xref.frm),
                    "xref_type": xref.type,
                })
    
    return results


def main():
    patterns_to_search = [
        # Pipe-related
        "pipe",
        "nesys_games",
        "CreateFile",
        "ReadFile",
        "WriteFile",
        "PeekNamedPipe",
        "WaitNamedPipe",
        "SetNamedPipeHandleState",
        
        # Network-related
        "socket",
        "connect",
        "send",
        "recv",
        "getaddrinfo",
        "WinHTTP",
        "WinINet",
        "libcurl",
        "http",
        "https",
        
        # Game-specific
        "matching",
        "battle",
        "result",
        "card",
        "player",
        "session",
        "heartbeat",
        "timeout",
        
        # Configuration
        "GameServer",
        "ServerPort",
        "OpenKey",
        "SaveData",
        "option.txt",
        "Game.ini",
        
        # Error handling
        "error",
        "fatal",
        "disconnect",
        "reconnect",
    ]
    
    result = {
        "file": ida_nalt.get_input_file_path(),
        "image_base": hex(ida_nalt.get_imagebase()),
        "string_searches": {},
        "import_searches": {},
        "xref_searches": {},
    }
    
    for pattern in patterns_to_search:
        result["string_searches"][pattern] = search_strings(pattern)
        result["import_searches"][pattern] = search_imports(pattern)
    
    # Specific searches for critical patterns
    critical_patterns = [
        "\\.\pipe\nesys_games",
        "CreateFileA",
        "CreateFileW",
        "ReadFile",
        "WriteFile",
        "PeekNamedPipe",
        "WaitNamedPipe",
    ]
    
    for pattern in critical_patterns:
        result["xref_searches"][pattern] = search_xrefs_to_string(pattern)
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\patterns_result.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"String searches: {sum(len(v) for v in result['string_searches'].values())} results")
    print(f"Import searches: {sum(len(v) for v in result['import_searches'].values())} results")
    print(f"Xref searches: {sum(len(v) for v in result['xref_searches'].values())} results")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
