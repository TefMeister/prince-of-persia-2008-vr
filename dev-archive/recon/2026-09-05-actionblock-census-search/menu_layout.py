import os, struct, sys, zlib
sys.path.insert(0, r"C:\Users\TD3KX\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import forge

GAME = r"C:\Steam\steamapps\common\Prince of Persia"
EXE = os.path.join(GAME, "PrinceOfPersia_Launcher.exe")
names = forge.TypeNames(EXE)
a = forge.Forge(os.path.join(GAME, "DataPC.forge"))
e = [x for x in a.entries if x.name == "Game Bootstrap"][0]
dec = forge.decompress_payload(a.read(e))
blocks = forge.split_datablocks(dec)
byid = {b["id"]: b for b in blocks}

print("%-5s %-9s %-34s %-9s %-9s %s" % ("blk", "id", "type", "field@+0x11", "resolves?", "screen"))
for b in blocks:
    tn = names(b["type_hash"])
    if "Menu" not in tn and "Interface" not in tn and "Hud" not in tn:
        continue
    raw = b["raw"]
    if b["size"] < 0x1d:
        continue
    own = struct.unpack_from("<I", raw, 0xd)[0]
    th2 = struct.unpack_from("<I", raw, 0x11)[0]
    f = struct.unpack_from("<I", raw, 0x15)[0]
    nl = struct.unpack_from("<I", raw, 0x19)[0]
    s = ""
    if 0 < nl < 64 and 0x1d + nl <= len(raw):
        s = raw[0x1d:0x1d + nl].decode("latin-1")
    res = names(f) if f in byid else ("=" + names(byid[f]["type_hash"]) if f in byid else "-")
    if f in byid:
        res = "%s(%s)" % (names(byid[f]["type_hash"]), byid[f]["name"])
    else:
        res = "-"
    print("%-5d %08x %-34s %08x  %-9s %r  own=%08x th2=%08x" % (
        b["index"], b["id"], tn, f, res, s, own, th2))
