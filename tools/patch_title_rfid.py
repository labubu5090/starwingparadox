"""patch_title_rfid.py - unblock ACPP_TitleMain::CheckReadCard so the Title
advances to SystemDataCheck even when the RFID wrapper is stuck in an error
state (RFIDReadSerialAndID / error at Title BeginPlay).

Freeze mechanism (run4): BeginPlay calls RFIDReadSerialAndID when reception
time is active; it error'd at 00:02:09, so CheckReadCard's
`RFIDGetStatus() == RFID_STATUS_IDLE` guard never passes -> Title never calls
NextSequence(SystemDataCheck) -> game stuck with WBP_InsertStart looping.

CheckReadCard @0x142AF2E50 (sub_142AF2E50). Only the two RFID guard jumps are
patched (the other gates - retry timer/reception time/UUSBIO tickable - are
currently satisfied and stay untouched):
  0x142AF2EA1  75 3A  jnz (RFIDGetStatus != IDLE -> skip)   <-- blocker
  0x142AF2EB8  75 0C  jnz (RFIDGetResult != 0 -> retry/RFIDRead) -> NOP so we
                       never re-enter the failing RFID lay (always -> SDC).
With both NOP'd the function always falls through to
  mov dl,7  (SystemDataCheck) / jmp NextSequence(this, SystemDataCheck)
matching the run2/run3 healthy no-card path.
"""
import ctypes
import sys

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pid, module_base, open_game, read_mem, write_mem

PATCHES = [
    (0x2AF2EA1, bytes.fromhex("75 3A"), b"\x90\x90"),
    (0x2AF2EB8, bytes.fromhex("75 0C"), b"\x90\x90"),
]


def main():
    pid = find_pid()
    if not pid:
        print("ERROR: game not running")
        return
    base, size = module_base(pid)
    if not base:
        print("ERROR: no module base")
        return
    print("pid=%d  base=0x%x  size=0x%x" % (pid, base or 0, size or 0))
    h = open_game(pid)
    if not h:
        print("ERROR: OpenProcess failed", ctypes.get_last_error())
        return
    ok_all = True
    for rva, old, new in PATCHES:
        addr = base + rva
        before = read_mem(h, addr, len(old))
        if before == old:
            ok = write_mem(h, addr, new)
            back = read_mem(h, addr, len(new))
        else:
            ok = None
            back = before
        good = (before == old) and bool(ok) and (back == new)
        ok_all &= bool(good)
        print("[t] %08X before=%s applied=%s after=%s good=%s"
              % (addr, before.hex() if before else "?",
                 bool(ok) if ok is not None else "N/A",
                 back.hex() if back else "?", good))
    print("ALL_OK=%s" % ok_all)


if __name__ == "__main__":
    main()