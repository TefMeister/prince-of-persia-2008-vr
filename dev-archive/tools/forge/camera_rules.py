#!/usr/bin/env python
"""Decode Scimitar `CameraRule` datablocks: which camera object each rule holds.

Why this exists. A `CameraRule` body is a flat sequence of tagged sub-records,
`{u32 objectId; u32 classHash; ...}`, where the class hash is CRC32 of the engine
class name (FORMAT.md section 6). The record that decides BEHAVIOUR is
`CameraHolder`: its first tail word is the datablock id of the camera object the
rule installs. That single reference is what makes one rule a free flycam and
another a third-person follow camera -- the difference is the CLASS of the object
held, not a flag inside the rule.

  python camera_rules.py rules  <archive.forge> [--exe <launcher.exe>] [--name RE]
  python camera_rules.py census <archive.forge> [--exe <launcher.exe>]
  python camera_rules.py subs   <archive.forge> [--exe <launcher.exe>]

`rules` dumps each matching rule's sub-records with references resolved; `census`
counts which camera class every rule holds; `subs` counts the nested sub-objects
inside each camera class (the `<u16 seq><0x9009><u32 classHash>` records), which
is what shows that only PopMarketingCamera reads the pad itself.

Read-only: it never writes to the game folder. It prints names, ids and counts,
which are interface metadata -- never archive contents.
"""
import argparse
import collections
import os
import re
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forge

CAMERA_RULE = 0x6A69B9C3
CAMERA_HOLDER = 0x3CEDBC28
STATE_DESC = 0x5E4FAACF
CGST_ANY = 309

# Sub-record classes seen inside a CameraRule body, keyed by CRC32 of the name.
RULE_SUBS = {}
for _n in ("CameraRule", "PopStateRuleCondition", "PopCharacterGraphStateDescription",
           "CameraExecution", "CameraHolder", "CameraTransitionSpecification",
           "BooleanRuleCondition", "MarketingCameraCondition"):
    RULE_SUBS[zlib.crc32(_n.encode()) & 0xFFFFFFFF] = _n


def body_of(b):
    """The datablock body, past typeHash / bodySize / nameLen / name / NUL."""
    nlen = struct.unpack_from("<I", b["raw"], 8)[0]
    return b["raw"][12 + nlen + 1:]


def bootstrap_blocks(path, exe):
    names = forge.TypeNames(exe)
    a = forge.Forge(path)
    for e in a.entries:
        if "Game Bootstrap" not in (e.name or ""):
            continue
        dec = forge.decompress_payload(a.read(e))
        return names, forge.split_datablocks(dec)
    raise SystemExit("no 'Game Bootstrap' datafile in %s" % path)


def rule_records(body):
    """Every recognised sub-record in a CameraRule body.

    Walked byte by byte rather than by stride: the records are not 4-aligned,
    because single trailing bytes between them shift the alignment.
    """
    out, p, n = [], 0, len(body)
    while p + 8 <= n:
        oid, ch = struct.unpack_from("<II", body, p)
        if ch in RULE_SUBS:
            out.append((p, oid, RULE_SUBS[ch]))
            p += 8
        else:
            p += 1
    return out


def held_camera(body):
    """The datablock id the rule's CameraHolder installs, or None."""
    for p in range(0, len(body) - 11):
        if struct.unpack_from("<I", body, p + 4)[0] == CAMERA_HOLDER:
            return struct.unpack_from("<I", body, p + 8)[0]
    return None


def cmd_rules(args):
    names, blocks = bootstrap_blocks(args.archive, args.exe)
    byid = {b["id"]: b for b in blocks}

    def ref(i):
        t = byid.get(i)
        if t is None:
            return "%08x" % i
        return "%08x (%s %r)" % (i, names(t["type_hash"]), t["name"])

    pat = re.compile(args.name, re.I) if args.name else None
    for b in blocks:
        if b["type_hash"] != CAMERA_RULE:
            continue
        if pat and not pat.search(b["name"] or ""):
            continue
        body = body_of(b)
        print("### %-24s id=%08x  block=%d  body=%d bytes"
              % (b["name"] or "(unnamed)", b["id"], b["index"], len(body)))
        recs = rule_records(body)
        for i, (off, oid, cls) in enumerate(recs):
            end = recs[i + 1][0] if i + 1 < len(recs) else len(body)
            tail = body[off + 8:end]
            print("  +%03x  %-34s obj=%08x  tail[%d]" % (off, cls, oid, len(tail)))
            if cls == "PopCharacterGraphStateDescription" and len(tail) >= 16:
                if struct.unpack_from("<I", tail, 0)[0] == 3:
                    print("          states = %s   (%d = CGST_Any, the don-t-care sentinel)"
                          % (struct.unpack_from("<3I", tail, 4), CGST_ANY))
            for k in range(0, max(0, len(tail) - 3)):
                v = struct.unpack_from("<I", tail, k)[0]
                if v in byid and v != b["id"]:
                    print("          tail+%-2d -> %s" % (k, ref(v)))
        print()


def cmd_census(args):
    names, blocks = bootstrap_blocks(args.archive, args.exe)
    byid = {b["id"]: b for b in blocks}
    held = collections.Counter()
    examples = collections.defaultdict(list)
    missing = []
    total = 0
    for b in blocks:
        if b["type_hash"] != CAMERA_RULE:
            continue
        total += 1
        tgt = held_camera(body_of(b))
        if tgt is None:
            missing.append(b["name"] or "(unnamed)")
            continue
        t = byid.get(tgt)
        cls = names(t["type_hash"]) if t else "UNRESOLVED"
        held[cls] += 1
        if len(examples[cls]) < 4:
            nm = (t["name"] if t else "%08x" % tgt) or "(unnamed)"
            examples[cls].append("%s -> %s" % (b["name"] or "(unnamed)", nm))
    print("CameraRule blocks: %d ; with a CameraHolder: %d ; without: %d"
          % (total, sum(held.values()), len(missing)))
    print()
    print("%-32s %6s  examples" % ("camera class the rule holds", "count"))
    for cls, n in held.most_common():
        print("%-32s %6d  %s" % (cls, n, " | ".join(examples[cls])))
    if missing:
        print()
        print("no CameraHolder: %s" % ", ".join(missing))


def cmd_subs(args):
    """Nested sub-objects per camera class.

    Records look like `<u16 seq><0x9009><u32 classHash>`; the hash resolves
    against the same exe string dictionary as a datablock typeHash.
    """
    names, blocks = bootstrap_blocks(args.archive, args.exe)
    pat = re.compile(rb"(..)\x09\x90(....)", re.S)
    per = collections.defaultdict(collections.Counter)
    nblk = collections.Counter()
    for b in blocks:
        t = names(b["type_hash"])
        if "Camera" not in t or t in ("CameraRule", "CameraGraph", "CameraTransitionManager"):
            continue
        nblk[t] += 1
        for m in pat.finditer(body_of(b)):
            per[t][names(struct.unpack("<I", m.group(2))[0])] += 1
    for t in sorted(nblk, key=lambda x: -nblk[x]):
        print("%-32s %4d block(s)" % (t, nblk[t]))
        for s, n in per[t].most_common():
            print("      %-40s %5d" % (s, n))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name, fn, with_name in (("rules", cmd_rules, True),
                                ("census", cmd_census, False),
                                ("subs", cmd_subs, False)):
        p = sub.add_parser(name)
        p.add_argument("archive")
        p.add_argument("--exe", help="the launcher exe, for CRC32 name resolution")
        if with_name:
            p.add_argument("--name", help="regex over the rule name")
        p.set_defaults(func=fn)
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
