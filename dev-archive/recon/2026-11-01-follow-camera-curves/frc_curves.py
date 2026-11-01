"""Per PopFreeRoamingCamera: the PolarCurveModifier's trajectories, each point as (x,y,z) at +5 and the copy at +117."""
import os, struct, sys, zlib
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
arch = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GAME, "DataPC.forge")
names, blocks = cr.bootstrap_blocks(arch,
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
H = lambda s: zlib.crc32(s.encode()) & 0xFFFFFFFF
FRC, PCM, TI, TP, FCM = map(H, ("PopFreeRoamingCamera", "PolarCurveModifier", "TrajectoryImpl",
                               "TrajectoryPoint", "FreeRoamingCollisionModifier"))


def tags(body, want):
    return [p for p in range(4, len(body) - 3) if struct.unpack_from("<I", body, p)[0] in want]


def curves(body):
    """Return (pcm_offset, [ [ (tag_off, xyz, xyz_copy), ... ] per trajectory ])."""
    s = tags(body, {PCM})
    if not s:
        return None, []
    start = s[0]
    stop = (tags(body, {FCM}) or [len(body)])[0]
    trajs = []
    for p in tags(body, {TI, TP}):
        if not (start < p < stop):
            continue
        cls = struct.unpack_from("<I", body, p)[0]
        if cls == TI:
            trajs.append([])
        else:
            a = struct.unpack_from("<3f", body, p + 4 + 5)
            c = struct.unpack_from("<3f", body, p + 4 + 117)
            trajs[-1].append((p, a, c))
    return start, trajs


if __name__ == "__main__":
    for b in blocks:
        if b["type_hash"] != FRC:
            continue
        start, tr = curves(cr.body_of(b))
        txt = " || ".join(" ".join("(%.2f,%.2f,%.2f)" % pt[1] for pt in t) for t in tr)
        print("%-32s %s" % ((b["name"] or "%08x" % b["id"])[:32], txt))
