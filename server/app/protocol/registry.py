"""Message type registry for the Starwing protocol."""

MESSAGE_TYPE_MAP: dict[int, str] = {
    0x65: "NotifyPushMessage",
    0x66: "Ping",
    0x67: "PingResponse",
    200: "RequestEntryMatching",
    201: "ResponseEntryMatching",
    0xCA: "RequestCancelMatching",  # 202
    0xCC: "NotifyMatchFailure",  # 204
    205: "ResponseEntryReMatching",
    206: "RequestJoinMatching",
     207: "ResponseJoinMatching",
    302: "NotifyMatchMade",
    304: "NotifyMatchBegin",
    601: "NotifyMatchOpen",
    208: "RequestEntryBurstGroup",
    209: "ResponseEntryBurstGroup",
    210: "RequestChangeBurstGroupMode",
    211: "ResponseChangeBurstGroupMode",
    214: "RequestUpdateBurstGroup",
    215: "ResponseUpdateBurstGroup",
    216: "RequestBurstGroupSelect",
    217: "ResponseBurstGroupSelect",
    307: "NotifyBurstGroupUpdated",
    308: "NotifyBurstGroupApply",
    310: "NotifyBurstMade",
    311: "NotifyBurstMeets",
}

REVERSE_MESSAGE_MAP: dict[str, int] = {v: k for k, v in MESSAGE_TYPE_MAP.items()}
