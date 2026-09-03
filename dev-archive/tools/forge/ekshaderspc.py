#!/usr/bin/env python3
"""ekshaderspc.py - decode Prince of Persia (2008)'s shader pack,
`ekshaderspccompress.bin`.

WHY THIS EXISTS
---------------
The dossier recorded, on 2026-09-01, that this file was "LZ-compressed" and that
the CTAB-off-disk method "does not work here": `CTAB` appears 830 times in the
compressed bytes and not one of them parses, with constant names visibly shredded
by LZ tokens (`ViewPro*j`, `Vi@ewProj`). That was a correct measurement and the
wrong conclusion. The file is not opaque - it is the SAME LZO2A container the
`.forge` archives use, with a slightly different block header, and once decoded
it yields 17,464 `CTAB` blocks that parse perfectly.

CONTAINER FORMAT (established 2026-09-03, no launch)
----------------------------------------------------
    u8[5]   preamble          f5 9f 37 a8 02   (unidentified; skipped)
    u8[8]   magic             33 AA FB 57 99 FA 04 10   - the SAME magic as .forge
    u16     version           1
    u8      compression type  2 = LZO2A
    u16     max block size    0x8000
    u16     ?                 0x0000   (.forge has 0x8000 here)
    then, repeated to EOF, one per block:
    u8      flag              1 on all 1,361 blocks
    u32     compressed size
    u32     uncompressed size
    u32     checksum          (same unidentified u32 as .forge - see FORMAT.md)
    u8[]    data

The difference from `.forge` is that there is **no block table**: sizes are
inline, per block, and each block header carries a leading flag byte. Everything
else - LZO2A, 32 KiB blocks, the trailing u32 checksum - is shared.

VERIFIED 2026-09-03: 1,361 blocks, **zero decompression failures**, the file is
consumed exactly (0 bytes left over), 9,784,709 -> 44,578,719 bytes, and the
result contains 17,464 `CTAB` and 0 `DXBC` (D3D9, as the dossier already said).

    python ekshaderspc.py <ekshaderspccompress.bin> [-o out.bin]
    python ekshaderspc.py <ekshaderspccompress.bin> --info

⚠️ The decoded output is GAME CONTENT. Do not commit it. It regenerates in one
command; only the extracted constant names and registers - interface metadata -
belong in the repo.
"""
import argparse
import importlib.util
import os
import struct
import sys

MAGIC = bytes.fromhex("33AAFB5799FA0410")


def _load_forge():
    """Reuse forge.py's verified LZO2A decoder rather than duplicating it."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "forge.py")
    spec = importlib.util.spec_from_file_location("forge", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iter_blocks(data):
    """Yield (flag, compressed_size, uncompressed_size, checksum, bytes) per block.

    Raises ValueError with the byte offset if the chain does not resolve - a
    silent partial decode is far worse than a loud failure here, because the
    output would look like a shorter but valid shader database.
    """
    off = data.find(MAGIC)
    if off < 0:
        raise ValueError("chunk magic not found - not an ekshaderspc container")
    p = data[off:]
    n = len(p)
    ver, ctype = struct.unpack_from("<HB", p, 8)
    if ver != 1 or ctype != 2:
        raise ValueError("unsupported version/type %d/%d" % (ver, ctype))

    q = 15
    while q + 13 <= n:
        flag = p[q]
        c, u, csum = struct.unpack_from("<III", p, q + 1)
        if c == 0 or u == 0 or c > 0x20000 or u > 0x20000:
            raise ValueError("implausible block header at +%d (flag=%d c=%d u=%d)"
                             % (q, flag, c, u))
        blob = p[q + 13:q + 13 + c]
        if len(blob) != c:
            raise ValueError("truncated block at +%d (want %d bytes, have %d)"
                             % (q, c, len(blob)))
        yield flag, c, u, csum, blob
        q += 13 + c
    if q != n:
        raise ValueError("block chain ends at +%d but the payload is %d bytes" % (q, n))


def decode(data):
    forge = _load_forge()
    out = bytearray()
    nblk = raw = 0
    for _flag, c, u, _csum, blob in iter_blocks(data):
        if c == u:
            out += blob
            raw += 1
        else:
            out += forge.decompress_block(blob, u)
        nblk += 1
    return bytes(out), nblk, raw


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("-o", "--out", help="write the decoded stream here")
    ap.add_argument("--info", action="store_true",
                    help="report the block chain without decompressing")
    args = ap.parse_args(argv)

    data = open(args.file, "rb").read()
    if args.info:
        n = tc = tu = 0
        flags = {}
        for flag, c, u, _csum, _b in iter_blocks(data):
            n += 1; tc += c; tu += u
            flags[flag] = flags.get(flag, 0) + 1
        print("%s: %d bytes" % (args.file, len(data)))
        print("blocks         : %d" % n)
        print("flag bytes     : %s" % flags)
        print("compressed     : %d" % tc)
        print("uncompressed   : %d  (%.2fx)" % (tu, tu / float(tc) if tc else 0))
        return 0

    out, nblk, raw = decode(data)
    print("blocks=%d (raw=%d), decoded %d -> %d bytes" % (nblk, raw, len(data), len(out)))
    print("CTAB=%d  DXBC=%d" % (out.count(b"CTAB"), out.count(b"DXBC")))
    if args.out:
        open(args.out, "wb").write(out)
        print("wrote %s" % args.out)
    else:
        print("(no -o given; nothing written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
