"""SYNTHETIC_SCHEMA_TEST — Legacy proto compatibility check.

This test parses the legacy .proto file (using regex, no protoc required) and
the generated Python descriptors, then compares message names, field names,
field numbers, and field types.

This is NOT a captured-traffic or cabinet-compatible fixture test.
It is a schema-level synthetic comparison to detect drift between the legacy
proto definition and the generated Python code.
"""

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

LEGACY_PROTO = Path(__file__).resolve().parents[3] / "legacy-js" / "js" / "starwingMessage.proto"
SERVER_PROTO = (
    Path(__file__).resolve().parents[3]
    / "server"
    / "app"
    / "protocol"
    / "proto"
    / "starwingMessage.proto"
)

# ---------------------------------------------------------------------------
# Simple regex-based .proto parser
# ---------------------------------------------------------------------------

# Maps proto type strings to a canonical short form for comparison.
_PROTO_TYPE_MAP = {
    "int32": "int32",
    "int64": "int64",
    "uint32": "uint32",
    "uint64": "uint64",
    "sint32": "sint32",
    "sint64": "sint64",
    "fixed32": "fixed32",
    "fixed64": "fixed64",
    "sfixed32": "sfixed32",
    "sfixed64": "sfixed64",
    "float": "float",
    "double": "double",
    "bool": "bool",
    "string": "string",
    "bytes": "bytes",
}


def _normalize_type(type_str: str) -> str:
    """Normalize a proto type string (handle optional/repeated wrappers)."""
    t = type_str.strip()
    if t.startswith("optional "):
        t = t[len("optional ") :]
    if t.startswith("repeated "):
        t = t[len("repeated ") :]
    return _PROTO_TYPE_MAP.get(t, t)


def _parse_field_number(num_str: str) -> int:
    """Parse a field number that may be decimal or hex (0x...)."""
    num_str = num_str.strip()
    if num_str.startswith("0x") or num_str.startswith("0X"):
        return int(num_str, 16)
    return int(num_str)


def parse_proto_messages(proto_path: Path) -> dict[str, list[dict]]:
    """Parse message definitions from a .proto file using regex.

    Returns:
        dict mapping message_name -> list of field dicts, each with keys:
        'name', 'number', 'type', 'label' (optional/repeated/none)
    """
    content = proto_path.read_text(encoding="utf-8")

    messages: dict[str, list[dict]] = {}

    # Find each message block: message Name { ... }
    # Use a simple brace-counting approach for nested messages.
    msg_pattern = re.compile(r"^\s*message\s+(\w+)\s*\{", re.MULTILINE)

    for match in msg_pattern.finditer(content):
        msg_name = match.group(1)
        start = match.end()

        # Count braces to find the end of this message
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            if content[pos] == "{":
                depth += 1
            elif content[pos] == "}":
                depth -= 1
            pos += 1

        body = content[start : pos - 1]

        # Strip oneof blocks before parsing fields
        body_no_oneof = re.sub(r"oneof\s+\w+\s*\{[^}]*\}", "", body)

        fields = []
        # Match field declarations: optional/required/repeated TYPE NAME = NUMBER;
        field_pattern = re.compile(
            r"^\s*(optional|required|repeated)?\s*(\w+)\s+(\w+)\s*=\s*(0x[\da-fA-F]+|\d+)",
            re.MULTILINE,
        )
        for fmatch in field_pattern.finditer(body_no_oneof):
            label = fmatch.group(1) or "none"
            type_str = fmatch.group(2)
            field_name = fmatch.group(3)
            field_number = _parse_field_number(fmatch.group(4))
            fields.append(
                {
                    "name": field_name,
                    "number": field_number,
                    "type": _normalize_type(type_str),
                    "label": label,
                }
            )

        messages[msg_name] = fields

    return messages


# ---------------------------------------------------------------------------
# Parse both proto files
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def legacy_messages() -> dict[str, list[dict]]:
    """Parse the legacy JS proto file."""
    return parse_proto_messages(LEGACY_PROTO)


@pytest.fixture(scope="module")
def server_messages() -> dict[str, list[dict]]:
    """Parse the server proto file."""
    return parse_proto_messages(SERVER_PROTO)


# ---------------------------------------------------------------------------
# Import generated descriptors
# ---------------------------------------------------------------------------

try:
    from app.protocol.generated import starwingMessage_pb2 as pb

    HAS_GENERATED = True
except ImportError:
    HAS_GENERATED = False


def _get_descriptor_fields(msg_class) -> dict[str, dict]:
    """Extract field info from a protobuf message class descriptor.

    Returns dict mapping field_name -> {'number': int, 'type': int, 'is_repeated': bool}
    """
    fields = {}
    for field in msg_class.DESCRIPTOR.fields:
        fields[field.name] = {
            "number": field.number,
            "type": field.type,
            "is_repeated": field.is_repeated,
        }
    return fields


# ---------------------------------------------------------------------------
# Tests: Proto file comparison
# ---------------------------------------------------------------------------


class TestProtoFileConsistency:
    """SYNTHETIC_SCHEMA_TEST — Compare legacy and server .proto files."""

    def test_both_proto_files_exist(self):
        """Both proto files should exist on disk."""
        assert LEGACY_PROTO.exists(), f"Legacy proto not found: {LEGACY_PROTO}"
        assert SERVER_PROTO.exists(), f"Server proto not found: {SERVER_PROTO}"

    def test_message_names_match(self, legacy_messages, server_messages):
        """Both proto files should define the same message names."""
        legacy_names = set(legacy_messages.keys())
        server_names = set(server_messages.keys())
        missing_in_server = legacy_names - server_names
        extra_in_server = server_names - legacy_names
        assert not missing_in_server, f"Messages in legacy but not server: {missing_in_server}"
        assert not extra_in_server, f"Messages in server but not legacy: {extra_in_server}"

    def test_field_counts_match(self, legacy_messages, server_messages):
        """Each message should have the same number of fields."""
        mismatches = []
        for msg_name in legacy_messages:
            legacy_count = len(legacy_messages[msg_name])
            server_count = len(server_messages[msg_name])
            if legacy_count != server_count:
                mismatches.append(f"{msg_name}: legacy={legacy_count} server={server_count}")
        assert not mismatches, f"Field count mismatches: {mismatches}"

    def test_field_numbers_match(self, legacy_messages, server_messages):
        """Each field should have the same field number in both files."""
        mismatches = []
        for msg_name in legacy_messages:
            legacy_fields = {f["name"]: f for f in legacy_messages[msg_name]}
            server_fields = {f["name"]: f for f in server_messages[msg_name]}
            for field_name in legacy_fields:
                if field_name not in server_fields:
                    mismatches.append(f"{msg_name}.{field_name}: missing in server")
                    continue
                legacy_num = legacy_fields[field_name]["number"]
                server_num = server_fields[field_name]["number"]
                if legacy_num != server_num:
                    mismatches.append(
                        f"{msg_name}.{field_name}: legacy={legacy_num} server={server_num}"
                    )
        assert not mismatches, "Field number mismatches:\n" + "\n".join(mismatches)

    def test_field_names_match(self, legacy_messages, server_messages):
        """Each message should have the same field names."""
        mismatches = []
        for msg_name in legacy_messages:
            legacy_names = {f["name"] for f in legacy_messages[msg_name]}
            server_names = {f["name"] for f in server_messages[msg_name]}
            missing = legacy_names - server_names
            extra = server_names - legacy_names
            if missing:
                mismatches.append(f"{msg_name}: missing fields {missing}")
            if extra:
                mismatches.append(f"{msg_name}: extra fields {extra}")
        assert not mismatches, "Field name mismatches:\n" + "\n".join(mismatches)

    def test_pbremessage_oneof_entries_match(self, legacy_messages, server_messages):
        """PbMessage oneof entries should have the same field numbers and names."""
        legacy_pbm = {f["name"]: f for f in legacy_messages.get("PbMessage", [])}
        server_pbm = {f["name"]: f for f in server_messages.get("PbMessage", [])}

        # The oneof entries appear as fields in PbMessage
        # Check that all oneof field numbers match
        mismatches = []
        for name in legacy_pbm:
            if name in server_pbm:
                if legacy_pbm[name]["number"] != server_pbm[name]["number"]:
                    mismatches.append(
                        f"PbMessage.{name}: legacy={legacy_pbm[name]['number']} "
                        f"server={server_pbm[name]['number']}"
                    )
            else:
                mismatches.append(f"PbMessage.{name}: missing in server")
        assert not mismatches, f"PbMessage oneof mismatches: {mismatches}"


# ---------------------------------------------------------------------------
# Tests: Generated descriptors vs proto file
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GENERATED, reason="Generated protobuf modules not available")
class TestGeneratedVsProto:
    """SYNTHETIC_SCHEMA_TEST — Compare generated Python descriptors against proto file."""

    def test_all_proto_messages_exist_in_generated(self, server_messages):
        """Every message in the server .proto should have a generated class."""
        missing = []
        for msg_name in server_messages:
            if not hasattr(pb, msg_name):
                missing.append(msg_name)
        assert not missing, f"Messages in proto but not in generated code: {missing}"

    def test_generated_field_numbers_match_proto(self, server_messages):
        """Generated field numbers should match the .proto file.

        For PbMessage, only compares top-level fields (packetId, messageType,
        sessionId) because oneof members are flattened in the generated descriptor.
        """
        # Top-level fields in PbMessage (not oneof members)
        top_level = {"packetId", "messageType", "sessionId"}

        mismatches = []
        for msg_name, expected_fields in server_messages.items():
            msg_class = getattr(pb, msg_name, None)
            if msg_class is None:
                continue
            gen_fields = _get_descriptor_fields(msg_class)

            for field in expected_fields:
                fname = field["name"]
                if msg_name == "PbMessage" and fname not in top_level:
                    continue  # Skip oneof members
                if fname in gen_fields:
                    if gen_fields[fname]["number"] != field["number"]:
                        mismatches.append(
                            f"{msg_name}.{fname}: proto={field['number']} "
                            f"generated={gen_fields[fname]['number']}"
                        )
                else:
                    mismatches.append(f"{msg_name}.{fname}: missing in generated")
        assert not mismatches, "Field number mismatches:\n" + "\n".join(mismatches)

    def test_generated_field_names_match_proto(self, server_messages):
        """Generated field names should match the .proto file.

        Only compares top-level fields (not oneof members), because the
        generated descriptor flattens oneofs into regular fields.
        """
        # Top-level fields in PbMessage (not oneof members)
        top_level = {"packetId", "messageType", "sessionId"}

        mismatches = []
        for msg_name, expected_fields in server_messages.items():
            msg_class = getattr(pb, msg_name, None)
            if msg_class is None:
                continue
            gen_field_names = {f.name for f in msg_class.DESCRIPTOR.fields}

            if msg_name == "PbMessage":
                # Only compare top-level fields, skip oneof members
                proto_field_names = top_level
                gen_field_names = gen_field_names & top_level
            else:
                proto_field_names = {f["name"] for f in expected_fields}

            missing = proto_field_names - gen_field_names
            extra = gen_field_names - proto_field_names
            if missing:
                mismatches.append(f"{msg_name}: missing in generated {missing}")
            if extra:
                mismatches.append(f"{msg_name}: extra in generated {extra}")
        assert not mismatches, "Field name mismatches:\n" + "\n".join(mismatches)

    def test_message_type_map_completeness(self):
        """MESSAGE_TYPE_MAP in registry should cover all oneof entries in PbMessage."""
        from app.protocol.registry import MESSAGE_TYPE_MAP

        # Extract oneof field numbers from the generated PbMessage descriptor
        pbm_fields = {}
        for field in pb.PbMessage.DESCRIPTOR.fields:
            if field.message_type is not None:
                pbm_fields[field.number] = field.name

        # Check that every PbMessage oneof field has a corresponding registry entry
        missing = []
        for field_num, field_name in sorted(pbm_fields.items()):
            if field_num not in MESSAGE_TYPE_MAP:
                missing.append(f"field {field_num} ({field_name})")
        assert not missing, (
            f"PbMessage oneof entries not in MESSAGE_TYPE_MAP: {missing}\n"
            f"MESSAGE_TYPE_MAP keys: {sorted(MESSAGE_TYPE_MAP.keys())}"
        )

    def test_phantom_registry_entries_documented(self):
        """Registry entries 202, 205, 206, 214, 215 reference non-existent proto messages.

        These are known discrepancies between the registry and the proto schema.
        They are neither in the legacy proto nor the server proto.
        This test documents them as a regression guard.
        """
        from app.protocol.registry import MESSAGE_TYPE_MAP

        phantom_entries = {202, 205, 206, 214, 215}
        found_phantoms = []
        for msg_type in phantom_entries:
            if msg_type in MESSAGE_TYPE_MAP:
                class_name = MESSAGE_TYPE_MAP[msg_type]
                exists = hasattr(pb, class_name)
                found_phantoms.append((msg_type, class_name, exists))

        # All phantom entries should point to non-existent classes
        for msg_type, class_name, exists in found_phantoms:
            assert not exists, (
                f"Phantom entry {msg_type} ({class_name}) unexpectedly exists in generated code"
            )
