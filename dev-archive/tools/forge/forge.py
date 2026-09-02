#!/usr/bin/env python3
"""
forge.py - reader for Scimitar/Anvil `.forge` archives as shipped by
Prince of Persia (2008).

Written from scratch on 2026-09-02 by reading the shipped archives; no public
schema for this container generation was available (the best public write-up
documents the AnvilNext variant and stops at the resource boundary).

Nothing here launches or modifies the game. Read-only: the tool never writes
into the game folder, and the archives are opened 'rb'.

Container layout (derived, see FORMAT.md):

  header @0
    char[8]  "scimitar"
    u8       0
    u32      version            (26 on this game's archives)
    u64      tableOffset
    u32      ?                  (0x10)
    u32      ?                  (1)

  table @tableOffset
    +0x00 u32  totalFileCount
    +0x04 u32  ?                (1)
    +0x08 u64  0
    +0x10 i64  -1
    +0x18 u32  chunkCapacity    (5000)
    +0x1c u32  chunkCount
    +0x20 u64  firstChunkOffset (= tableOffset+0x28)

  chunk @chunkOffset - an index chunk holding up to chunkCapacity entries.
  Archives with more than 5000 datafiles carry several, chained through +0x10.
    +0x00 u32  count            (entries in this chunk)
    +0x04 u32  ?                (1)
    +0x08 u64  fileTableOffset  (= chunkOffset+0x30)
    +0x10 i64  nextChunkOffset  (-1 = last chunk)
    +0x18 u32  0
    +0x1c u32  chunkCapacity-1  (4999)
    +0x20 u64  nameTableOffset
    +0x28 u64  auxTableOffset   (purpose not established)
    +0x30 fileTable[count]      {u64 dataOffset; u32 timestamp; u32 size}

  Both sub-tables are pre-allocated at full capacity, so in chunk 0 the file
  table runs 0x46e..0x13cee (5000 x 16) and the name table starts there.

  nameTable @nameTableOffset - count records, stride 0xBC:
    +0x00 u32  size             (matches fileTable size)
    +0x04 u64  uid
    +0x1c i32  nextIndex        (-1 = end)
    +0x20 i32  prevIndex        (-1 = start)
    +0x28 u32  unixTime         (build date; NOT a hash - values repeat
                                 across different names and decode to Nov 2008)
    +0x2c char[] name, NUL-terminated

  datafile @dataOffset
    +0x000  char[8] "FILEDATA"
    +0x008  char[]  name, NUL-padded
    +0x187  descriptor:
              +0x00 u32 timestamp
              +0x04 u32 size
              +0x08 u64 uid
              +0x1c u32 ?
              +0x20 u32 ?
              +0x28 u32 unixTime   (build date, Nov 2008 on this game)
              +0x2c u32 0
              +0x30 u8  0
    +0x1B8  payload, `size` bytes   (= dataOffset + 0x187 + 0x31)

  payload - a chain of compressed chunks, each:
    char[8] 33 AA FB 57 99 FA 04 10   (compressed-chunk magic)
    u16     1                        (version)
    u8      compressionType          (2 everywhere seen = LZO2A, per the
                                      exe's own enum LZO1X_1/LZO1X_999/LZO2A/LZX)
    u16     0x8000  maxBlockSize
    u16     0x8000
    u16     blockCount
    {u16 uncompressedSize; u16 compressedSize}[blockCount]
    then per block: u32 checksum; u8 data[compressedSize]
    (a block whose two sizes are equal is stored raw)
"""
import argparse
import os
import re
import struct
import sys

MAGIC = b"scimitar"
FILEDATA = b"FILEDATA"

HDR_TABLE_OFF = 0x0D
NAME_STRIDE = 0xBC
DESC_OFF = 0x187            # datafile start -> descriptor
PAYLOAD_OFF = 0x187 + 0x31  # datafile start -> payload (descriptor is 0x31 bytes)


class Entry(object):
    __slots__ = ("index", "name", "unix_time", "uid", "data_offset", "size",
                 "timestamp", "next_index", "prev_index")

    def __repr__(self):
        return ("<%d %r off=0x%x size=%d hash=0x%08x>"
                % (self.index, self.name, self.data_offset, self.size,
                   self.unix_time))

    @property
    def payload_offset(self):
        return self.data_offset + PAYLOAD_OFF


class Forge(object):
    def __init__(self, path):
        self.path = path
        self.f = open(path, "rb")
        self._read_header()
        self._read_entries()

    # -- reading helpers -------------------------------------------------
    def _at(self, off, n):
        self.f.seek(off)
        b = self.f.read(n)
        if len(b) != n:
            raise ValueError("%s: short read at 0x%x" % (self.path, off))
        return b

    def _u32(self, off):
        return struct.unpack("<I", self._at(off, 4))[0]

    def _u64(self, off):
        return struct.unpack("<Q", self._at(off, 8))[0]

    # -- structure -------------------------------------------------------
    def _read_header(self):
        head = self._at(0, 0x20)
        if head[:8] != MAGIC:
            raise ValueError("%s: not a .forge archive (magic %r)"
                             % (self.path, head[:8]))
        self.version = struct.unpack_from("<I", head, 0x09)[0]
        self.table_offset = struct.unpack_from("<Q", head, HDR_TABLE_OFF)[0]

        t = self.table_offset
        self.file_count = self._u32(t + 0x00)
        self.chunk_capacity = self._u32(t + 0x18)
        self.chunk_count = self._u32(t + 0x1C)
        self.first_chunk_offset = self._u64(t + 0x20)
        if self.first_chunk_offset != t + 0x28:
            raise ValueError("%s: unexpected first-chunk offset 0x%x (expected 0x%x)"
                             % (self.path, self.first_chunk_offset, t + 0x28))

    def _read_entries(self):
        self.entries = []
        self.chunks = []
        c = self.first_chunk_offset
        guard = 0
        while c not in (0, 0xFFFFFFFFFFFFFFFF):
            guard += 1
            if guard > 4096:
                raise ValueError("%s: chunk chain does not terminate" % self.path)
            n = self._u32(c + 0x00)
            file_table = self._u64(c + 0x08)
            nxt = struct.unpack("<q", self._at(c + 0x10, 8))[0]
            name_table = self._u64(c + 0x20)
            aux_table = self._u64(c + 0x28)
            if file_table != c + 0x30:
                raise ValueError("%s: chunk 0x%x file table at 0x%x (expected 0x%x)"
                                 % (self.path, c, file_table, c + 0x30))
            if n > self.chunk_capacity:
                raise ValueError("%s: chunk 0x%x holds %d entries (capacity %d)"
                                 % (self.path, c, n, self.chunk_capacity))
            self.chunks.append((c, n, file_table, name_table, aux_table))
            ftab = self._at(file_table, n * 16)
            ntab = self._at(name_table, n * NAME_STRIDE)
            for i in range(n):
                e = Entry()
                e.index = len(self.entries)
                e.data_offset, e.timestamp, e.size = struct.unpack_from("<QII", ftab, i * 16)
                r = i * NAME_STRIDE
                nsize, uid = struct.unpack_from("<IQ", ntab, r)
                e.uid = uid
                e.next_index, e.prev_index = struct.unpack_from("<ii", ntab, r + 0x1C)
                e.unix_time = struct.unpack_from("<I", ntab, r + 0x28)[0]
                raw = ntab[r + 0x2C:r + NAME_STRIDE]
                e.name = raw.split(b"\0", 1)[0].decode("latin-1")
                if nsize != e.size:
                    raise ValueError("%s: entry %d size disagreement %d vs %d"
                                     % (self.path, e.index, nsize, e.size))
                self.entries.append(e)
            c = nxt if nxt >= 0 else 0
        if len(self.entries) != self.file_count:
            raise ValueError("%s: chunks yielded %d entries, header says %d"
                             % (self.path, len(self.entries), self.file_count))
        # legacy single-chunk convenience attributes
        self.file_table_offset = self.chunks[0][2]
        self.name_table_offset = self.chunks[0][3]
        self.aux_table_offset = self.chunks[0][4]

    # -- payload ---------------------------------------------------------
    def read(self, e):
        """Return the raw payload bytes of one datafile."""
        head = self._at(e.data_offset, 8)
        if head != FILEDATA:
            raise ValueError("%s: entry %d (%r) has magic %r at 0x%x"
                             % (self.path, e.index, e.name, head, e.data_offset))
        return self._at(e.payload_offset, e.size)

    def inline_name(self, e):
        """The datafile's own copy of its name (cross-check for the name table)."""
        raw = self._at(e.data_offset + 8, DESC_OFF - 8)
        return raw.split(b"\0", 1)[0].decode("latin-1")

    def inline_desc(self, e):
        d = self._at(e.data_offset + DESC_OFF, 0x30)
        ts, size = struct.unpack_from("<II", d, 0)
        uid = struct.unpack_from("<Q", d, 8)[0]
        utime = struct.unpack_from("<I", d, 0x28)[0]
        return ts, size, uid, utime


# -- compression ---------------------------------------------------------
CHUNK_MAGIC = bytes.fromhex("33aafb5799fa0410")


def lzo2a_decompress(src, out_len):
    """Pure-Python LZO2A decompressor.

    Transcribed from LZO's lzo2a_d.ch with the config2a.h build constants
    (SWD_N 8191 - so no M3 branch - M1_MIN_LEN 2, LZO_EOF_CODE). Bit buffer
    is LSB-first, refilled one byte at a time. Returns (bytes, consumed, how)
    where how is 'eof' when the stream ended on the EOF marker.
    """
    out = bytearray()
    ip = 0
    b = 0
    k = 0
    n = len(src)
    while ip < n:
        if k < 1:
            b |= src[ip] << k
            ip += 1
            k += 8
        if b & 1 == 0:                      # literal
            b >>= 1
            k -= 1
            out.append(src[ip])
            ip += 1
            continue
        b >>= 1
        k -= 1
        if k < 1:
            b |= src[ip] << k
            ip += 1
            k += 8
        if b & 1 == 0:                      # M1: len 2..5, offset 1..256
            b >>= 1
            k -= 1
            if k < 2:
                b |= src[ip] << k
                ip += 1
                k += 8
            t = 2 + (b & 3)
            b >>= 2
            k -= 2
            mp = len(out) - 1 - src[ip]
            ip += 1
            if mp < 0:
                raise ValueError("lookbehind underrun at ip=%d" % ip)
            for _ in range(t):
                out.append(out[mp])
                mp += 1
            continue
        b >>= 1
        k -= 1
        t = src[ip]                          # M2: 13-bit offset, len 3..9 or long
        mp = len(out) - ((t & 31) | (src[ip + 1] << 5))
        ip += 2
        t >>= 5
        if t == 0:
            t = 9
            while src[ip] == 0:
                t += 255
                ip += 1
            t += src[ip]
            ip += 1
        else:
            if mp == len(out):
                return bytes(out), ip, "eof"
            t += 2
        if mp < 0:
            raise ValueError("lookbehind underrun at ip=%d" % ip)
        for _ in range(t):
            out.append(out[mp])
            mp += 1
    return bytes(out), ip, "noeof"


def iter_chunks(payload):
    """Yield (uncompressedSize, compressedSize, checksum, data) for every
    block of every compressed chunk in a datafile payload, in order."""
    p = 0
    n = len(payload)
    while p < n:
        if payload[p:p + 8] != CHUNK_MAGIC:
            raise ValueError("no chunk magic at payload+0x%x" % p)
        ver, ctype, _maxblk, _unk, nblk = struct.unpack_from("<HBHHH", payload, p + 8)
        if ver != 1 or ctype != 2:
            raise ValueError("unsupported chunk version/type %d/%d at payload+0x%x"
                             % (ver, ctype, p))
        tbl = [struct.unpack_from("<HH", payload, p + 17 + 4 * i) for i in range(nblk)]
        q = p + 17 + 4 * nblk
        for (u, c) in tbl:
            csum = struct.unpack_from("<I", payload, q)[0]
            yield u, c, csum, payload[q + 4:q + 4 + c]
            q += 4 + c
        p = q
    if p != n:
        raise ValueError("chunk chain ends at %d, payload is %d" % (p, n))


_clib = None


def _native():
    """Load lzo2a.dll (built from lzo2a.c beside this file) if present."""
    global _clib
    if _clib is not None:
        return _clib or None
    import ctypes
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("lzo2a.dll", "liblzo2a.so", "liblzo2a.dylib"):
        p = os.path.join(here, name)
        if os.path.exists(p):
            lib = ctypes.CDLL(p)
            lib.lzo2a_decompress.restype = ctypes.c_long
            lib.lzo2a_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
                                             ctypes.c_char_p, ctypes.c_size_t,
                                             ctypes.POINTER(ctypes.c_size_t)]
            _clib = lib
            return lib
    _clib = False
    return None


def decompress_block(data, u):
    """Decompress one block to exactly `u` bytes, native if possible."""
    lib = _native()
    if lib is not None:
        import ctypes
        out = ctypes.create_string_buffer(u)
        used = ctypes.c_size_t(0)
        r = lib.lzo2a_decompress(data, len(data), out, u, ctypes.byref(used))
        if r != u or used.value != len(data):
            raise ValueError("block decode mismatch (native): rc %d used %d/%d"
                             % (r, used.value, len(data)))
        return out.raw
    blk, used, how = lzo2a_decompress(data, u)
    if len(blk) != u or used != len(data) or how != "eof":
        raise ValueError("block decode mismatch: out %d/%d used %d/%d %s"
                         % (len(blk), u, used, len(data), how))
    return blk


def is_chunked(payload):
    return payload[:8] == CHUNK_MAGIC


def decompress_payload(payload):
    """Return the concatenated decompressed blocks of a datafile payload.
    A payload that does not start with the chunk magic (the unnamed second
    datafile of every archive) is returned unchanged."""
    if not is_chunked(payload):
        return payload
    out = bytearray()
    for u, c, _csum, data in iter_chunks(payload):
        if u == c:
            out += data
        else:
            out += decompress_block(data, u)
    return bytes(out)


def split_datablocks(decompressed):
    """Split a decompressed datafile into its datablocks.

    The first datablock-table is `u16 count; {u32 id; u32 size}[count]`
    (its own bytes are the first 2+8*count of the stream), followed by the
    datablocks back to back. Each datablock begins
    `u32 typeHash; u32 bodySize; u32 nameLen; char name[nameLen]; u8 0`.
    Returns a list of dicts.
    """
    count = struct.unpack_from("<H", decompressed, 0)[0]
    table = [struct.unpack_from("<II", decompressed, 2 + 8 * i) for i in range(count)]
    p = 2 + 8 * count
    blocks = []
    for i, (bid, size) in enumerate(table):
        raw = decompressed[p:p + size]
        if len(raw) != size:
            raise ValueError("datablock %d runs past the stream" % i)
        rec = {"index": i, "id": bid, "size": size, "offset": p, "raw": raw,
               "type_hash": None, "name": None}
        if size >= 12:
            th, body, nlen = struct.unpack_from("<III", raw, 0)
            if 12 + nlen <= size:
                rec["type_hash"] = th
                rec["body_size"] = body
                rec["name"] = raw[12:12 + nlen].decode("latin-1", "replace")
        blocks.append(rec)
        p += size
    if p != len(decompressed):
        raise ValueError("datablocks end at %d, stream is %d" % (p, len(decompressed)))
    return blocks


# -- commands ------------------------------------------------------------
def cmd_info(args):
    for p in args.archive:
        a = Forge(p)
        total = sum(e.size for e in a.entries)
        print("%s: version=%d files=%d chunks=%d payloadBytes=%d "
              "tableOffset=0x%x nameTable=0x%x aux=0x%x"
              % (os.path.basename(p), a.version, a.file_count, len(a.chunks),
                 total, a.table_offset, a.name_table_offset, a.aux_table_offset))


def cmd_list(args):
    for p in args.archive:
        a = Forge(p)
        if len(args.archive) > 1:
            print("== %s" % os.path.basename(p))
        for e in a.entries:
            if args.match and not re.search(args.match, e.name, re.I):
                continue
            print("%6d  0x%010x  %10d  0x%08x  %016x  %s"
                  % (e.index, e.data_offset, e.size, e.unix_time, e.uid, e.name))


def cmd_verify(args):
    """Cross-check every derived field against the datafile's own copy."""
    bad = 0
    checked = 0
    for p in args.archive:
        a = Forge(p)
        size_on_disk = os.path.getsize(p)
        prev_end = 0
        for e in a.entries:
            checked += 1
            ts, size, uid, utime = a.inline_desc(e)
            iname = a.inline_name(e)
            problems = []
            if size != e.size:
                problems.append("size %d != %d" % (size, e.size))
            if uid != e.uid:
                problems.append("uid %x != %x" % (uid, e.uid))
            if utime != e.unix_time:
                problems.append("time %08x != %08x" % (utime, e.unix_time))
            if ts != e.timestamp:
                problems.append("ts %08x != %08x" % (ts, e.timestamp))
            if iname != e.name:
                problems.append("name %r != %r" % (iname, e.name))
            if a._at(e.data_offset, 8) != FILEDATA:
                problems.append("no FILEDATA magic")
            if e.data_offset < prev_end:
                problems.append("overlaps previous entry (ends 0x%x)" % prev_end)
            if e.payload_offset + e.size > size_on_disk:
                problems.append("payload runs past end of file")
            prev_end = e.payload_offset + e.size
            if problems:
                bad += 1
                print("%s [%d] %s: %s"
                      % (os.path.basename(p), e.index, e.name, "; ".join(problems)))
        # the doubly-linked list uses archive-global indices and must visit
        # every entry exactly once, forwards and backwards
        n = a.file_count
        for label, start_attr, step_attr in (("next", "prev_index", "next_index"),
                                             ("prev", "next_index", "prev_index")):
            seen = set()
            i = next((e.index for e in a.entries if getattr(e, start_attr) == -1), None)
            while i is not None and i != -1 and 0 <= i < n and i not in seen:
                seen.add(i)
                i = getattr(a.entries[i], step_attr)
            if len(seen) != n:
                bad += 1
                print("%s: %s-linked list covers %d/%d entries"
                      % (os.path.basename(p), label, len(seen), n))
    print("verify: %d entries checked, %d problem(s)" % (checked, bad))
    return 1 if bad else 0


def _safe(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name) or "unnamed"


def cmd_extract(args):
    os.makedirs(args.out, exist_ok=True)
    n = 0
    for p in args.archive:
        a = Forge(p)
        sub = os.path.join(args.out, os.path.splitext(os.path.basename(p))[0])
        os.makedirs(sub, exist_ok=True)
        for e in a.entries:
            if args.match and not re.search(args.match, e.name, re.I):
                continue
            data = a.read(e)
            if args.decompress:
                data = decompress_payload(data)
            fn = os.path.join(sub, "%05d_%s.bin" % (e.index, _safe(e.name)))
            with open(fn, "wb") as fh:
                fh.write(data)
            n += 1
    print("extracted %d datafile(s) to %s" % (n, args.out))


class TypeNames(object):
    """CRC32 -> identifier, built from every identifier-shaped string in the
    game executable (type hashes are CRC32 of the engine class name)."""

    def __init__(self, exe=None):
        self.table = {}
        if exe:
            import zlib
            data = open(exe, "rb").read()
            for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_:]{2,80}", data):
                s = m.group()
                self.table.setdefault(zlib.crc32(s) & 0xFFFFFFFF, s.decode("latin-1"))

    def __call__(self, h):
        if h is None:
            return "-"
        return self.table.get(h, "%08x" % h)


def _each_datafile(args):
    """Yield (archive, entry, decompressed, datablocks-or-None)."""
    for p in args.archive:
        a = Forge(p)
        for e in a.entries:
            if getattr(args, "match", None) and not re.search(args.match, e.name, re.I):
                continue
            payload = a.read(e)
            if not is_chunked(payload):
                yield a, e, payload, None
                continue
            try:
                dec = decompress_payload(payload)
            except ValueError as exc:
                print("  !! %s [%d] %s: %s" % (os.path.basename(p), e.index, e.name, exc))
                continue
            try:
                blocks = split_datablocks(dec)
            except (ValueError, struct.error) as exc:
                print("  !! %s [%d] %s: datablock split failed: %s"
                      % (os.path.basename(p), e.index, e.name, exc))
                blocks = None
            yield a, e, dec, blocks


def cmd_blocks(args):
    names = TypeNames(args.exe)
    for a, e, dec, blocks in _each_datafile(args):
        base = os.path.basename(a.path)
        if blocks is None:
            print("== %s [%d] %s: %d bytes, not chunked" % (base, e.index, e.name, len(dec)))
            continue
        print("== %s [%d] %s: %d bytes -> %d datablocks"
              % (base, e.index, e.name, len(dec), len(blocks)))
        for b in blocks:
            if args.type and not re.search(args.type, names(b["type_hash"]), re.I):
                continue
            if args.name and not re.search(args.name, b["name"] or "", re.I):
                continue
            print("   %5d  %08x  %9d  %-32s %s"
                  % (b["index"], b["id"], b["size"], names(b["type_hash"]), b["name"]))


def cmd_types(args):
    """Census: datablock count and bytes per type, across the archives."""
    names = TypeNames(args.exe)
    census = {}
    for a, e, dec, blocks in _each_datafile(args):
        if blocks is None:
            continue
        for b in blocks:
            c = census.setdefault(b["type_hash"], [0, 0, set()])
            c[0] += 1
            c[1] += b["size"]
            if len(c[2]) < 3:
                c[2].add("%s/%s" % (e.name or "?", b["name"] or "?"))
    rows = sorted(census.items(), key=lambda kv: -kv[1][1])
    print("%-40s %8s %12s  %s" % ("type", "count", "bytes", "examples"))
    for h, (n, sz, ex) in rows:
        print("%-40s %8d %12d  %s" % (names(h), n, sz, "; ".join(sorted(ex))))


def cmd_grep(args):
    """Search decompressed datablocks for 32-bit values, both byte orders,
    and name the datablock each hit falls in."""
    names = TypeNames(args.exe)
    vals = [int(v, 0) for v in args.value]
    needles = [(v, order, struct.pack(fmt, v))
               for v in vals for order, fmt in (("LE", "<I"), ("BE", ">I"))]
    hits = {v: 0 for v in vals}
    for a, e, dec, blocks in _each_datafile(args):
        base = os.path.basename(a.path)
        for v, order, needle in needles:
            start = 0
            while True:
                k = dec.find(needle, start)
                if k < 0:
                    break
                hits[v] += 1
                where = ""
                if blocks:
                    for b in blocks:
                        if b["offset"] <= k < b["offset"] + b["size"]:
                            where = " in datablock %d %s %r (+0x%x)" % (
                                b["index"], names(b["type_hash"]), b["name"],
                                k - b["offset"])
                            break
                print("0x%08x %s: %s [%d] %s @0x%x%s"
                      % (v, order, base, e.index, e.name, k, where))
                start = k + 1
                if args.first:
                    break
    for v in vals:
        print("grep 0x%08x: %d hit(s)" % (v, hits[v]))
    return 0 if any(hits.values()) else 2


def main(argv=None):
    ap = argparse.ArgumentParser(description="reader for Scimitar .forge archives")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, fn, **kw):
        p = sub.add_parser(name, **kw)
        p.add_argument("archive", nargs="+")
        p.set_defaults(func=fn)
        return p

    add("info", cmd_info, help="header summary")
    p = add("list", cmd_list, help="list datafiles")
    p.add_argument("--match", help="regex on the datafile name")
    add("verify", cmd_verify, help="cross-check the derived layout")
    p = add("extract", cmd_extract, help="write datafile payloads to disk")
    p.add_argument("--out", required=True)
    p.add_argument("--match", help="regex on the datafile name")
    p.add_argument("--decompress", action="store_true",
                   help="write the decompressed datablock stream instead of the raw payload")
    p = add("blocks", cmd_blocks, help="list the datablocks inside datafiles")
    p.add_argument("--match", help="regex on the datafile name")
    p.add_argument("--type", help="regex on the resolved type name")
    p.add_argument("--name", help="regex on the datablock name")
    p.add_argument("--exe", help="game executable, to resolve type hashes to class names")
    p = add("types", cmd_types, help="census of datablock types")
    p.add_argument("--match", help="regex on the datafile name")
    p.add_argument("--exe", help="game executable, to resolve type hashes to class names")
    p = add("grep", cmd_grep, help="search decompressed datablocks for 32-bit values")
    p.add_argument("--value", required=True, action="append",
                   help="e.g. 0xA80488AB (repeatable)")
    p.add_argument("--match", help="regex on the datafile name")
    p.add_argument("--exe", help="game executable, to name the datablock a hit falls in")
    p.add_argument("--first", action="store_true",
                   help="stop after the first hit per datafile per byte order")

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
