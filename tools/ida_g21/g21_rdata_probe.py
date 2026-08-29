import ida_funcs, ida_name, ida_nalt, idautils, idc, json, os

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g21_rdata_probe.json"
ib = ida_nalt.get_imagebase()

# Test xrefs to a known .rdata address (application/json at 0x14851AFE8)
test_addr = 0x14851AFE8
xrefs = list(idautils.XrefsTo(test_addr))
result = {"test_addr": hex(test_addr), "xref_count": len(xrefs)}

# Also check a small range around it
nearby_xrefs = 0
for off in range(-16, 16, 4):
    ea = test_addr + off
    for xr in idautils.XrefsTo(ea):
        nearby_xrefs += 1
        if nearby_xrefs >= 5:
            break
    if nearby_xrefs >= 5:
        break
result["nearby_xrefs_in_range"] = nearby_xrefs

# Check if there's a pointer to our string somewhere
# Read 8 bytes at test_addr to see what's there
raw = ida_bytes.get_bytes(test_addr, 32)
result["raw_bytes"] = raw.hex() if raw else None

# Check imports for WinHttp/WinInet
imports = []
for mod in idautils.Modules():
    imports.append(str(mod.name))
result["imports"] = imports[:20]

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
