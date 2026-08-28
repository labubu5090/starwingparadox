"""PE analysis script for game executables."""
import pefile
import json
import os
import hashlib


def calculate_sha256(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def analyze_pe(file_path):
    """Analyze a PE file and extract key information."""
    pe = pefile.PE(file_path)
    
    result = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "sha256": calculate_sha256(file_path),
        "file_size": os.path.getsize(file_path),
        "machine": hex(pe.FILE_HEADER.Machine),
        "timestamp": hex(pe.FILE_HEADER.TimeDateStamp),
        "characteristics": hex(pe.FILE_HEADER.Characteristics),
        "image_base": hex(pe.OPTIONAL_HEADER.ImageBase),
        "section_alignment": pe.OPTIONAL_HEADER.SectionAlignment,
        "file_alignment": pe.OPTIONAL_HEADER.FileAlignment,
        "subsystem": pe.OPTIONAL_HEADER.Subsystem,
        "dll_characteristics": hex(pe.OPTIONAL_HEADER.DllCharacteristics),
        "sections": [],
        "imports": {},
        "exports": [],
        "resources": [],
        "strings": [],
    }
    
    # Extract sections
    for section in pe.sections:
        section_info = {
            "name": section.Name.decode('utf-8', errors='ignore').rstrip('\x00'),
            "virtual_address": hex(section.VirtualAddress),
            "virtual_size": section.Misc_VirtualSize,
            "raw_data_size": section.SizeOfRawData,
            "characteristics": hex(section.Characteristics),
        }
        result["sections"].append(section_info)
    
    # Extract imports
    if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode('utf-8', errors='ignore')
            functions = []
            for imp in entry.imports:
                if imp.name:
                    functions.append({
                        "name": imp.name.decode('utf-8', errors='ignore'),
                        "hint": imp.hint,
                        "address": hex(imp.address),
                    })
            result["imports"][dll_name] = functions
    
    # Extract exports
    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name:
                result["exports"].append({
                    "name": exp.name.decode('utf-8', errors='ignore'),
                    "ordinal": exp.ordinal,
                    "address": hex(exp.address),
                })
    
    # Extract strings (simplified - just look for ASCII strings)
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Look for ASCII strings of length >= 4
        current_string = []
        strings = []
        
        for i, byte in enumerate(data):
            if 32 <= byte <= 126:  # Printable ASCII
                current_string.append(chr(byte))
            else:
                if len(current_string) >= 4:
                    string_value = ''.join(current_string)
                    strings.append({
                        "offset": hex(i - len(current_string)),
                        "value": string_value,
                        "length": len(string_value),
                    })
                current_string = []
        
        # Add the last string if any
        if len(current_string) >= 4:
            string_value = ''.join(current_string)
            strings.append({
                "offset": hex(len(data) - len(current_string)),
                "value": string_value,
                "length": len(string_value),
            })
        
        result["strings"] = strings[:1000]  # Limit to first 1000 strings
        
    except Exception as e:
        print(f"Error extracting strings: {e}")
    
    pe.close()
    return result


def main():
    """Main analysis function."""
    files_to_analyze = [
        r"X:\StarwingParadox\WindowsNoEditor\AcrGame.exe",
        r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe",
        r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\GALAXYIO.dll",
        r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\Lua524.dll",
        r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\QRreader.dll",
    ]
    
    results = {}
    
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            print(f"Analyzing {os.path.basename(file_path)}...")
            result = analyze_pe(file_path)
            results[os.path.basename(file_path)] = result
            print(f"  - SHA256: {result['sha256']}")
            print(f"  - Sections: {len(result['sections'])}")
            print(f"  - Imports: {sum(len(v) for v in result['imports'].values())} from {len(result['imports'])} DLLs")
            print(f"  - Exports: {len(result['exports'])}")
            print(f"  - Strings: {len(result['strings'])}")
        else:
            print(f"File not found: {file_path}")
    
    # Save results
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\pe_analysis_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    return results


if __name__ == "__main__":
    main()
