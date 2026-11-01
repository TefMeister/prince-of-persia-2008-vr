"""Diff same-size PopFreeRoamingCamera bodies: which 4-byte words differ, shown as floats."""
import os, struct, sys, zlib
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = cr.bootstrap_blocks(os.path.join(GAME, "DataPC.forge"),
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
FRC = zlib.crc32(b"PopFreeRoamingCamera") & 0xFFFFFFFF
size = int(sys.argv[1])
grp = [b for b in blocks if b["type_hash"] == FRC and len(cr.body_of(b)) == size]
bodies = [cr.body_of(b) for b in grp]
print("blocks:", [b["name"] for b in grp])
diffbytes = [i for i in range(size) if len({x[i] for x in bodies}) > 1]
print("differing byte positions:", len(diffbytes))
# group into runs
runs, s = [], None
for i in diffbytes:
    if s is None or i > prev + 1:
        if s is not None: runs.append((s, prev))
        s = i
    prev = i
if s is not None: runs.append((s, prev))
for a, z in runs:
    # align to a 4-byte window ending at z; try offsets a-3..a and show float of the word covering it
    print("run +%04x..+%04x" % (a, z))
    for st in range(max(0, z - 3), a + 1):
        vals = []
        for x in bodies:
            v = struct.unpack_from("<f", x, st)[0]
            vals.append(v)
        if all(abs(v) < 1e5 and (v == 0 or abs(v) > 1e-4) for v in vals):
            print("   as f32 @+%04x: %s" % (st, " ".join("%.3f" % v for v in vals)))
