"""Deep string analysis for game executables."""
import pefile
import re
import json


def extract_all_strings(file_path, min_length=4):
    """Extract all ASCII and Unicode strings from a PE file."""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # ASCII strings
    ascii_strings = []
    current = []
    for i, byte in enumerate(data):
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                ascii_strings.append({
                    "offset": i - len(current),
                    "value": ''.join(current),
                    "type": "ascii"
                })
            current = []
    
    # Unicode strings (UTF-16LE)
    unicode_strings = []
    i = 0
    while i < len(data) - 1:
        if data[i] >= 32 and data[i] <= 126 and data[i+1] == 0:
            start = i
            chars = []
            while i < len(data) - 1 and data[i] >= 32 and data[i] <= 126 and data[i+1] == 0:
                chars.append(chr(data[i]))
                i += 2
            if len(chars) >= min_length:
                unicode_strings.append({
                    "offset": start,
                    "value": ''.join(chars),
                    "type": "unicode"
                })
        else:
            i += 1
    
    return ascii_strings, unicode_strings


def filter_strings(strings, patterns):
    """Filter strings that match any of the given patterns."""
    results = {}
    for pattern in patterns:
        matches = []
        for s in strings:
            if pattern.lower() in s["value"].lower():
                matches.append(s)
        if matches:
            results[pattern] = matches
    return results


def main():
    files = {
        "AcrGame-Win64-Shipping.exe": r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe",
        "GALAXYIO.dll": r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\GALAXYIO.dll",
        "AcrGame.exe": r"X:\StarwingParadox\WindowsNoEditor\AcrGame.exe",
    }
    
    patterns = [
        # Pipe patterns
        "pipe", "\\\\.\\pipe", "nesys_games", "CreateFile", "ReadFile", "WriteFile",
        "PeekNamedPipe", "WaitNamedPipe", "ConnectNamedPipe", "SetNamedPipeHandleState",
        
        # Network patterns
        "socket", "connect", "http", "https", "tcp", "port", "localhost", "127.0.0.1",
        "winhttp", "wininet", "curl",
        
        # Game-specific patterns
        "matching", "battle", "result", "card", "player", "session", "heartbeat",
        "timeout", "nesys", "galaxy", "starwing",
        
        # Configuration patterns
        "GameServer", "ServerPort", "OpenKey", "SaveData", "option.txt", "Game.ini",
        "command", "line", "argument",
        
        # Error patterns
        "error", "fatal", "disconnect", "reconnect", "retry",
        
        # Protocol patterns
        "protobuf", "proto", "message", "request", "response", "reply",
        
        # Launcher patterns
        "launch", "start", "exec", "process", "create",
        
        # URL patterns
        ".jp", ".net", ".com", "www", "dev",
    ]
    
    results = {}
    
    for name, path in files.items():
        print(f"\n=== Analyzing {name} ===")
        ascii_strings, unicode_strings = extract_all_strings(path)
        
        print(f"  ASCII strings: {len(ascii_strings)}")
        print(f"  Unicode strings: {len(unicode_strings)}")
        
        all_strings = ascii_strings + unicode_strings
        
        filtered = filter_strings(all_strings, patterns)
        
        file_results = {
            "total_ascii": len(ascii_strings),
            "total_unicode": len(unicode_strings),
            "filtered_matches": {}
        }
        
        for pattern, matches in filtered.items():
            print(f"\n  Pattern '{pattern}' ({len(matches)} matches):")
            for match in matches[:5]:  # Show first 5
                value = match["value"]
                print(f"    [{match['type']}] {value}")
            if len(matches) > 5:
                print(f"    ... and {len(matches) - 5} more")
            
            file_results["filtered_matches"][pattern] = [
                {"offset": m["offset"], "value": m["value"], "type": m["type"]}
                for m in matches
            ]
        
        results[name] = file_results
    
    # Save results
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\string_analysis_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
