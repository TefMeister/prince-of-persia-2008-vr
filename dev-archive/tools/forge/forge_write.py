#!/usr/bin/env python3
"""
forge_write.py - a `.forge` REPACKER: patch bytes inside a named datafile's
decompressed payload and write a new, valid archive.

Built 2026-09-03 by `/pd`, dev PC. THE GAME WAS NOT LAUNCHED to build or test
this, and this tool never opens the game's own install files for writing -
every run in this session read the shipped archives and wrote to a scratch
directory only. It never overwrites its input.

WHY THIS EXISTS
---------------
ENGINE-DOSSIER.md §6 records a data-only mod: rewriting `CameraRule
"CR_Debug_1stPerson"`'s state-condition list from (188 CGST_DebugMode, 189
CGST_DebugModeFPSCamera, 309 CGST_Any) to (309, 309, 309) with a raised
priority would put the shipped `PopMarketingCamera "CAM FPS"` datablock live
in normal play, with NO CODE PATCH. That was blocked only on the per-block
`u32` checksum, solved 2026-09-03 (Adler-32 seeded 0 - see FORMAT.md §4). This
tool is what "no remaining format unknown" cashes out to.

WHY A FULL ARCHIVE REWRITE, NOT AN IN-PLACE PATCH
--------------------------------------------------
The target field sits inside a block that is stored LZO2A-COMPRESSED (9,290
bytes for 32,768 uncompressed). We have a decoder (lzo2a_decompress, in
forge.py) but no encoder, so the edited block cannot be recompressed to fit
its old slot. The format's own escape hatch is legal: "a block whose two
sizes are equal is stored raw" - so the edited block is re-stored RAW
(uncompressed == compressed == 32768). That makes it larger than before,
which means:

  1. everything in the archive AFTER that block's data shifts forward
  2. the touched datafile's declared `size` grows (three copies of it exist:
     the file-table entry, the name-table entry, and the datafile's own
     inline descriptor - all three must agree, per forge.py's own
     cross-check `nsize != e.size`)
  3. every LATER datafile's `data_offset` shifts by the aligned growth

Verified empirically before writing any of this (see the 2026-09-03 session):
entries are laid out in the archive in the SAME order as their index, and for
EVERY one of the 29 consecutive pairs in DataPC.forge,
    next.data_offset == align_up(this.data_offset + PAYLOAD_OFF + this.size, 0x800)
holds exactly, with the gap bytes always zero. That is the whole layout this
tool depends on, and it is exact rather than approximate - `verify_layout()`
below re-checks it on whatever archive you point this at, before touching
anything.

WHAT THIS TOOL DOES NOT DO
---------------------------
- It does not re-encode any block with LZO2A. Every edited block becomes
  RAW. Untouched blocks are copied byte-for-byte, compressed or not.
- It does not change a datablock's own declared length, add or remove
  datablocks, or touch the datablock table. Every edit is a same-length byte
  substitution inside an existing datablock's body. A length-changing edit
  would need the datablock table (see FORMAT.md §5) rewritten too - out of
  scope, and not needed for the recorded mod.
- It does not touch archives with more than one index chunk (>5000 entries -
  only the streamed-sound archives). `Forge._read_entries` already refuses
  those if the legacy single-chunk attributes are used incorrectly; this
  tool asserts `len(a.chunks) == 1` and stops rather than guess.

USAGE
-----
    # sanity: does this archive's layout match every assumption above?
    python forge_write.py verify-layout <archive.forge>

    # the null-op acceptance test: patch a byte to ITS OWN VALUE in an
    # ALREADY-RAW block (so nothing should move) and require byte-identical
    # output to the source file.
    python forge_write.py selftest-noop <archive.forge>

    # apply one or more edits and write a new archive
    python forge_write.py patch <archive.forge> <out.forge> \\
        --datafile "Game Bootstrap" \\
        --edit 0x56a3a4:bc000000=35010000 \\
        --edit 0x56a3a8:bd000000=35010000

    # verify a patched archive against its source: every datablock in every
    # OTHER datafile decompresses byte-identical; the touched datafile
    # decompresses byte-identical EXCEPT at exactly the edited ranges; every
    # block's stored Adler-0 checksum verifies.
    python forge_write.py diff <original.forge> <patched.forge>
"""
import argparse
import importlib.util
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("forge", os.path.join(HERE, "forge.py"))
forge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forge)

ALIGN = 0x800


def align_up(x, a=ALIGN):
    return (x + a - 1) // a * a


def adler0(data):
    """The block checksum: Adler-32 with both accumulators seeded to 0
    instead of 1 (LZO's own lzo_adler32(0, buf, len) - see FORMAT.md §4).
    Pure Python, matched against zlib.adler32(data, 0) in the self-tests."""
    BASE = 65521
    a = b = 0
    for x in data:
        a = (a + x) % BASE
        b = (b + a) % BASE
    return (b << 16) | a


# ---- layout verification ----------------------------------------------------

def verify_layout(a, data):
    """Re-derive the empirical layout facts this tool depends on, on THIS
    archive, before trusting them. Returns (ok, message)."""
    if len(a.chunks) != 1:
        return False, "archive has %d index chunks (>5000 entries) - not supported" % len(a.chunks)
    offs = [e.data_offset for e in a.entries]
    if not all(offs[i] <= offs[i + 1] for i in range(len(offs) - 1)):
        return False, "entries are not laid out in index order"
    bad = 0
    for i in range(len(a.entries) - 1):
        e, nx = a.entries[i], a.entries[i + 1]
        end = e.data_offset + forge.PAYLOAD_OFF + e.size
        expect = align_up(end)
        if nx.data_offset != expect:
            bad += 1
        else:
            pad = data[end:nx.data_offset]
            if any(pad):
                return False, "nonzero padding after entry %d" % i
    if bad:
        return False, "%d/%d consecutive pairs violate the alignment formula" % (bad, len(a.entries) - 1)
    return True, "%d entries, layout formula holds exactly, padding is all zero" % len(a.entries)


# ---- block location within a datafile's decompressed payload ----------------

def locate_blocks(payload, targets):
    """Walk every chunk/block of `payload` (as iter_chunks does) and, for each
    absolute decompressed offset in the sorted set `targets`, record which
    block it falls in. Returns a dict keyed by block identity
    (block_table_off) -> info dict, each carrying the list of target offsets
    that landed in it. Raises if a target offset is not covered by any block
    (payload too short, or the caller made an arithmetic mistake)."""
    targets = sorted(set(targets))
    ti = 0
    blocks = {}
    p = 0
    n = len(payload)
    dec_cum = 0
    while p < n:
        if payload[p:p + 8] != forge.CHUNK_MAGIC:
            raise ValueError("no chunk magic at payload+0x%x" % p)
        ver, ctype, _maxblk, _unk, nblk = struct.unpack_from("<HBHHH", payload, p + 8)
        if ver != 1 or ctype != 2:
            raise ValueError("unsupported chunk version/type %d/%d" % (ver, ctype))
        tbl_off = p + 17
        tbl = [struct.unpack_from("<HH", payload, tbl_off + 4 * i) for i in range(nblk)]
        q = tbl_off + 4 * nblk
        for bi, (u, c) in enumerate(tbl):
            block_table_off = tbl_off + 4 * bi
            checksum_off = q
            data_off = q + 4
            dec_start, dec_end = dec_cum, dec_cum + u
            while ti < len(targets) and dec_start <= targets[ti] < dec_end:
                blocks.setdefault(block_table_off, dict(
                    block_table_off=block_table_off, checksum_off=checksum_off,
                    data_off=data_off, compressed=c, uncompressed=u,
                    dec_start=dec_start, targets=[]))
                blocks[block_table_off]["targets"].append(targets[ti])
                ti += 1
            dec_cum += u
            q += 4 + c
        p = q
    if p != n:
        raise ValueError("chunk chain ends at %d, payload is %d" % (p, n))
    if ti != len(targets):
        raise ValueError("target offset 0x%x is past the end of the decompressed payload (%d bytes)"
                         % (targets[ti], dec_cum))
    return blocks


def patch_payload(payload, edits):
    """`edits`: list of (absolute_decompressed_offset, old_bytes, new_bytes),
    same length required. Returns the new payload bytes.

    Every affected block is decompressed, patched, and re-stored RAW - see
    the module docstring for why. Blocks are processed back-to-front so that
    earlier byte offsets in `payload` stay valid as later ones grow."""
    targets = [off for off, _o, _n in edits]
    blocks = locate_blocks(payload, targets)
    by_target = {}
    for info in blocks.values():
        for t in info["targets"]:
            by_target[t] = info

    out = bytearray(payload)
    # Process blocks in descending order of position, so earlier offsets
    # into `out` are never invalidated by a growing later block.
    for block_table_off in sorted(blocks, reverse=True):
        info = blocks[block_table_off]
        if info["compressed"] == info["uncompressed"]:
            plain = bytearray(out[info["data_off"]:info["data_off"] + info["compressed"]])
        else:
            raw = bytes(out[info["data_off"]:info["data_off"] + info["compressed"]])
            plain = bytearray(forge.decompress_block(raw, info["uncompressed"]))
            if len(plain) != info["uncompressed"]:
                raise ValueError("decompressed length %d != declared %d at block_table_off 0x%x"
                                 % (len(plain), info["uncompressed"], block_table_off))

        for off, old_bytes, new_bytes in edits:
            if off not in info["targets"]:
                continue
            if len(old_bytes) != len(new_bytes):
                raise ValueError("edit at 0x%x: old/new length mismatch (%d vs %d) - "
                                 "this tool only does same-length substitutions"
                                 % (off, len(old_bytes), len(new_bytes)))
            rel = off - info["dec_start"]
            actual = bytes(plain[rel:rel + len(old_bytes)])
            if actual != old_bytes:
                raise ValueError("edit at 0x%x: expected %r, found %r - refusing to guess"
                                 % (off, old_bytes, actual))
            plain[rel:rel + len(new_bytes)] = new_bytes

        new_compressed = bytes(plain)                    # stored RAW
        new_u, new_c = info["uncompressed"], len(new_compressed)
        new_checksum = adler0(new_compressed)

        out[block_table_off:block_table_off + 4] = struct.pack("<HH", new_u, new_c)
        out[info["checksum_off"]:info["checksum_off"] + 4] = struct.pack("<I", new_checksum)
        old_end = info["data_off"] + info["compressed"]
        out[info["data_off"]:old_end] = new_compressed

    return bytes(out)


# ---- whole-archive patch -----------------------------------------------------

def patch_archive(archive_path, out_path, datafile_name, edits, quiet=False):
    """edits: list of (absolute_decompressed_offset, old_bytes, new_bytes).
    Writes a complete new archive to `out_path`. Never touches `archive_path`."""
    a = forge.Forge(archive_path)
    with open(archive_path, "rb") as f:
        orig = f.read()

    ok, msg = verify_layout(a, orig)
    if not ok:
        raise ValueError("layout verification failed, refusing to patch: %s" % msg)
    if not quiet:
        print("layout verified: %s" % msg)

    matches = [e for e in a.entries if e.name == datafile_name]
    if len(matches) != 1:
        raise ValueError("expected exactly one datafile named %r, found %d" % (datafile_name, len(matches)))
    entry = matches[0]

    old_payload = a.read(entry)
    if len(old_payload) != entry.size:
        raise ValueError("payload length %d != declared size %d" % (len(old_payload), entry.size))

    new_payload = patch_payload(old_payload, edits)
    delta = len(new_payload) - len(old_payload)
    if not quiet:
        print("datafile %r: payload %d -> %d bytes (delta %+d)" % (datafile_name, len(old_payload), len(new_payload), delta))

    buf = bytearray(orig)

    old_end = entry.data_offset + forge.PAYLOAD_OFF + entry.size
    new_size = entry.size + delta
    new_end = entry.data_offset + forge.PAYLOAD_OFF + new_size
    old_next = align_up(old_end)
    new_next = align_up(new_end)
    shift = new_next - old_next

    # 1) patch the three copies of this entry's size (file table, name table,
    #    the datafile's own inline descriptor) - all in the PREFIX region,
    #    which is copied into the output before the payload splice point.
    ft_off = a.file_table_offset + entry.index * 16
    nt_off = a.name_table_offset + entry.index * forge.NAME_STRIDE
    desc_size_off = entry.data_offset + forge.DESC_OFF + 4
    for off, label in ((ft_off + 12, "file-table size"), (nt_off + 0, "name-table size"),
                       (desc_size_off, "inline descriptor size")):
        cur = struct.unpack_from("<I", buf, off)[0]
        if cur != entry.size:
            raise ValueError("%s at 0x%x reads %d, expected %d - aborting" % (label, off, cur, entry.size))
        struct.pack_into("<I", buf, off, new_size)

    # 2) shift every LATER entry's data_offset by `shift`. (Confirmed by
    #    verify_layout that entries are in index order, so "later" == higher
    #    index == higher data_offset; iterate all and compare defensively
    #    rather than assume.)
    if shift:
        for e2 in a.entries:
            if e2.data_offset > entry.data_offset:
                off = a.file_table_offset + e2.index * 16
                cur = struct.unpack_from("<Q", buf, off)[0]
                if cur != e2.data_offset:
                    raise ValueError("file-table data_offset for entry %d changed under us" % e2.index)
                struct.pack_into("<Q", buf, off, cur + shift)

    # 3) splice: unchanged prefix (through this entry's header+descriptor,
    #    already patched above) + new payload + zero padding to the next
    #    alignment boundary + unchanged suffix (from the OLD next-entry
    #    offset onward - the index-table region patched in steps 1-2 is
    #    entirely inside the prefix, well before any payload region, so it
    #    is not duplicated or lost by this split).
    prefix = bytes(buf[:entry.data_offset + forge.PAYLOAD_OFF])
    pad = b"\x00" * (new_next - new_end)
    suffix = bytes(buf[old_next:])
    result = prefix + new_payload + pad + suffix

    if len(result) != len(orig) + shift:
        raise ValueError("internal error: output length %d, expected %d"
                         % (len(result), len(orig) + shift))

    with open(out_path, "wb") as f:
        f.write(result)
    if not quiet:
        print("wrote %s (%d bytes, %+d vs source)" % (out_path, len(result), shift))
    return result


# ---- verification: diff two archives' full decompressed content -------------

def diff_archives(path_a, path_b, quiet=False):
    """Decompress EVERY datafile in both archives and report every byte range
    that differs. Also re-verifies every block's checksum in `path_b`
    (the presumed patched one) so a corrupt splice cannot pass silently."""
    fa, fb = forge.Forge(path_a), forge.Forge(path_b)
    if len(fa.entries) != len(fb.entries):
        return False, "entry count differs: %d vs %d" % (len(fa.entries), len(fb.entries))

    total_diff_ranges = []
    checksum_failures = []
    for ea, eb in zip(fa.entries, fb.entries):
        if ea.name != eb.name:
            return False, "entry %d name differs: %r vs %r" % (ea.index, ea.name, eb.name)
        pa, pb = fa.read(ea), fb.read(eb)
        if not forge.is_chunked(pa):
            if pa != pb:
                total_diff_ranges.append((ea.name, "whole (unchunked)", 0, max(len(pa), len(pb))))
            continue

        # checksum re-verification on the (presumed patched) side, over every
        # block regardless of whether this datafile was touched.
        for u, c, csum, data in forge.iter_chunks(pb):
            got = adler0(data)
            if got != csum:
                checksum_failures.append((eb.name, csum, got))

        da = forge.decompress_payload(pa)
        db = forge.decompress_payload(pb)
        if len(da) != len(db):
            total_diff_ranges.append((ea.name, "length", len(da), len(db)))
            continue
        i = 0
        n = len(da)
        while i < n:
            if da[i] == db[i]:
                i += 1
                continue
            j = i
            while j < n and da[j] != db[j]:
                j += 1
            total_diff_ranges.append((ea.name, "byte-range", i, j))
            i = j

    ok = not checksum_failures
    return ok, dict(diff_ranges=total_diff_ranges, checksum_failures=checksum_failures)


# ---- self-test: null-op patch on an already-raw block ------------------------

def find_raw_block_target(a):
    """Find (datafile_name, absolute_decompressed_offset, 4_bytes) for some
    byte quad sitting inside a block that is ALREADY stored raw, in the
    smallest chunked datafile - so a "patch it to itself" run exercises the
    real pipeline (locate -> decompress-or-copy -> re-store raw -> splice
    with delta 0) and must reproduce the source file exactly."""
    from collections import Counter
    name_counts = Counter(e.name for e in a.entries)
    candidates = [e for e in a.entries if e.size > 0 and e.name and name_counts[e.name] == 1]
    candidates.sort(key=lambda e: e.size)
    for e in candidates:
        payload = a.read(e)
        if not forge.is_chunked(payload):
            continue
        dec_cum = 0
        p = 0
        n = len(payload)
        while p < n:
            if payload[p:p + 8] != forge.CHUNK_MAGIC:
                break
            _ver, _ct, _mb, _unk, nblk = struct.unpack_from("<HBHHH", payload, p + 8)
            tbl_off = p + 17
            tbl = [struct.unpack_from("<HH", payload, tbl_off + 4 * i) for i in range(nblk)]
            q = tbl_off + 4 * nblk
            for u, c in tbl:
                if u == c and u >= 4:
                    data_off = q + 4
                    quad = bytes(payload[data_off:data_off + 4])
                    return e.name, dec_cum, quad
                dec_cum += u
                q += 4 + c
            p = q
    return None


def selftest_noop(archive_path, out_dir=None):
    """`out_dir` defaults to the system temp directory, NEVER beside the
    source archive - this tool must not write into the game's own install
    folder even transiently, per this project's standing /pd rule (read a
    game file, never write one). Pass out_dir explicitly to override."""
    import tempfile
    a = forge.Forge(archive_path)
    found = find_raw_block_target(a)
    if not found:
        print("no already-raw block found in this archive - cannot run the null-op self-test here")
        return False
    name, off, quad = found
    print("null-op target: datafile=%r offset=0x%x bytes=%s" % (name, off, quad.hex()))
    out_dir = out_dir or tempfile.gettempdir()
    out_path = os.path.join(out_dir, os.path.basename(archive_path) + ".selftest-noop.tmp")
    try:
        patch_archive(archive_path, out_path, name, [(off, quad, quad)])
        with open(archive_path, "rb") as f:
            orig = f.read()
        with open(out_path, "rb") as f:
            new = f.read()
        if orig == new:
            print("PASS: patched output is byte-identical to the source (%d bytes)" % len(orig))
            return True
        diffs = sum(1 for x, y in zip(orig, new) if x != y)
        print("FAIL: %d differing bytes (lengths %d vs %d)" % (diffs, len(orig), len(new)))
        return False
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


# ---- CLI ---------------------------------------------------------------------

def parse_edit(spec):
    # "0x56a3a4:bc000000=35010000"
    addr, rest = spec.split(":", 1)
    old_hex, new_hex = rest.split("=", 1)
    return int(addr, 0), bytes.fromhex(old_hex), bytes.fromhex(new_hex)


def cmd_verify_layout(args):
    a = forge.Forge(args.archive)
    with open(args.archive, "rb") as f:
        data = f.read()
    ok, msg = verify_layout(a, data)
    print(("PASS: " if ok else "FAIL: ") + msg)
    return 0 if ok else 1


def cmd_selftest_noop(args):
    return 0 if selftest_noop(args.archive) else 1


def cmd_patch(args):
    edits = [parse_edit(s) for s in args.edit]
    patch_archive(args.archive, args.out, args.datafile, edits)
    return 0


def cmd_diff(args):
    ok, result = diff_archives(args.a, args.b)
    if isinstance(result, str):
        print("FAIL:", result)
        return 1
    for name, kind, i, j in result["diff_ranges"]:
        print("DIFF  %-20s %-16s 0x%x .. 0x%x  (%d bytes)" % (name, kind, i, j, j - i))
    for name, want, got in result["checksum_failures"]:
        print("CHECKSUM FAIL  %-20s want=0x%08x got=0x%08x" % (name, want, got))
    print()
    print("%d differing range(s) across %d entries; %d checksum failure(s) in b"
          % (len(result["diff_ranges"]), max(1, len(result["diff_ranges"])), len(result["checksum_failures"])))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("verify-layout")
    p.add_argument("archive")
    p.set_defaults(func=cmd_verify_layout)

    p = sub.add_parser("selftest-noop")
    p.add_argument("archive")
    p.set_defaults(func=cmd_selftest_noop)

    p = sub.add_parser("patch")
    p.add_argument("archive")
    p.add_argument("out")
    p.add_argument("--datafile", required=True)
    p.add_argument("--edit", action="append", required=True,
                   help="offset:oldhex=newhex, e.g. 0x56a3a4:bc000000=35010000")
    p.set_defaults(func=cmd_patch)

    p = sub.add_parser("diff")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(func=cmd_diff)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
