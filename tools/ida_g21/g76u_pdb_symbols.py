"""Read PDB public symbols via DbgHelp SymInitialize/SymLoadModuleEx/SymEnumSymbols.
Extract addresses for weapon-pack related functions."""
import ctypes
import ctypes.wintypes as wt
import os, json

OUT = r"C:\Users\KAHO\Pictures\Starwing\tools\ida_g21\out\g76u_pdb_symbols.json"
PDB = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.pdb"

dbghelp = ctypes.WinDLL("dbghelp", use_last_error=True)

SymInitialize = dbghelp.SymInitialize
SymInitialize.argtypes = [wt.HANDLE, wt.LPCWSTR, wt.BOOL]
SymInitialize.restype = wt.BOOL

SymCleanup = dbghelp.SymCleanup
SymCleanup.argtypes = [wt.HANDLE]
SymCleanup.restype = wt.BOOL

class MODULEINFO(ctypes.Structure):
    _fields_ = [("BaseOfDll", ctypes.c_void_p),
                ("SizeOfImage", wt.DWORD),
                ("EntryPoint", ctypes.c_void_p)]

SymLoadModuleEx = dbghelp.SymLoadModuleExW
SymLoadModuleEx.argtypes = [wt.HANDLE, wt.HANDLE, wt.LPWSTR, wt.LPWSTR,
                            ctypes.c_void_p, wt.DWORD, wt.DWORD, ctypes.c_void_p]
SymLoadModuleEx.restype = ctypes.c_void_p

SymEnumSymbols = dbghelp.SymEnumSymbolsW
SymEnumSymbols.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.LPCWSTR,
                           ctypes.c_void_p, ctypes.c_void_p]
SymEnumSymbols.restype = wt.BOOL

host = wt.HANDLE(int(ctypes.addressof(ctypes.c_int())) or ctypes.windll.kernel32.GetCurrentProcess())

ok = SymInitialize(host, None, False)
print("SymInitialize:", ok)
if not ok:
    print("err", ctypes.get_last_error(), ctypes.FormatError(ctypes.get_last_error()))
    raise SystemExit

base = SymLoadModuleEx(host, None, PDB, None, 0x140000000, 0x8000000, 0, None)
print("SymLoadModuleEx base:", hex(base) if base else base, "err", ctypes.get_last_error())

class SymbolInfo(ctypes.Structure):
    _fields_ = [("SizeOfStruct", wt.DWORD), ("TypeIndex", wt.DWORD),
                ("Reserved", ctypes.c_uint64), ("Index", wt.DWORD),
                ("Size", wt.DWORD), ("ModBase", ctypes.c_uint64),
                ("Flags", wt.DWORD), ("Value", ctypes.c_uint64),
                ("Address", ctypes.c_uint64), ("Register", wt.WORD),
                ("Scope", wt.WORD), ("Pdb", wt.DWORD),
                ("Tag", wt.DWORD), ("NameLen", wt.DWORD),
                ("MaxNameLen", wt.DWORD), ("Name", ctypes.c_wchar * 1)]

matches = []
keep = ("WeaponPack", "CreateWeaponBody", "InitWeaponPack", "InitalizeWeapon", "GetWeaponPack")
def enum_proc(si_ptr, user):
    si = ctypes.cast(si_ptr, ctypes.POINTER(SymbolInfo)).contents
    nm = ctypes.wstring_at(ctypes.byref(si, SymbolInfo.Name.offset), si.NameLen)
    if any(k in nm for k in keep):
        matches.append((hex(si.Address), nm, si.Size))
    return True

CALLBACK = ctypes.WINFUNCTYPE(wt.BOOL, ctypes.POINTER(SymbolInfo), wt.DWORD)
cb = CALLBACK(enum_proc)
r = SymEnumSymbols(host, base, None, cb, None)
print("SymEnumSymbols:", r, "matches:", len(matches))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"matches": matches}, f, ensure_ascii=False, indent=1)
SymCleanup(host)

for m in matches[:40]:
    print(m)