"""Survey the PopFreeRoamingCamera datablocks: names, sizes, sub-object layout."""
import collections, os, re, struct, sys, zlib
TOOLS = r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge"
sys.path.insert(0, TOOLS)
import camera_rules as cr

GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = cr.bootstrap_blocks(os.path.join(GAME, "DataPC.forge"),
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
FRC = zlib.crc32(b"PopFreeRoamingCamera") & 0xFFFFFFFF
frc = [b for b in blocks if b["type_hash"] == FRC]
print("PopFreeRoamingCamera blocks:", len(frc))
sizes = collections.Counter(len(cr.body_of(b)) for b in frc)
print("body sizes:", sizes.most_common())
pat = re.compile(rb"(..)\x09\x90(....)", re.S)
mode = sys.argv[1] if len(sys.argv) > 1 else "list"
for b in frc:
    body = cr.body_of(b)
    subs = [(m.start(), struct.unpack("<H", m.group(1))[0], names(struct.unpack("<I", m.group(2))[0]))
            for m in pat.finditer(body)]
    if mode == "list":
        print("%08x %-36r body=%5d subs=%d" % (b["id"], b["name"], len(body), len(subs)))
    elif mode == "layout" and b["name"] == (sys.argv[2] if len(sys.argv) > 2 else "Parent Ground Cam"):
        for s in subs:
            print("  +%04x seq=%5d %s" % s)
