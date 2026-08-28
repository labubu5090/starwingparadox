"""Analyze game log for G9 post-HTTP gating condition."""
import re
import json
import sys

LOG_PATH = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"

KEYWORDS = [
    "IsOnline", "bGameConnect", "bNesysServerLive", "MatchingConnect", "MatchingServer",
    "TcpConnect", "TcpThread", "SetupConnect", "TryToConnect", "GameConnect",
    "DispError", "Http", "matching/server", "matching/Matching",
    "ConnectAddress", "TcpLink", "ResolvedAddress", "ResolvedAddr",
    "GameSequence", "NextGameSequence", "RequestGameSequence", "SetGameSequence",
    "SystemDataCheck", "OpenKey", "PromotionMovie", "InsertStart", "Advertise",
    "CardReader", "NESYS", "Nesys", "nesys",
    "EXCEPTION", "OnCrash",
    "OnConnect", "OnDisconnect", "ConnectionComplete",
    "127.0.0.1:6666", "6666",
    "StateCheck", "CheckOpenKey", "NESYS Event",
    "OutGameSequenceWork",
    "GameServerPort", "GameServer",
    "HTTP Request", "HTTP Response",
    "Closing by request", "RequestExit",
    "LoadJsonFile", "SaveData",
    "CurrentLevelName", "TerminateLevel",
    "RankingDownload", "SendServer",
    "WindowString", "LoadKeyFile",
]

def main():
    with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    events = []
    for i, line in enumerate(lines):
        for kw in KEYWORDS:
            if kw.lower() in line.lower():
                ts_match = re.search(r"\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d+)\]", line)
                ts = ts_match.group(1) if ts_match else ""
                events.append({
                    "line": i + 1,
                    "ts": ts,
                    "content": line.rstrip(),
                })
                break

    events.sort(key=lambda x: x["line"])

    for e in events:
        print("L{line} [{ts}] {content}".format(**e)[:300])

    print(f"\nTotal events: {len(events)}")

    # Also dump to JSON for structured analysis
    with open(r"C:\Users\KAHO\Pictures\Starwing\docs\generated\g9_log_events.json", "w") as jf:
        json.dump(events, jf, indent=2)
    print(f"Wrote {len(events)} events to docs/generated/g9_log_events.json")


if __name__ == "__main__":
    main()
