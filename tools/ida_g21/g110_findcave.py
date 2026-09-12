import json
OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g110_findcave.json"
import ida_ida, ida_bytes, ida_segment
res = {"caves": [], "ca80_region": {}}
base = 0x140000000
rva = 0x063FC89B   # existing CA80 cave
ea = base + rva
# read 64 bytes around
raw = ida_bytes.get_bytes(ea - 0x40, 0x200)
res["ca80_region"]["off_0x40_hex"] = raw.hex() if raw else None
# scan whole executable for 128-byte zero runs in executable segments
import ida_segment
dur = 0x1000000
step = 0x1000
for seg in range(ida_segment.get_segm_qty()):
    s = ida_segment.getnseg(seg)
    name = ida_segment.get_segm_name(s)
    if s.perm & 1:  # readable
        start = s.start_ea
        end = s.end_ea
        # scan for zero runs >= 64
        run = 0
        run_start = 0
        for ea2 in range(start, end):
            if ida_bytes.get_byte(ea2) == 0:
                if run == 0:
                    run_start = ea2
                run += 1
                if run >= 64:
                    res["caves"].append({"rva": hex(run_start - base), "len": run})
                    # skip forward
                    ea2 = run_start + run
            else:
                run = 0
# keep first few in exec segment
res["caves"] = res["caves"][:8]
res["status"] = "DONE"
open(OUT,"w").write(json.dumps(res, indent=1))
print("done", len(res["caves"]))
