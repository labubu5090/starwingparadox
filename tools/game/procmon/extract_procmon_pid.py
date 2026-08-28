"""Extract Procmon CSV rows by exact PID.

Usage:
    python extract_procmon_pid.py --input capture.csv --pid 1234 --output filtered.csv --summary summary.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED_HEADERS = {"Time of Day", "Process Name", "PID", "Operation", "Path", "Result", "Detail"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract Procmon rows by exact PID")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--pid", required=True, type=int, help="Exact PID to extract")
    parser.add_argument("--output", required=True, help="Output filtered CSV path")
    parser.add_argument("--summary", default=None, help="Output summary JSON path")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    target_pid = args.pid

    if not input_path.exists():
        print(f"ERROR: Input not found: {input_path}", file=sys.stderr)
        return 1

    input_sha = sha256_file(input_path)

    # Read and validate header
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("ERROR: CSV has no header row", file=sys.stderr)
            return 1

        headers = set(reader.fieldnames)
        missing = REQUIRED_HEADERS - headers
        if missing:
            print(f"ERROR: Missing required headers: {missing}", file=sys.stderr)
            return 1

        # Stream rows, extract matching PID
        matched: list[dict] = []
        total = 0
        pid_str = str(target_pid)

        for row in total and [] or reader:
            total += 1
            row_pid = row.get("PID", "").strip()
            # Exact match: row PID must equal target PID as string
            if row_pid == pid_str:
                row_proc = row.get("Process Name", "").strip()
                matched.append({
                    "time": row.get("Time of Day", ""),
                    "process": row_proc,
                    "pid": row_pid,
                    "operation": row.get("Operation", ""),
                    "path": row.get("Path", ""),
                    "result": row.get("Result", ""),
                    "detail": row.get("Detail", ""),
                })

    if total == 0:
        print("ERROR: CSV is empty (zero rows)", file=sys.stderr)
        return 1

    if not matched:
        print(f"ERROR: No rows found with PID {target_pid} (scanned {total} rows)", file=sys.stderr)
        return 2

    # Validate all matched rows are NesysService.exe
    proc_names = set(m["process"] for m in matched)
    if proc_names != {"NesysService.exe"}:
        print(f"WARNING: Matched rows have unexpected process names: {proc_names}", file=sys.stderr)

    # Write filtered CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Time of Day", "Process Name", "PID", "Operation", "Path", "Result", "Detail"])
        writer.writeheader()
        for m in matched:
            writer.writerow({
                "Time of Day": m["time"],
                "Process Name": m["process"],
                "PID": m["pid"],
                "Operation": m["operation"],
                "Path": m["path"],
                "Result": m["result"],
                "Detail": m["detail"],
            })

    output_sha = sha256_file(output_path)

    # Operation and result counts
    op_counts = Counter(m["operation"] for m in matched)
    result_counts = Counter(m["result"] for m in matched)

    timestamps = [m["time"] for m in matched if m["time"]]

    summary = {
        "input_file": str(input_path),
        "input_sha256": input_sha,
        "output_file": str(output_path),
        "output_sha256": output_sha,
        "target_pid": target_pid,
        "full_row_count": total,
        "matched_row_count": len(matched),
        "matched_process_names": sorted(proc_names),
        "matched_pids": sorted(set(m["pid"] for m in matched)),
        "first_timestamp": timestamps[0] if timestamps else None,
        "last_timestamp": timestamps[-1] if timestamps else None,
        "operation_counts": dict(op_counts.most_common()),
        "result_counts": dict(result_counts.most_common()),
    }

    if args.summary:
        summary_path = Path(args.summary)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary written to {summary_path}")

    print(f"Extracted {len(matched)} rows (PID {target_pid}) from {total} total")
    print(f"Process: {', '.join(sorted(proc_names))}")
    print(f"Timestamps: {timestamps[0] if timestamps else 'N/A'} -> {timestamps[-1] if timestamps else 'N/A'}")

    return 0


if __name__ == "__main__":
    sys.exit(run())
