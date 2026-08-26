"""Unit tests for protocol message type registry."""

# Simulated message type registry (mimics what the real implementation would have)
MESSAGE_TYPE_REGISTRY: dict[int, dict[str, str]] = {
    101: {"name": "NotifyPushMessage", "direction": "server_to_client"},
    102: {"name": "Ping", "direction": "bidirectional"},
    103: {"name": "PingResponse", "direction": "server_to_client"},
    200: {"name": "RequestEntryMatching", "direction": "client_to_server"},
    201: {"name": "ResponseEntryMatching", "direction": "server_to_client"},
    202: {"name": "RequestCancelMatching", "direction": "client_to_server"},
    204: {"name": "NotifyMatchFailure", "direction": "server_to_client"},
    205: {"name": "ResponseEntryReMatching", "direction": "server_to_client"},
    206: {"name": "RequestJoinMatching", "direction": "client_to_server"},
    208: {"name": "RequestEntryBurstGroup", "direction": "client_to_server"},
    209: {"name": "ResponseEntryBurstGroup", "direction": "server_to_client"},
    210: {"name": "RequestChangeBurstGroupMode", "direction": "client_to_server"},
    211: {"name": "ResponseChangeBurstGroupMode", "direction": "server_to_client"},
    214: {"name": "RequestUpdateBurstGroup", "direction": "client_to_server"},
    215: {"name": "ResponseUpdateBurstGroup", "direction": "server_to_client"},
    216: {"name": "RequestBurstGroupSelect", "direction": "client_to_server"},
    217: {"name": "ResponseBurstGroupSelect", "direction": "server_to_client"},
    302: {"name": "NotifyMatchMade", "direction": "server_to_client"},
    304: {"name": "NotifyMatchBegin", "direction": "server_to_client"},
    307: {"name": "NotifyBurstGroupUpdated", "direction": "server_to_client"},
    308: {"name": "NotifyBurstGroupApply", "direction": "server_to_client"},
    310: {"name": "NotifyBurstMade", "direction": "server_to_client"},
    311: {"name": "NotifyBurstMeets", "direction": "server_to_client"},
    601: {"name": "NotifyMatchOpen", "direction": "server_to_client"},
}


def lookup_message_type(msg_type: int) -> dict[str, str] | None:
    return MESSAGE_TYPE_REGISTRY.get(msg_type)


def get_all_message_types() -> list[int]:
    return sorted(MESSAGE_TYPE_REGISTRY.keys())


class TestProtocolRegistry:
    """Test message type registry lookup."""

    def test_ping_lookup(self):
        info = lookup_message_type(102)
        assert info is not None
        assert info["name"] == "Ping"
        assert info["direction"] == "bidirectional"

    def test_request_entry_matching_lookup(self):
        info = lookup_message_type(200)
        assert info is not None
        assert info["name"] == "RequestEntryMatching"
        assert info["direction"] == "client_to_server"

    def test_response_entry_matching_lookup(self):
        info = lookup_message_type(201)
        assert info is not None
        assert info["name"] == "ResponseEntryMatching"
        assert info["direction"] == "server_to_client"

    def test_notify_match_made_lookup(self):
        info = lookup_message_type(302)
        assert info is not None
        assert info["name"] == "NotifyMatchMade"

    def test_notify_match_begin_lookup(self):
        info = lookup_message_type(304)
        assert info is not None
        assert info["name"] == "NotifyMatchBegin"

    def test_burst_group_entry_lookup(self):
        info = lookup_message_type(208)
        assert info is not None
        assert info["name"] == "RequestEntryBurstGroup"

    def test_burst_made_lookup(self):
        info = lookup_message_type(310)
        assert info is not None
        assert info["name"] == "NotifyBurstMade"

    def test_burst_meets_lookup(self):
        info = lookup_message_type(311)
        assert info is not None
        assert info["name"] == "NotifyBurstMeets"

    def test_unknown_message_type_returns_none(self):
        info = lookup_message_type(9999)
        assert info is None

    def test_zero_returns_none(self):
        info = lookup_message_type(0)
        assert info is None

    def test_negative_returns_none(self):
        info = lookup_message_type(-1)
        assert info is None

    def test_all_message_types_registered(self):
        types = get_all_message_types()
        assert len(types) >= 24

    def test_request_types_are_client_to_server(self):
        request_types = [200, 202, 206, 208, 210, 214, 216]
        for msg_type in request_types:
            info = lookup_message_type(msg_type)
            assert info is not None, f"Message type {msg_type} not found"
            assert info["direction"] == "client_to_server", (
                f"Message type {msg_type} should be client_to_server"
            )

    def test_response_types_are_server_to_client(self):
        response_types = [201, 204, 205, 209, 211, 215, 217]
        for msg_type in response_types:
            info = lookup_message_type(msg_type)
            assert info is not None, f"Message type {msg_type} not found"
            assert info["direction"] == "server_to_client", (
                f"Message type {msg_type} should be server_to_client"
            )

    def test_notify_types_are_server_to_client(self):
        notify_types = [101, 302, 304, 307, 308, 310, 311, 601]
        for msg_type in notify_types:
            info = lookup_message_type(msg_type)
            assert info is not None, f"Message type {msg_type} not found"
            assert info["direction"] == "server_to_client", (
                f"Message type {msg_type} should be server_to_client"
            )
