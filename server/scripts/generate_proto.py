#!/usr/bin/env python3
"""Generate Python protobuf modules from starwingMessage.proto.

Requirements:
    pip install grpcio-tools

Usage (from server/ directory):
    python scripts/generate_proto.py

This produces files in app/protocol/generated/:
    - starwingMessage_pb2.py
    - starwingMessage_pb2_grpc.py (if services were defined)
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    server_dir = Path(__file__).resolve().parent.parent
    proto_dir = server_dir / "app" / "protocol" / "proto"
    generated_dir = server_dir / "app" / "protocol" / "generated"
    proto_file = proto_dir / "starwingMessage.proto"

    if not proto_file.exists():
        print(f"ERROR: Proto file not found: {proto_file}", file=sys.stderr)
        sys.exit(1)

    generated_dir.mkdir(parents=True, exist_ok=True)

    try:
        from grpc_tools import protoc
    except ImportError:
        print(
            "ERROR: grpcio-tools not installed.\n  pip install grpcio-tools",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate Python stubs
    result = protoc.main(
        [
            "protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={generated_dir}",
            str(proto_file.name),
        ]
    )

    if result != 0:
        print(f"ERROR: protoc exited with code {result}", file=sys.stderr)
        sys.exit(result)

    # Write __init__.py if missing
    init_file = generated_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

    print(f"Generated protobuf modules in {generated_dir}")
    for f in sorted(generated_dir.glob("*.py")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
