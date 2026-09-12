import ctypes
import struct
import sys

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
from nesys_online_inject import find_pids, module_base, open_game, read_mem

print(memoryview(b''))  # noop to keep imports warm

def main():
    pids = find_pids()
    print('game pids:', pids)
    if not pids:
        return
    base, size = module_base(pids[0])
    print('base: 0x%X size: 0x%X' % (base, size))
    h = open_game(pids[0])
    if not h:
        print('open failed')
        return

    checks = [
        ('ibc-jmp @0x243D4A0', 0x243D4A0, 5, 'e9'),
        ('ibc-cave @0x63FC8D8', 0x63FC8D8, 18, '4885c9750331c0c3'),
        ('wm-cf50 @0x243CF50', 0x243CF50, 40, '85c074248b78300fb6483480e90280f9017715498bcee84528f90089fa4533c0488bc8e808fbffff'),
        ('ca80-jmp @0x243CA80', 0x243CA80, 5, 'e9'),
        ('stage-jmp @0x2DD8E50', 0x2DD8E50, 5, 'e9'),
        ('url-jnz @0x2C36309', 0x2C36309, 6, '909090909090'),
        ('select @0x2ADCE85', 0x2ADCE85, 6, '31c090'),
    ]
    for name, rva, length, expect_prefix in checks:
        mem = read_mem(h, base + rva, length)
        if mem is None:
            print('%-28s READ FAIL' % name)
            continue
        ok = 'OK' if mem[:len(expect_prefix)//2].hex().startswith(expect_prefix) else '??'
        print('%-28s %s %s (expect %s...)' % (name, ok, mem.hex(), expect_prefix))
    ctypes.windll.kernel32.CloseHandle(h)

main()