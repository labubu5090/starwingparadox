"""TCP protocol handlers for matching and battle flows.

Handles RequestEntryMatching (200), RequestCancelMatching (202),
RequestJoinMatching (206), and RequestEntryBurstGroup (208).
Sends back proper protobuf responses including NotifyMatchMade (302)
and NotifyMatchBegin (304) with CPU opponents.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from app.protocol.codec import encode_length_prefix
from app.protocol.registry import REVERSE_MESSAGE_MAP

logger = logging.getLogger(__name__)

try:
    from app.protocol.generated import starwingMessage_pb2 as pb

    HAS_PB = True
except ImportError:
    HAS_PB = False
    logger.warning("protobuf modules not available; matching handlers disabled")


_match_counter = 10000

# Normal-mode stages present in StageTable.csv (ModeID=0) whose assets exist
# on disk. The client always asks for 10000, but we rotate so matches vary.
_NORMAL_STAGE_IDS = [10000, 10100, 10102, 10202, 11100, 11200, 12100, 12200, 13100]


def _next_match_id() -> int:
    global _match_counter
    _match_counter += 1
    return _match_counter


def _build_player(
    player_id: int = 10010,
    buddy_id: int = 5,
    card_id: int = 7020392000000000,
    mac_address: int = 247207015480323,
    player_name: str = "ArcadeMachinist",
    location_id: int = 77,
    location_name: str = "ZenGarden",
) -> Any:
    """Build a Player matching the proven working legacy payload.

    The player's own team is the ONLY team in the match. With VsCPU=true the
    game generates the CPU opponents itself, so we only need to describe the
    human player's side (mirrors legacy-js/js/starwing.js NotifyMatchMade).

    IMPORTANT: PlayerId MUST echo the requesting player's UserId, otherwise the
    client logs "Not existence matching team my ID[...]" and fails the match.
    """
    p = pb.Player()
    p.PlayerId = player_id
    p.MacAddress = mac_address
    p.CardId = card_id
    p.PlayerName = player_name
    p.PlayerRank = 20
    p.BuddyId = buddy_id
    p.LocationId = location_id
    p.LocationName = location_name
    p.Intrude = False
    p.OfficialType = 0
    p.BurstGroupId = 0
    p.BurstNum = 0
    p.Rank2on2 = 20
    return p


def _build_buddy(player_id: int = 10011) -> Any:
    p = pb.Player()
    p.PlayerId = player_id
    p.MacAddress = 12346
    p.CardId = 7020392000000001
    p.PlayerName = "LordCereth"
    p.PlayerRank = 20
    p.BuddyId = 2
    p.LocationId = 77
    p.LocationName = "ZenGarden"
    p.Intrude = False
    p.OfficialType = 0
    p.BurstGroupId = 0
    p.BurstNum = 0
    p.Rank2on2 = 20
    return p


def _make_entry_matching_response(packet_id: int, timeout: int = 30) -> bytes:
    """Build ResponseEntryMatching (201) frame."""
    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 201
    resp = msg.ResponseEntryMatching
    resp.messageId = packet_id
    resp.timeout = timeout
    return encode_length_prefix(msg.SerializeToString())


def _make_notify_match_made(
    packet_id: int,
    match_id: int,
    stage_id: int = 10000,
    game_mode: int = 0,
    match_mode: int = 0,
    num_cpu: int = 2,
    play_mode: int = 101,
    player_id: int = 10010,
    card_id: int = 7020392000000000,
    mac_address: int = 247207015480323,
    player_name: str = "ArcadeMachinist",
    location_id: int = 77,
    location_name: str = "ZenGarden",
) -> bytes:
    """Build NotifyMatchMade (302) reflecting the proven working VsCPU flow.

    Mirrors legacy-js/js/starwing.js: a single Team listing the human player
    (plus a buddy); VsCPU=true lets the client spawn CPU opponents. PlayMode
    101, StageId 10000, StartState 1, MatchType 1.
    """
    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 302

    nmm = msg.NotifyMatchMade
    nmm.Match.MatchId = match_id
    nmm.Match.State = 1
    nmm.Match.PlayMode = play_mode
    nmm.Match.Difficulty = 0
    nmm.Match.CoopModeIndex = 0
    nmm.Match.MatchGroup = 0
    nmm.Match.StageId = stage_id
    nmm.Match.Version = "70571"
    nmm.Match.MatchMode = match_mode
    nmm.Match.Tournament = False
    nmm.Match.Event = False
    nmm.Match.VsCPU = True
    nmm.Match.EndTime = 0
    nmm.Match.StageMode = 0
    nmm.Match.PlayZone = 0
    nmm.Match.RuleId = 1
    nmm.Match.GameMode = game_mode

    player_team = nmm.Match.Team.add()
    player_team.PlayerCount = num_cpu
    player_team.PinchLevel = 0
    player_team.Force = 0
    player_team.Player.append(_build_player(
        player_id=player_id,
        card_id=card_id,
        mac_address=mac_address,
        player_name=player_name,
        location_id=location_id,
        location_name=location_name,
    ))
    if num_cpu > 1:
        player_team.Player.append(_build_buddy())

    nmm.ds.ServerId = 6789
    nmm.ds.State = 1
    nmm.ds.address = ""
    nmm.ds.version = "70571"
    nmm.ds.language = "0"

    nmm.MatchType = 1
    nmm.GameMode = game_mode
    nmm.StageId = stage_id

    return encode_length_prefix(msg.SerializeToString())


def _make_notify_match_begin(packet_id: int, match_id: int) -> bytes:
    """Build NotifyMatchBegin (304) frame."""
    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 304
    msg.NotifyMatchBegin.MatchId = match_id
    return encode_length_prefix(msg.SerializeToString())


def _make_response_join_matching(packet_id: int, result: int = 0) -> bytes:
    """Build ResponseJoinMatching (207) frame.

    Mirrors the game binary schema:
        message ResponseJoinMatching {
            int64 messageId = 1;
            int32 result = 2; // 0 OK_Joined, 1 NG_EndBattle, 2 NG_ServerError
        }
    """
    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 207
    resp = msg.ResponseJoinMatching
    resp.messageId = packet_id
    resp.result = result
    return encode_length_prefix(msg.SerializeToString())


async def handle_entry_matching(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestEntryMatching (200).

    1. Decode the request to extract game mode / stage info.
    2. Send ResponseEntryMatching (201) immediately.
    3. After a short delay, push NotifyMatchMade (302) with CPU opponents.
    4. Then push NotifyMatchBegin (304).
    """
    if not HAS_PB:
        logger.error("Cannot handle matching: protobuf not available")
        return None

    try:
        envelope = pb.PbMessage()
        envelope.ParseFromString(raw_payload)
    except Exception as e:
        logger.warning("Failed to parse RequestEntryMatching envelope: %s", e)
        envelope = pb.PbMessage()

    request = envelope.RequestEntryMatching

    stage_id = getattr(request, "StageId", 0) or 10000
    # Rotate maps: when the client asks for the default stage (10000), pick a
    # random normal stage so the user does not play the same map every match.
    if stage_id == 10000:
        stage_id = random.choice(_NORMAL_STAGE_IDS)
    game_mode = getattr(request, "GameMode", 0) or 0
    match_mode = getattr(request, "MatchMode", 0) or 0
    play_mode = getattr(request, "PlayMode", 0) or 101
    user_id = getattr(request, "UserId", 0)
    card_id = getattr(request, "CardId", 0)
    mac_address = getattr(request, "MacAddress", 0)
    location_id = getattr(request, "LocationId", 0) or 77
    location_name = getattr(request, "LocationName", "") or "ZenGarden"

    logger.info(
        "RequestEntryMatching: userId=%d cardId=%d stageId=%d gameMode=%d matchMode=%d",
        user_id, card_id, stage_id, game_mode, match_mode,
    )

    match_id = _next_match_id()

    # Step 1: Send ResponseEntryMatching (201)
    resp = _make_entry_matching_response(packet_id, timeout=30)

    # Step 2: After delay, push NotifyMatchMade + NotifyMatchBegin
    if writer is not None:
        try:
            writer.write(resp)
            await writer.drain()
            logger.info("Sent ResponseEntryMatching (201) matchId=%d", match_id)

            await asyncio.sleep(1.0)

            made_frame = _make_notify_match_made(
                packet_id=packet_id,
                match_id=match_id,
                stage_id=stage_id,
                game_mode=game_mode,
                match_mode=match_mode,
                num_cpu=1,
                play_mode=play_mode,
                player_id=user_id or 10010,
                card_id=card_id,
                mac_address=mac_address,
                player_name="Player%d" % user_id if user_id else "ArcadeMachinist",
                location_id=location_id,
                location_name=location_name,
            )
            writer.write(made_frame)
            await writer.drain()
            logger.info("Sent NotifyMatchMade (302) matchId=%d", match_id)

            await asyncio.sleep(0.5)

            begin_frame = _make_notify_match_begin(packet_id, match_id)
            writer.write(begin_frame)
            await writer.drain()
            logger.info("Sent NotifyMatchBegin (304) matchId=%d", match_id)
        except Exception as e:
            logger.error("Error sending matching response: %s", e)

    return None


async def handle_cancel_matching(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestCancelMatching (202)."""
    logger.info("RequestCancelMatching received")
    return None


async def handle_join_matching(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestJoinMatching (206)."""
    logger.info("RequestJoinMatching received")
    if not HAS_PB:
        return None

    envelope = pb.PbMessage()
    try:
        envelope.ParseFromString(raw_payload)
    except Exception as e:
        logger.warning("Failed to parse RequestJoinMatching envelope: %s", e)
        return None

    request = envelope.RequestJoinMatching
    # RequestJoinMatching schema (per game binary): id=1, matchId=2
    match_id = getattr(request, "matchId", 0) or _next_match_id()
    logger.info("RequestJoinMatching: MatchId=%d", match_id)

    if writer is not None:
        try:
            open_frame = _make_response_join_matching(packet_id, result=0)
            writer.write(open_frame)
            await writer.drain()
            logger.info("Sent ResponseJoinMatching (207) matchId=%d result=0(OK_Joined)", match_id)
        except Exception as e:
            logger.error("Error sending ResponseJoinMatching: %s", e)

    return None


async def handle_entry_burst_group(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestEntryBurstGroup (208)."""
    logger.info("RequestEntryBurstGroup received")
    if not HAS_PB:
        return None

    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 209
    resp = msg.ResponseEntryBurstGroup
    resp.messageId = packet_id
    resp.timeout = 30
    resp.BurstNumMax = 4
    return encode_length_prefix(msg.SerializeToString())


async def handle_change_burst_group_mode(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestChangeBurstGroupMode (210)."""
    logger.info("RequestChangeBurstGroupMode received")
    if not HAS_PB:
        return None

    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 211
    resp = msg.ResponseChangeBurstGroupMode
    resp.messageId = packet_id
    resp.Result = 0
    resp.StageId = 10000
    return encode_length_prefix(msg.SerializeToString())


async def handle_update_burst_group(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestUpdateBurstGroup (214)."""
    logger.info("RequestUpdateBurstGroup received")
    if not HAS_PB:
        return None

    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 215
    return encode_length_prefix(msg.SerializeToString())


async def handle_burst_group_select(
    packet_id: int,
    message_type: int,
    message_name: str,
    raw_payload: bytes,
    writer: Any = None,
) -> bytes | None:
    """Handle RequestBurstGroupSelect (216)."""
    logger.info("RequestBurstGroupSelect received")
    if not HAS_PB:
        return None

    msg = pb.PbMessage()
    msg.packetId = packet_id
    msg.messageType = 217
    resp = msg.ResponseBurstGroupSelect
    resp.messageId = packet_id
    resp.Result = 0
    resp.Timeout = 30
    return encode_length_prefix(msg.SerializeToString())


def register_matching_handlers(tcp_register_fn) -> None:
    """Register all matching/burst handlers with the TCP server."""
    tcp_register_fn(200, handle_entry_matching)
    tcp_register_fn(0xCA, handle_cancel_matching)
    tcp_register_fn(206, handle_join_matching)
    tcp_register_fn(208, handle_entry_burst_group)
    tcp_register_fn(210, handle_change_burst_group_mode)
    tcp_register_fn(214, handle_update_burst_group)
    tcp_register_fn(216, handle_burst_group_select)
    logger.info("Matching handlers registered for messageTypes: 200, 202, 206, 208, 210, 214, 216")
