"""IDAPython script: Extract import table from the loaded binary."""
import json
import idaapi
import ida_nalt
import idautils


def get_imports():
    """Extract all imported functions from the import table."""
    imports = {}
    
    # Get the import module count
    nimps = idaapi.get_import_module_qty()
    
    for i in range(nimps):
        mod = idaapi.import_module_t()
        if idaapi.get_import_module_info(mod, i):
            mod_name = idaapi.get_import_module_name(i)
            if not mod_name:
                mod_name = f"module_{i}"
            
            entries = []
            
            # Iterate over import entries
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
        "imports": get_imports(),
        "exports": get_exports(),
        "import_module_count": idaapi.get_import_module_qty(),
    }
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\imports_result.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Extracted {sum(len(v) for v in result['imports'].values())} imports from {len(result['imports'])} modules")
    print(f"Extracted {len(result['exports'])} exports")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
