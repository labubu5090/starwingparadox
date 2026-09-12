import idautils, idc, traceback
out = []
def A(fmt, *a):
    out.append(fmt % a if a else fmt)
try:
    it = None
    for s in idautils.Strings():
        it = s
        break
    if it is None:
        A("No strings!")
    else:
        A("StringItem type: %s", type(it))
        A("dir: %s", [x for x in dir(it) if not x.startswith('__')])
        A("ea attr: 0x%X", it.ea)
        A("get_strlit_contents: %r", idc.get_strlit_contents(it.ea))
except Exception:
    A("EXCEPTION: %s", traceback.format_exc())
with open(r"C:\Users\KAHO\AppData\Local\Temp\opencode\ida_test.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(out))