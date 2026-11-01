"""Hex + annotation dump of one camera body: resolve u32 words that are known class hashes or block ids."""
import os, struct, sys, zlib
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = cr.bootstrap_blocks(os.path.join(GAME, "DataPC.forge"),
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
byid = {b["id"]: b for b in blocks}
name = sys.argv[1]
lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x200
b = next(x for x in blocks if x["name"] == name)
body = cr.body_of(b)
print("%s id=%08x type=%s body=%d" % (name, b["id"], names(b["type_hash"]), len(body)))
for row in range(lo, min(hi, len(body)), 16):
    chunk = body[row:row + 16]
    print("+%04x  %s" % (row, " ".join("%02x" % c for c in chunk)))
print("--- annotations (any alignment) ---")
for p in range(lo, min(hi, len(body)) - 3):
    v = struct.unpack_from("<I", body, p)[0]
    n = names(v)
    if n != "%08x" % v:
        print("  +%04x  class/name %08x = %s" % (p, v, n))
    elif v in byid and v != 0:
        t = byid[v]
        print("  +%04x  ref %08x -> %s %r" % (p, v, names(t["type_hash"]), t["name"]))
