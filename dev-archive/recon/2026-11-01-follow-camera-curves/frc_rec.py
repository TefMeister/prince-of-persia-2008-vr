"""Dump each sub-object of a camera body as plausible floats: split at class tags, print f32 at every
offset whose value looks like a real number. args: <camera name> [class filter regex]"""
import os, re, struct, sys
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
GAME = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = cr.bootstrap_blocks(os.path.join(GAME, "DataPC.forge"),
                                    os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
cam = sys.argv[1]
flt = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
b = next(x for x in blocks if x["name"] == cam)
body = cr.body_of(b)
tags = []
for p in range(4, len(body) - 3):
    v = struct.unpack_from("<I", body, p)[0]
    n = names(v)
    if n != "%08x" % v:
        tags.append((p, n))
for i, (p, n) in enumerate(tags):
    end = tags[i + 1][0] - 4 if i + 1 < len(tags) else len(body)
    if flt and not flt.search(n):
        continue
    seg = body[p + 4:end]
    out = []
    k = 0
    while k + 4 <= len(seg):
        f = struct.unpack_from("<f", seg, k)[0]
        u = struct.unpack_from("<I", seg, k)[0]
        if f != 0 and 1e-3 < abs(f) < 1e4:
            out.append("@%d=%.4g" % (k, f)); k += 4
        else:
            k += 1
    print("+%04x %-30s len=%3d  %s" % (p, n, len(seg), " ".join(out)))
