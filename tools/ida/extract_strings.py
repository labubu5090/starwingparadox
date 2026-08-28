"""IDAPython script: Extract strings from the loaded binary."""
import json
import idautils
import idc
import ida_nalt
import ida_segment


def get_strings():
    """Extract all strings from the binary."""
    strings = []
    
    for s in idautils.Strings():
        entry = {
            "ea": hex(s.ea),
            "length": s.length,
            "strtype": s.strtype,
            "value": str(s),
        }
        strings.append(entry)
    
    return strings


def get_segments():
    """Extract segment information."""
    segments = []
    
    seg = ida_segment.get_first_seg()
    while seg:
        entry = {
            "name": ida_segment.get_segm_name(seg),
            "start_ea": hex(seg.start_ea),
            "end_ea": hex(seg.end_ea),
            "size": seg.end_ea - seg.start_ea,
            "type": seg.type,
            "perm": seg.perm,
        }
        segments.append(entry)
        seg = ida_segment.get_next_seg(seg.start_ea)
    
    return segments


def get_entry_points():
    """Extract entry points."""
    entry_points = []
    
    for i in range(idaapi.get_entry_qty()):
        ordinal = idaapi.get_entry_ordinal(i)
        entry = idaapi.get_entry(ordinal)
        if entry:
            entry_points.append({
                "ordinal": ordinal,
                "ea": hex(entry),
                "name": idaapi.get_entry_name(ordinal),
            })
    
    return entry_points


def main():
    result = {
        "file": ida_nalt.get_input_file_path(),
        "image_base": hex(ida_nalt.get_imagebase()),
        "strings": get_strings(),
        "segments": get_segments(),
        "entry_points": get_entry_points(),
    }
    
    output_path = r"C:\Users\KAHO\Pictures\Starwing\tools\ida\strings_result.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Extracted {len(result['strings'])} strings")
    print(f"Extracted {len(result['segments'])} segments")
    print(f"Extracted {len(result['entry_points'])} entry points")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
