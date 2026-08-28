"""Extract source code paths and create module map."""
import json
import re


def extract_source_paths(strings):
    """Extract source code file paths from strings."""
    paths = []
    pattern = r'C:\\work\\acr\\[^\s"]+\.cpp'
    
    for s in strings:
        matches = re.findall(pattern, s["value"])
        for match in matches:
            if match not in paths:
                paths.append(match)
    
    return sorted(paths)


def categorize_paths(paths):
    """Categorize source paths by module."""
    categories = {}
    
    for path in paths:
        # Extract module name
        parts = path.split('\\')
        if 'Source' in parts:
            source_idx = parts.index('Source')
            if source_idx + 1 < len(parts):
                module = parts[source_idx + 1]
                if module not in categories:
                    categories[module] = []
                categories[module].append(path)
    
    return categories


def main():
    # Load the string analysis results
    with open(r'C:\Users\KAHO\Pictures\Starwing\tools\ida\string_analysis_results.json', 'r') as f:
        data = json.load(f)
    
    # Extract source paths from shipping executable
    shipping_strings = data['AcrGame-Win64-Shipping.exe']['filtered_matches']
    
    all_source_paths = []
    for pattern, matches in shipping_strings.items():
        for match in matches:
            if 'C:\\work\\acr' in match['value']:
                paths = extract_source_paths([match])
                all_source_paths.extend(paths)
    
    # Remove duplicates
    all_source_paths = list(set(all_source_paths))
    all_source_paths.sort()
    
    # Categorize by module
    categories = categorize_paths(all_source_paths)
    
    print("=== Source Code Module Structure ===\n")
    for module, paths in sorted(categories.items()):
        print(f"\n{module} ({len(paths)} files):")
        for path in sorted(paths)[:10]:  # Show first 10
            print(f"  {path}")
        if len(paths) > 10:
            print(f"  ... and {len(paths) - 10} more")
    
    # Save results
    result = {
        "total_paths": len(all_source_paths),
        "categories": categories,
        "all_paths": all_source_paths,
    }
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\source_paths.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n\nTotal unique source paths: {len(all_source_paths)}")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
