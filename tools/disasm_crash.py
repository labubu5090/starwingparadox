import struct

EXE = r'X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe'
data = open(EXE, 'rb').read()

def rva_to_off(rva):
    e_lfanew = struct.unpack_from('<I', data, 0x3C)[0]
    nsec = struct.unpack_from('<H', data, e_lfanew+6)[0]
    optsize = struct.unpack_from('<H', data, e_lfanew+20)[0]
    off = e_lfanew + 24 + optsize
    for i in range(nsec):
        name = data[off:off+8].rstrip(b'\0').decode()
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, off+8)
        if vaddr <= rva < vaddr + vsize:
            return raddr + (rva - vaddr)
        off += 40
    return None

# Check the .text section bounds and what lies at these cave RVAs
for rva in [0x63FC89B, 0x63FC8AD, 0x63FC8CB, 0x63FC8D8, 0x63FC8D8+18, 0x63FD000]:
    fo = rva_to_off(rva)
    if fo is None:
        print(f'RVA 0x{rva:X}: no raw mapping (in gap)')
        continue
    chunk = data[fo:fo+8]
    print(f'RVA 0x{rva:X} -> raw 0x{fo:X}: {chunk.hex()}')

# What is the last section end?
e_lfanew = struct.unpack_from('<I', data, 0x3C)[0]
nsec = struct.unpack_from('<H', data, e_lfanew+6)[0]
optsize = struct.unpack_from('<H', data, e_lfanew+20)[0]
off = e_lfanew + 24 + optsize
for i in range(nsec):
    name = data[off:off+8].rstrip(b'\0').decode()
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, off+8)
    print(f'section {name}: VA 0x{vaddr:X} VSize 0x{vsize:X} ends 0x{vaddr+vsize:X} | raw 0x{raddr:X} size 0x{rsize:X}')
    off += 40