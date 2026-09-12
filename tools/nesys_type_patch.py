import sys
import time
import os

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import (
    find_pid, module_base, open_game, read_mem, write_mem, write_fstring,
    read_fstring, OBJ_HTTPIP_OFF, CFGADDR_TEXT,
)

# VA 0x148EE1738 = &off_148EE1730 + 8  (ENesysGameServerType value byte)  -> RVA
TYPE_BYTE_RVA = 0x8EE1738
CFG_ADDR_RVA  = 0x8EE17B8
CFG_FLAG_RVA  = 0x8EE1804

GAME_EXE = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
GAME_DIR = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64"
GAME_ARGS = [
    "-UseConfigMatchingServer=1",
    "-DefaultMatchingServerAddress=127.0.0.1:6666",
    "-HttpServerAddress=127.0.0.1:4001",
    "-log",
]
LOG = r"C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\AcrGame.log"

SUCCESS_PATTERNS = [
    "OnReceiveResponseMatchingServer / _IsSuccess[1]",
    "SetConnectAddress / address[",
    "SHORT_MOCK_URL",
    "bHttpSuccess[1]",
    "GetHostAddress / HostURL[http://127",
]


def read_globals(h, base):
    raw = read_mem(h, base + TYPE_BYTE_RVA, 0x20)
    type_byte = raw[8] if raw and len(raw) >= 9 else None
    f = read_fstring(h, base + CFG_ADDR_RVA)
    flag = read_mem(h, base + CFG_FLAG_RVA, 1)
    return type_byte, f, flag


def patch(h, base):
    type_byte, cfg, flag = read_globals(h, base)
    print("[patch] before: type_byte=0x%02x cfg_addr=%r cfg_flag=%r" % (type_byte & 0xFF if type_byte is not None else 0xFF, cfg, flag.hex() if flag else None))
    if type_byte is not None and type_byte != 0:
        write_mem(h, base + TYPE_BYTE_RVA, b"\x00")
    ok1 = write_fstring(h, base + CFG_ADDR_RVA, CFGADDR_TEXT)
    ok2 = write_mem(h, base + CFG_FLAG_RVA, b"\x01")
    type_byte2, cfg2, flag2 = read_globals(h, base)
    print("[patch] after:  type_byte=0x%02x cfg_addr=%r cfg_flag=%r (fstring_ok=%s flag_ok=%s)"
          % (type_byte2 & 0xFF if type_byte2 is not None else 0xFF, cfg2, flag2.hex() if flag2 else None, ok1, ok2))


def tail_log(pos, maxlen=200000):
    try:
        size = os.path.getsize(LOG)
        if size <= pos:
            return pos, ""
        with open(LOG, "rb") as fh:
            fh.seek(max(0, size - maxlen))
            data = fh.read()
        text = data.decode("utf-8", errors="replace")
        return pos, text
    except Exception as e:
        return pos, ""


def main():
    pid = find_pid()
    if not pid:
        print("launching game...")
        os.system('start "" "%s" %s' % (GAME_EXE, " ".join(GAME_ARGS)))
        print("launched; waiting for process...")
        deadline = time.time() + 180
        while not pid and time.time() < deadline:
            time.sleep(2)
            pid = find_pid()
        if not pid:
            print("ERROR: game never appeared")
            return
    print("pid:", pid)
    base, size = module_base(pid)
    print("modbase: 0x%x  size: 0x%x" % (base or 0, size or 0))
    if not base:
        print("ERROR: no module base")
        return
    h = open_game(pid)
    if not h:
        print("ERROR: OpenProcess failed", ctypes_last_error())
        return
    print("open ok")

    # wait until the game reaches the matching phase (log shows the failure)
    pos = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    seen = False
    deadline = time.time() + 300
    while time.time() < deadline:
        pos, text = tail_log(pos)
        if "GetNesysGameServerHttpIP is empty." in text or "GetHostAddress" in text:
            seen = True
            break
        if find_pid() is None:
            print("game exited during wait")
            return
        time.sleep(2)

    print("matching phase reached (log: %s)" % seen)
    if not seen:
        print("WARNING: no matching log lines yet; proceeding anyway")

    patch(h, base)

    # keep the type byte zeroed (game may rewrite it), and watch for success
    start = time.time()
    posight = os.path.getsize(LOG)
    while time.time() - start < 180:
        if find_pid() is None:
            print("GAME EXITED (attract idle?)")
            return
        # re-zero type byte every poll
        raw = read_mem(h, base + TYPE_BYTE_RVA, 9)
        if raw:
            tb = raw[8]
            if tb != 0:
                write_mem(h, base + TYPE_BYTE_RVA, b"\x00")
                print("  re-zeroed type byte (was 0x%02x)" % tb)
        posight, text = tail_log(posight)
        for pat in SUCCESS_PATTERNS:
            if pat in text:
                print("  LOG HIT: " + pat)
        time.sleep(3)


def ctypes_last_error():
    import ctypes
    return ctypes.get_last_error()


if __name__ == "__main__":
    main()