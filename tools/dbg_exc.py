import struct

dmp = r'C:\Users\KAHO\AppData\Local\AcrGame\Saved\Crashes\UE4CC-Windows-160665474D433411929A32BCCADD8FE4_0000\UE4Minidump.dmp'
data = open(dmp, 'rb').read()

# ExceptionStream at rva 0x654, size 168
drva = 0x654
print('Raw exception stream bytes:')
for i in range(0, 168, 16):
    b = data[drva+i:drva+i+16]
    hexs = ' '.join(f'{x:02X}' for x in b)
    print(f'+{i:02X}: {hexs}')

# Search for EXCEPTION_ACCESS_VIOLATION marker C0000005
print('\nSearching for C0000005 within exception stream:')
for off in range(0, 64):
    if data[drva+off:drva+off+4] == b'\xc0\x00\x00\x05':
        print(f'  Found at +{off} (rva 0x{drva+off:X})')
        # ThreadId is 4 bytes before the record start
        # record starts at off (ExceptionCode), then:
        # +0 code, +4 flags, +8 excrec ptr(8), +16 ExceptionAddress(8), +24 NParams(4), +28 align, +32 Info[0](8), +40 Info[1](8)
        exc_addr = struct.unpack_from('<Q', data, drva+off+16)[0]
        nparams = struct.unpack_from('<I', data, drva+off+24)[0]
        info0 = struct.unpack_from('<Q', data, drva+off+32)[0]
        info1 = struct.unpack_from('<Q', data, drva+off+40)[0]
        print(f'  ExceptionAddress (RIP): 0x{exc_addr:016X}')
        print(f'  NumberParameters: {nparams}')
        print(f'  Info[0]: 0x{info0:016X}')
        print(f'  Info[1]: 0x{info1:016X}')

print('\n=== RESULT ===')
# find game base: 8-byte 0x00007FF65DD20000 = bytes 00 00 D2 5D F6 7F 00 00
needle = struct.pack('<Q', 0x7ff65dd20000)
print('Game base needle:', needle.hex())
# The module list stream starts at 0x208C; count(4) then entries. Search first 2000 bytes of that region.
for off in range(0x208C, 0x208C+2000):
    if data[off:off+8] == needle:
        print(f'Game base 0x7ff65dd20000 found at rva 0x{off:X}')
        break