import sys, os
sys.path.insert(0, r"D:/claude video game stuff/github-backups-pd/prince-of-persia-2008-vr/dev-archive/tools/forge")
import forge

GAME = r"D:/Program Files (x86)/Steam/steamapps/common/Prince of Persia"
OUT  = sys.argv[1]
ARCH = os.path.join(GAME, "DataPC.forge")

f = forge.Forge(ARCH)
ent = [e for e in f.entries if "Game Bootstrap" in e.name]
assert len(ent) == 1, ent
e = ent[0]
dec = forge.decompress_payload(f.read(e))
print("decompressed stream: %d bytes" % len(dec))
blocks = forge.split_datablocks(dec)
print("datablocks: %d" % len(blocks))
want = ("MagmaCommon_MGB", "MagmaInGame_MGB", "MagmaPregame_MGB", "MagmaFonts_MGB")
for b in blocks:
    if b["name"] in want:
        # body starts after 12 + nameLen + 1 (NUL)
        nlen = len(b["name"])
        hdr = 12 + nlen
        body = b["raw"][hdr:]
        p = os.path.join(OUT, b["name"] + ".bin")
        open(p, "wb").write(body)
        print("%-20s id=%08x size=%d body=%d hdr=%d -> %s"
              % (b["name"], b["id"], b["size"], b["body_size"], hdr, p))
        print("   first 64 bytes: %s" % body[:64].hex())
