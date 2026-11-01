"""Who references each PopFreeRoamingCamera id (any datablock, any alignment), and which rules hold it."""
import collections, os, struct, sys, zlib
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = cr.bootstrap_blocks(os.path.join(GAME, "DataPC.forge"),
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
FRC = zlib.crc32(b"PopFreeRoamingCamera") & 0xFFFFFFFF
frc = {b["id"]: b for b in blocks if b["type_hash"] == FRC}
refs = collections.defaultdict(list)
for b in blocks:
    raw = b["raw"]
    for p in range(0, len(raw) - 3):
        v = struct.unpack_from("<I", raw, p)[0]
        if v in frc and v != b["id"]:
            refs[v].append("%s %r" % (names(b["type_hash"]), b["name"]))
for i, b in frc.items():
    held = [r for r in refs[i]]
    print("%08x %-34r refs=%d  %s" % (i, b["name"], len(held), " | ".join(held[:4])))
