import json
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g110_verify.json"
import ida_bytes
res = {}
base = 0x140000000
# entry: 0x2dd8e50 - 5 bytes
res["entry"] = {"rva": "0x2dd8e50", "bytes": ida_bytes.get_bytes(base+0x2dd8e50, 5).hex()}
# cave: 0x63fc8ad - 36 bytes
res["cave"] = {"rva": "0x63fc8ad", "bytes": ida_bytes.get_bytes(base+0x63fc8ad, 36).hex()}
# target: 0x2dd8e5d - 8 bytes
res["target"] = {"rva": "0x2dd8e5d", "bytes": ida_bytes.get_bytes(base+0x2dd8e5d, 8).hex()}
open(OUT,"w").write(json.dumps(res, indent=1))
print("ok")
