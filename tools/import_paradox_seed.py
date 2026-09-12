# -*- coding: utf-8 -*-
"""Parse paradox.sql (PostgreSQL COPY format) and import all player seed data
into the local SQLite db.  INSERT OR REPLACE by primary key id so re-runs are safe."""
import re
import shutil
import sqlite3
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SQL_PATH = r"C:\Users\KAHO\Pictures\Starwing\server\data\starwing.db"
DUMP_PATH = r"C:\Users\KAHO\AppData\Local\Temp\opencode\paradox.sql"

BACKUP = SQL_PATH + f".bak_seed_import_{time.strftime('%Y%m%d_%H%M%S')}"

COPY_RE = re.compile(
    r"COPY public\.(\w+)\s*\(([^)]+)\)\s*FROM stdin;\n(.*?)\\\.\n",
    re.S,
)

def parse_value(v: str):
    if v == r"\N":
        return None
    if v == "t":
        return 1
    if v == "f":
        return 0
    return v

def main() -> None:
    with open(DUMP_PATH, "r", encoding="utf-8") as fh:
        dump = fh.read()

    tables = {}
    for m in COPY_RE.finditer(dump):
        name = m.group(1)
        cols = [c.strip().strip('"') for c in m.group(2).split(",")]
        rows = []
        for line in m.group(3).splitlines():
            if not line.strip():
                continue
            vals = line.split("\t")
            if len(vals) != len(cols):
                print(f"  !! {name}: row col mismatch {len(vals)} vs {len(cols)}: {line!r}")
                continue
            rows.append([parse_value(v) for v in vals])
        tables[name] = (cols, rows)

    shutil.copy2(SQL_PATH, BACKUP)
    print(f"backup: {BACKUP}")

    con = sqlite3.connect(SQL_PATH)
    cur = con.cursor()

    # tables localised here only (skip: none of dump tables are excluded)
    summary = {}
    for name, (cols, rows) in tables.items():
        placeholders = ",".join("?" * len(cols))
        sql = f"INSERT OR REPLACE INTO {name} ({','.join(cols)}) VALUES ({placeholders})"
        cur.executemany(sql, rows)
        summary[name] = len(rows)
        print(f"  imported {name}: {len(rows)} rows")

    con.commit()
    con.close()
    print("\nALL IMPORTED OK")
    for name, n in summary.items():
        print(f"  {name:28s}{n}")


if __name__ == "__main__":
    main()