import sys
import zlib, re, struct, sys, json, subprocess
EXE = sys.argv[1]   # path to a Steamless-unpacked copy of PrinceOfPersia_Launcher.exe
d = open(EXE,"rb").read()
def crc32(s): return zlib.crc32(s.encode() if isinstance(s,str) else s) & 0xffffffff
DICT = {}
seen=set()
for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{2,90}", d):
    s = m.group()
    if s in seen: continue
    seen.add(s)
    DICT.setdefault(crc32(s), set()).add(s.decode("latin-1"))
print("dictionary: %d strings, %d distinct hashes" % (len(seen), len(DICT)), file=sys.stderr)
json.dump({("%08x"%k): sorted(v) for k,v in DICT.items()}, open("crc_dict.json","w"))

if len(sys.argv) > 2:
    for a in sys.argv[2:]:
        v = int(a,16)
        print("0x%08x -> %s" % (v, sorted(DICT.get(v, [])) or "UNRESOLVED"))
