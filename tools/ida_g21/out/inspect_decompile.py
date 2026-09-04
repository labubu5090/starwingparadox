import json
with open('tools/ida_g21/out/g40_tutorial_gamedata_decompile.json') as f:
    data = json.load(f)
for key, val in data.items():
    refs = val.get("string_refs", [])
    print(f"{key}: size={val.get('size','?')}, strings={len(refs)}")
    for r in refs:
        s = r["string"]
        if any(kw in s.lower() for kw in ["http", "url", "result", "error", "tutorial", "record", "game_data", "skip", "save", "load", "status", "json", "player_id"]):
            print(f"  {r['address']}: {s}")
