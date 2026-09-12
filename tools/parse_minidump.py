import struct, os, sys

dmp = r'C:\Users\KAHO\AppData\Local\AcrGame\Saved\Crashes\UE4CC-Windows-160665474D433411929A32BCCADD8FE4_0000\UE4Minidump.dmp'
data = open(dmp, 'rb').read()
print(f'Dump size: {len(data)} bytes')

# Print first 64 bytes raw
print('\n--- Raw header (first 64 bytes) ---')
for i in range(0, 64, 16):
    hex_str = ' '.join(f'{data[j]:02X}' for j in range(i, min(i+16, 64)))
    ascii_str = ''.join(chr(data[j]) if 32 <= data[j] < 127 else '.' for j in range(i, min(i+16, 64)))
    print(f'  +{i:02X}: {hex_str}  {ascii_str}')

# MINIDUMP_HEADER (32-bit fields, standard):
# +0:  Signature (ULONG32)
# +4:  Version (ULONG32)
# +8:  NumberOfStreams (ULONG32)
# +12: StreamDirectoryRva (ULONG32)
# +16: CheckSum (ULONG32)
# +20: TimeDateStamp (ULONG32)
# +24: Flags (ULONG32)
# +28: ModulesDirectory.DataSize (ULONG32)
# +32: ModulesDirectory.Rva (ULONG32)
# +36: MemoryListDirectory.DataSize (ULONG32)
# +40: MemoryListDirectory.Rva (ULONG32)

sig = struct.unpack_from('<I', data, 0)[0]
ver = struct.unpack_from('<I', data, 4)[0]
num_streams = struct.unpack_from('<I', data, 8)[0]
dir_rva = struct.unpack_from('<I', data, 12)[0]

print(f'\nSignature: 0x{sig:08X}')
print(f'Version: 0x{ver:08X}')
print(f'NumberOfStreams: {num_streams}')
print(f'StreamDirectoryRva: 0x{dir_rva:X}')

if dir_rva > len(data):
    print('ERROR: StreamDirectoryRva exceeds file size!')
    sys.exit(1)

# Parse stream directory entries
# Each entry: StreamType(4) + DataSize(4) + Rva(4) = 12 bytes
print(f'\n--- Stream Directory ({num_streams} entries) ---')
exc_addr = None
game_base = None

for i in range(num_streams):
    off = dir_rva + i * 12
    if off + 12 > len(data):
        print(f'  Stream {i}: OUT OF RANGE')
        break
    stype, dsize, drva = struct.unpack_from('<III', data, off)
    print(f'  Stream {i}: type={stype}, size={dsize}, rva=0x{drva:X}')
    
    if stype == 6:  # ExceptionStream
        print(f'    >>> ExceptionStream')
        # MINIDUMP_EXCEPTION_STREAM: ThreadId(4) + EXCEPTION_RECORD64(152) + ThreadContext(8)
        # EXCEPTION_RECORD64: Code(4) Flags(4) ExRecord-ptr(8) ExAddress(8) NParams(4) align(4) Info[15](120)
        if drva + 48 > len(data):
            print(f'    ERROR: stream data out of range')
            continue
        # Try aligned layout (ExceptionRecord starts at +8 after ThreadId + 4 pad)
        rec = drva + 8
        tid = struct.unpack_from('<I', data, drva)[0]
        exc_code = struct.unpack_from('<I', data, rec)[0]
        exc_flags = struct.unpack_from('<I', data, rec+4)[0]
        exc_addr = struct.unpack_from('<Q', data, rec+16)[0]
        exc_nparams = struct.unpack_from('<I', data, rec+24)[0]
        exc_param0 = struct.unpack_from('<Q', data, rec+32)[0] if exc_nparams > 0 else 0
        exc_param1 = struct.unpack_from('<Q', data, rec+40)[0] if exc_nparams > 1 else 0
        if exc_code != 0xC0000005 and exc_nparams not in (0, 1, 2, 15):
            # try packed layout (ExceptionRecord starts at +4)
            rec = drva + 4
            tid = struct.unpack_from('<I', data, drva)[0]
            exc_code = struct.unpack_from('<I', data, rec)[0]
            exc_flags = struct.unpack_from('<I', data, rec+4)[0]
            exc_addr = struct.unpack_from('<Q', data, rec+16)[0]
            exc_nparams = struct.unpack_from('<I', data, rec+24)[0]
            exc_param0 = struct.unpack_from('<Q', data, rec+32)[0] if exc_nparams > 0 else 0
            exc_param1 = struct.unpack_from('<Q', data, rec+40)[0] if exc_nparams > 1 else 0
            layout = 'packed'
        else:
            layout = 'aligned'
        print(f'    Layout: {layout}')
        print(f'    ThreadId: {tid}')
        print(f'    ExceptionCode: 0x{exc_code:08X}')
        print(f'    ExceptionFlags: 0x{exc_flags:08X}')
        print(f'    ExceptionAddress (RIP): 0x{exc_addr:016X}')
        print(f'    NumberParameters: {exc_nparams}')
        print(f'    Info[0] (faulting addr): 0x{exc_param0:016X}')
        print(f'    Info[1]: 0x{exc_param1:016X}')

    if stype == 4:  # ModuleListStream
        print(f'    >>> ModuleListStream at rva=0x{drva:X}')
        if drva + 4 > len(data):
            print(f'    ERROR: stream data out of range')
            continue
        nmodules = struct.unpack_from('<I', data, drva)[0]
        print(f'    NumberOfModules: {nmodules}')
        
        # MINIDUMP_MODULE in 64-bit dump: BaseOfImage is ULONG32 in the struct
        # Total struct size: 108 bytes (common in practice for 64-bit minidumps)
        # But let's try to validate by checking if the first module name is readable
        
        for stride in [108, 104]:
            for pad in [0, 4]:
                base_off = drva + 4 + pad
                if base_off + stride > len(data):
                    continue
                moff = base_off
                base_img = struct.unpack_from('<I', data, moff)[0]
                size_img = struct.unpack_from('<I', data, moff+4)[0]
                name_rva = struct.unpack_from('<I', data, moff+16)[0]
                
                valid = True
                name = '<invalid>'
                if name_rva > 0 and name_rva + 4 < len(data):
                    name_len = struct.unpack_from('<H', data, name_rva)[0]
                    if 0 < name_len < 200 and name_rva + 2 + name_len <= len(data):
                        name_bytes = data[name_rva+2:name_rva+2+name_len]
                        name = name_bytes.decode('ascii', errors='replace')
                        if not any(c in name for c in ['\\', '/', '.']):
                            valid = False
                    else:
                        valid = False
                else:
                    valid = False
                
                if valid:
                    print(f'    VALID config: stride={stride}, pad={pad}')
                    print(f'    First module: base=0x{base_img:08X}, size=0x{size_img:X}, name="{name}"')
                    
                    # Now list ALL modules
                    for j in range(nmodules):
                        moff = base_off + j * stride
                        if moff + stride > len(data):
                            break
                        base_img = struct.unpack_from('<I', data, moff)[0]
                        size_img = struct.unpack_from('<I', data, moff+4)[0]
                        name_rva = struct.unpack_from('<I', data, moff+16)[0]
                        if name_rva > 0 and name_rva + 4 < len(data):
                            name_len = struct.unpack_from('<H', data, name_rva)[0]
                            if 0 < name_len < 200 and name_rva + 2 + name_len <= len(data):
                                name_bytes = data[name_rva+2:name_rva+2+name_len]
                                name = name_bytes.decode('ascii', errors='replace')
                            else:
                                name = '?'
                        else:
                            name = '?'
                        is_game = 'AcrGame' in name or 'Starwing' in name
                        marker = ' <<<< TARGET' if is_game else ''
                        print(f'    [{j:2d}] 0x{base_img:08X} +0x{size_img:06X} "{name}"{marker}')
                        if is_game:
                            game_base = base_img
                    break
            if game_base is not None:
                break

print(f'\n=== RESULTS ===')
if exc_addr:
    print(f'Exception RIP: 0x{exc_addr:016X}')
if game_base:
    print(f'Game base: 0x{game_base:016X}')
    rva = exc_addr - game_base
    print(f'Crash RVA: 0x{rva:X}')
    ida_addr = rva + 0x140000000
    print(f'IDA address: 0x{ida_addr:016X}')
elif exc_addr:
    # Fallback: use known base
    known_base = 0x7ff65dd20000
    rva = exc_addr - known_base
    print(f'Game base not found in dump, using known base 0x{known_base:016X}')
    print(f'Crash RVA (assumed): 0x{rva:X}')
    ida_addr = rva + 0x140000000
    print(f'IDA address (assumed): 0x{ida_addr:016X}')
