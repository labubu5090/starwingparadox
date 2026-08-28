"""IDAPython master script: Run all analysis scripts."""
import json
import os
import sys

# Add the tools directory to the path
sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools\ida")


def run_analysis():
    """Run all analysis scripts and consolidate results."""
    results = {}
    
    # Run imports extraction
    try:
        from extract_imports import main as imports_main
        imports_result = imports_main()
        results["imports"] = imports_result
    except Exception as e:
        print(f"Error running imports extraction: {e}")
    
    # Run strings extraction
    try:
        from extract_strings import main as strings_main
        strings_result = strings_main()
        results["strings"] = strings_result
    except Exception as e:
        print(f"Error running strings extraction: {e}")
    
    # Run pattern search
    try:
        from search_patterns import main as patterns_main
        patterns_result = patterns_main()
        results["patterns"] = patterns_result
    except Exception as e:
        print(f"Error running pattern search: {e}")
    
    # Run function analysis
    try:
        from analyze_functions import main as functions_main
        functions_result = functions_main()
        results["functions"] = functions_result
    except Exception as e:
        print(f"Error running function analysis: {e}")
    
    # Save consolidated results
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\consolidated_analysis.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Consolidated analysis saved to {output_path}")
    
    return results


if __name__ == "__main__":
    run_analysis()
