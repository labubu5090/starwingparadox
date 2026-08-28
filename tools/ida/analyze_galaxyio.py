"""IDAPython script: Analyze GALAXYIO.dll for pipe client behavior."""
import json
import idautils
import idc
import ida_nalt
import ida_search
import ida_bytes


def search_all_strings():
    """Extract all strings from the DLL."""
    strings = []
    
    for s in idautils.Strings():
        entry = {
            "ea": hex(s.ea),
            "value": str(s),
            "length": s.length,
        }
        strings.append(entry)
    
    return strings


def search_pipe_references():
    """Search specifically for pipe-related patterns."""
    results = []
    
    pipe_patterns = [
        "pipe",
        "nesys_games",
        "\\\\.\\pipe",
        "CreateFile",
        "ReadFile",
        "WriteFile",
        "PeekNamedPipe",
        "WaitNamedPipe",
        "SetNamedPipeHandleState",
        "ConnectNamedPipe",
        "DisconnectNamedPipe",
        "GetNamedPipeInfo",
        "GetNamedPipeHandleState",
        "TransactNamedPipe",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in pipe_patterns:
            if pattern.lower() in value.lower():
                results.append({
                    "ea": hex(s.ea),
                    "value": value,
                    "pattern_matched": pattern,
                    "length": s.length,
                })
                break
    
    return results


def search_network_references():
    """Search specifically for network-related patterns."""
    results = []
    
    network_patterns = [
        "socket",
        "connect",
        "send",
        "recv",
        "getaddrinfo",
        "WinHTTP",
        "WinINet",
        "http",
        "https",
        "tcp",
        "udp",
        "port",
        "localhost",
        "127.0.0.1",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in network_patterns:
            if pattern.lower() in value.lower():
                results.append({
                    "ea": hex(s.ea),
                    "value": value,
                    "pattern_matched": pattern,
                    "length": s.length,
                })
                break
    
    return results


def search_game_references():
    """Search specifically for game-related patterns."""
    results = []
    
    game_patterns = [
        "matching",
        "battle",
        "result",
        "card",
        "player",
        "session",
        "heartbeat",
        "timeout",
        "error",
        "fatal",
        "disconnect",
        "reconnect",
        "nesys",
        "galaxy",
        "starwing",
    ]
    
    for s in idautils.Strings():
        value = str(s)
        for pattern in game_patterns:
            if pattern.lower() in value.lower():
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
        "all_strings": search_all_strings(),
        "pipe_references": search_pipe_references(),
        "network_references": search_network_references(),
        "game_references": search_game_references(),
        "imports": get_imports(),
        "exports": get_exports(),
    }
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\galaxyio_analysis.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Total strings: {len(result['all_strings'])}")
    print(f"Pipe references: {len(result['pipe_references'])}")
    print(f"Network references: {len(result['network_references'])}")
    print(f"Game references: {len(result['game_references'])}")
    print(f"Imports: {sum(len(v) for v in result['imports'].values())} from {len(result['imports'])} modules")
    print(f"Exports: {len(result['exports'])}")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
