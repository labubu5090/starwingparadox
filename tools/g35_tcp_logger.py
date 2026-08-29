"""Minimal TCP frame logger for port 6666 matching traffic.
Captures raw TCP data on loopback, decodes length-prefixed frames,
logs hex dumps and protobuf analysis to JSON.
"""
import asyncio, json, struct, hashlib, time, os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "g35_tcp_frames.jsonl")
frames = []

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"[+] Client connected from {addr}")
    frame_count = 0
    while True:
        try:
            # Read 4-byte length prefix
            header = await reader.readexactly(4)
            if not header:
                break
            msg_len = struct.unpack(">I", header)[0]
            if msg_len > 10 * 1024 * 1024:
                print(f"[!] Frame too large: {msg_len}")
                break
            payload = await reader.readexactly(msg_len)
            frame_count += 1
            
            sha256 = hashlib.sha256(header + payload).hexdigest()
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Decode first few bytes as potential packet ID
            pkt_id = struct.unpack(">H", payload[:2])[0] if len(payload) >= 2 else None
            
            frame_data = {
                "frame": frame_count,
                "timestamp": timestamp,
                "direction": "server_recv",
                "length_prefix": list(header),
                "msg_len": msg_len,
                "payload_hex": payload[:64].hex(),
                "payload_len": len(payload),
                "sha256": sha256,
                "pkt_id": pkt_id,
                "first_4_bytes": list(payload[:4]) if len(payload) >= 4 else list(payload),
            }
            frames.append(frame_data)
            print(f"[{frame_count}] RECV {msg_len}B pkt_id={pkt_id} sha={sha256[:16]}")
            
            # Respond with Pong (0x67) if this was a Ping (0x66)
            if pkt_id == 0x66:
                pong = struct.pack(">H", 0x67) + payload[2:]
                pong_header = struct.pack(">I", len(pong))
                writer.write(pong_header + pong)
                await writer.drain()
                print(f"[{frame_count}] SENT Pong {len(pong)}B")
                pong_sha = hashlib.sha256(pong_header + pong).hexdigest()
                frames.append({
                    "frame": f"{frame_count}_pong",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "direction": "server_send",
                    "length_prefix": list(pong_header),
                    "msg_len": len(pong),
                    "payload_hex": pong[:64].hex(),
                    "payload_len": len(pong),
                    "sha256": pong_sha,
                    "pkt_id": 0x67,
                    "first_4_bytes": list(pong[:4]),
                })
            else:
                print(f"[{frame_count}] NON-PING pkt_id=0x{pkt_id:04x} - logged, no response sent")
        except asyncio.IncompleteReadError:
            print("[*] Client disconnected")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            break
    
    writer.close()
    await writer.wait_closed()
    print(f"[*] Client handler done. Total frames: {frame_count}")
    # Write all frames to JSON
    with open(LOG_PATH, "w") as f:
        json.dump(frames, f, indent=2)
    print(f"[*] Wrote {len(frames)} frames to {LOG_PATH}")

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 6666)
    print(f"[*] TCP frame logger listening on 127.0.0.1:6666")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
