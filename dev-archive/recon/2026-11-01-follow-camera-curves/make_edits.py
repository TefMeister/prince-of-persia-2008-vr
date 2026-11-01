"""Compute payload offsets for the close-up camera builds and print --edit arguments.

A: CR_Debug_1stPerson's CameraHolder (+ its transition's camera field) -> 99d3ca72 (Prince close-up cam).
B: A + the close-up cam's first PolarCurve trajectory, every point's height (+4 into the point vec) raised by RAISE.
"""
import os, struct, sys
sys.path.insert(0, r"D:\claude video game stuff\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import camera_rules as cr
import frc_curves as fc
G = r"D:\Program Files (x86)\Steam\steamapps\common\Prince of Persia"
names, blocks = fc.names, fc.blocks
RAISE = 3.0
CLOSE = 0x99d3ca72
OLD = 0x842a4105


def body_base(b):
    nlen = struct.unpack_from("<I", b["raw"], 8)[0]
    return b["offset"] + 12 + nlen + 1


rule = next(b for b in blocks if b["name"] == "CR_Debug_1stPerson")
rb = cr.body_of(rule)
hits = [p for p in range(len(rb) - 3) if struct.unpack_from("<I", rb, p)[0] == OLD]
editsA = []
for p in hits:
    off = body_base(rule) + p
    editsA.append("0x%x:%s=%s" % (off, struct.pack("<I", OLD).hex(), struct.pack("<I", CLOSE).hex()))
print("A holder fields at body+%s" % [hex(p) for p in hits])
cam = next(b for b in blocks if b["id"] == CLOSE)
cb = cr.body_of(cam)
start, tr = fc.curves(cb)
editsB = list(editsA)
for (p, a, c) in tr[0]:
    for rel, val in ((4 + 5 + 4, a[1]), (4 + 117 + 4, c[1])):
        off = body_base(cam) + p + rel
        old = struct.pack("<f", val)
        assert cb[p + rel:p + rel + 4] == old
        editsB.append("0x%x:%s=%s" % (off, old.hex(), struct.pack("<f", val + RAISE).hex()))
    print("B point at body+%#x: y %.4f -> %.4f (copy %.4f -> %.4f)" % (p, a[1], a[1] + RAISE, c[1], c[1] + RAISE))
open("edits_A.txt", "w").write("\n".join(editsA) + "\n")
open("edits_B.txt", "w").write("\n".join(editsB) + "\n")
print("A:", " ".join(editsA))
print("B:", " ".join(editsB))
