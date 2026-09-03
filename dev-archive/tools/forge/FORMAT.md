# Prince of Persia (2008) `.forge` — container, compression and datablock layout

Derived on 2026-09-02 (`/pd`, dev PC, game never launched) by reading the 20 shipped
archives with `forge.py`. Everything below is `[verified-numerically 2026-09-02]`
unless tagged otherwise: the reader parses all **33,401 datafiles in all 20 archives with
zero cross-check failures** (`forge.py verify *.forge`), and the decompressor reproduced
every block it was pointed at to the exact declared size, consuming exactly the declared
input and ending on the LZO EOF marker — **7.90 GB of decompressed output across the 14
non-sound archives** in one sweep, plus a native-vs-Python cross-check on 10 blocks.

No public schema for this container generation existed; the best public write-up covers
the later AnvilNext variant and stops at the resource boundary. Fields marked `?` are
unexplained but constant on this game. All integers little-endian.

## 1. Archive header (offset 0)

| off | type | value on this game |
| --- | --- | --- |
| 0x00 | `char[8]` | `"scimitar"` |
| 0x08 | `u8` | 0 |
| 0x09 | `u32` | 26 (format version) |
| 0x0d | `u64` | `tableOffset` — always 0x416 here |
| 0x15 | `u32` | 0x10 `?` |
| 0x19 | `u32` | 1 `?` |

## 2. Index table (at `tableOffset`)

| off | type | meaning |
| --- | --- | --- |
| +0x00 | `u32` | total datafile count |
| +0x04 | `u32` | 1 `?` |
| +0x08 | `u64` | 0 |
| +0x10 | `i64` | −1 |
| +0x18 | `u32` | chunk capacity — 5000 |
| +0x1c | `u32` | chunk count |
| +0x20 | `u64` | first chunk offset (= `tableOffset` + 0x28) |

### Index chunk (up to 5000 entries each; the sound archives with 6260 files use two)

| off | type | meaning |
| --- | --- | --- |
| +0x00 | `u32` | entries in this chunk |
| +0x04 | `u32` | 1 `?` |
| +0x08 | `u64` | file-table offset (= chunk + 0x30) |
| +0x10 | `i64` | next chunk offset, −1 on the last |
| +0x18 | `u32` | 0 |
| +0x1c | `u32` | 4999 (capacity − 1) |
| +0x20 | `u64` | name-table offset |
| +0x28 | `u64` | auxiliary table offset — purpose not established, not needed to extract |
| +0x30 | `{u64 dataOffset; u32 ?; u32 size}[n]` | file table |

The file table's second field is a per-file 32-bit value (`0xcffb0dae`-ish, sequential
within an archive) that also appears at +0x00 of the datafile descriptor. Not a size,
not a CRC32 of anything obvious; treat as opaque. The `GlobalMetaFile` entry carries
0x10 there.

Both sub-tables are pre-allocated at full capacity: in chunk 0 the file table runs
0x46e..0x13cee (5000 × 16) and the name table begins exactly there.

### Name-table record (stride 0xBC)

| off | type | meaning |
| --- | --- | --- |
| +0x00 | `u32` | size (equals the file-table size) |
| +0x04 | `u64` | uid |
| +0x1c | `i32` | next index (archive-global; −1 at the tail) |
| +0x20 | `i32` | previous index (−1 at the head) |
| +0x28 | `u32` | Unix time — a build date (`0x492333e9` = 2008-11-18). **Not a hash**: the same value recurs across different names |
| +0x2c | `char[]` | name, NUL-terminated; 128-byte field |

The doubly-linked list visits every entry exactly once in both directions (checked).

## 3. Datafile (at `dataOffset`)

| off | type | meaning |
| --- | --- | --- |
| +0x000 | `char[8]` | `"FILEDATA"` |
| +0x008 | `char[]` | name, NUL-padded to +0x187 |
| +0x187 | descriptor | `u32 ?` (the file-table value) · `u32 size` · `u64 uid` · zeros · `u32 ?` · `u32 ?` · `u32 unixTime` at +0x28 · `u32 0` · `u8 0` — 0x31 bytes |
| +0x1b8 | `u8[size]` | payload |

The payload offset was first estimated at +0x1b7 from last-non-zero-byte analysis and
corrected to +0x1b8 when the chunk walk over-ran by exactly one byte on every file —
LZO2A streams end in a zero byte, which is what fooled the first estimate.

Datafiles are 0x800-aligned. Every archive's entry 0 is a 195-byte `GlobalMetaFile`
and entry 1 an unnamed 79–303-byte blob that is **not** chunk-compressed (it carries a
lightly obfuscated build string); everything else is.

## 4. Payload: chunked LZO2A

A payload is a chain of compressed chunks, each:

| type | meaning |
| --- | --- |
| `u8[8]` | magic `33 AA FB 57 99 FA 04 10` |
| `u16` | 1 (version) |
| `u8` | compression type — **2 everywhere seen** |
| `u16` | 0x8000 max block size |
| `u16` | 0x8000 `?` |
| `u16` | block count |
| `{u16 uncompressed; u16 compressed}[count]` | block table |
| per block: `u32 checksum; u8 data[compressed]` | |

A block whose two sizes are equal is stored raw. Blocks are ≤ 32 KiB uncompressed.

**Compression type 2 is LZO2A.** The executable carries the compressor enum as literal
strings — `LZO1X_1`, `LZO1X_999`, `LZO2A`, `LZX` — and the LZO2A decoder transcribed from
LZO's `lzo2a_d.ch` with the `config2a.h` constants (`SWD_N 8191`, hence no M3 branch;
`M1_MIN_LEN 2`; `LZO_EOF_CODE`) reproduces every block exactly. Bit buffer is LSB-first,
refilled a byte at a time. `lzo2a.c` is the C transcription; `forge.py` falls back to the
pure-Python one when the DLL is absent (measured 184 MB/s native on the 61 MB Game Bootstrap datafile; the Python path is tens of times slower on large files, fine for single datafiles). `lzo2a.dll` is a build artifact and is git-ignored — build it with the one-line `clang` command in its header.

**✅ The per-block `checksum` is SOLVED (2026-09-03): it is Adler-32 with the accumulators
seeded to 0 instead of 1**, computed over the block's **stored (compressed) bytes** - i.e. exactly
the `u8 data[compressed]` that follows it. Equivalently `zlib.adler32(stored, 0)`.

This is LZO's own `lzo_adler32(0, buf, len)`. LZO documents the seed idiom as
`lzo_adler32(0, NULL, 0)`, which *returns* 1; whoever wrote the packer initialised the running value
to a literal `0` and never made that call. That one-bit difference is exactly why "Adler-32" was
correctly ruled out before - the standard function never matches a single block.

```python
BASE = 65521
def block_checksum(stored_bytes):     # note: a starts at 0, not 1
    a = b = 0
    for x in stored_bytes:
        a = (a + x) % BASE
        b = (b + a) % BASE
    return (b << 16) | a
```

`[verified-numerically 2026-09-03, n=241758 blocks across 10 archives]` - every block of every
chunk-compressed datafile in the game (401 of 33,401 entries are chunked; the rest are streamed
sound and metadata with no block checksums), 100% match, 0 failures. Independently re-checked in
this session over 1,500 blocks from `DataPC_OB.forge` with two implementations; standard Adler-32
matched **0** of them.

**Diagnostic tell, worth remembering for the next unknown u32:** both 16-bit halves are always
`< 65521`, so no checksum ever has a half in `0xFFF1..0xFFFF`. That gap in the distribution is the
Adler fingerprint, and the seed is then a two-value guess. An all-zero block hashes to `0x00000000`
here, where standard Adler-32 would give `0x00010001`.

**For a repacker:** compute it *after* compression, over the bytes you are about to write; for a
raw-stored block (`uncompressed == compressed`) over those same bytes. That is the whole rule.

## 5. Decompressed stream: datablocks

The decompressed stream is a **datablock table followed by the datablocks**:

```
u16 count
{ u32 id; u32 size }[count]      -- sizes sum exactly to the rest of the stream
datablock[count], back to back
```

Each datablock:

```
u32 typeHash        -- CRC32 of the engine class name (see §6)
u32 bodySize        -- bytes after the name
u32 nameLen
char name[nameLen]  -- then a NUL
u8  body[bodySize]
```

`id` is a per-object 32-bit reference (small integers in the tiny archives, hash-like
elsewhere); other datablocks refer to it by value.

## 6. Hashes are CRC32 of the identifier — exe-side and data-side

`zlib.crc32(b"CGST_DebugModeFPSCamera") == 0xA80488AB`, the value the executable's own
state registry stores beside that name — so the registry's third column is plain CRC32
`[verified-numerically 2026-09-02, all 313 rows reproduce]`. The datablock `typeHash`
is the same function over the class name: building a CRC32 dictionary from every
identifier-shaped string in the exe (107,173 of them) resolves **201 of the 202 type
hashes** seen across the estate (`TextureMap`, `MaterialTemplate`, `CameraRule`,
`PopCharacterGraphStateDescription`, …). The one unresolved type, `0x824a23ba`, is the
`*_SubFX` family (4,703 blocks) and simply has no matching string in the exe.

Serialized sub-records inside a body carry the same kind of tag: e.g. a `CameraRule`
body is a sequence of `{u32 objectId; u32 classHash; ...}` records whose class hashes
resolve to `PopStateRuleCondition`, `PopCharacterGraphStateDescription`,
`BooleanRuleCondition`, `CameraExecution`, `CameraHolder`,
`CameraTransitionSpecification`, `MarketingCameraCondition`.

## 7. How the character state machine is referenced in data

**Not by hash.** The 313 `CGST_*` state hashes do not occur in any datablock outside
audio noise: three positive-control states that unquestionably run in normal play
(`CGST_Idle`, `CGST_Walk`, `CGST_Ground`) were searched estate-wide and every hit fell
inside `SoundBao` (audio) blocks at identical offsets in duplicated sounds — chance
bytes, not references. The hash-needle plan is therefore **disproved as a method**
`[disproved 2026-09-02]`, and a null on `0xA80488AB` proves nothing.

**By ordinal.** `PopCharacterGraphStateDescription` is `u32 count=3; u32 state[3]` with
the registry ordinals, and `309 = CGST_Any` as the don't-care sentinel. The two debug
camera rules read:

| datablock | states |
| --- | --- |
| `CameraRule "CR_Debug_1stPerson"` | 188 `CGST_DebugMode`, **189 `CGST_DebugModeFPSCamera`**, 309 `CGST_Any` |
| `CameraRule "CR_Debug_GhostCam"` | 188 `CGST_DebugMode`, 309, 309 |
| unnamed `CameraRule` in `LR4_TowerExterior_LU` | 188, 188, 309 |
| every other `CameraRule` (873 estate-wide) | 309, 309, 309 |

## 8. Tool

```
python forge.py info     *.forge
python forge.py verify   *.forge                       # 33,401 entries, 0 problems
python forge.py list     DataPC.forge
python forge.py blocks   --exe PrinceOfPersia_Launcher.exe --match "Game Bootstrap" --type Camera DataPC.forge
python forge.py types    --exe PrinceOfPersia_Launcher.exe DataPC.forge
python forge.py grep     --exe PrinceOfPersia_Launcher.exe --value 0xBC DataPC.forge
python forge.py extract  --decompress --out <dir> --match "Game Bootstrap" DataPC.forge
clang -O2 -shared -o lzo2a.dll lzo2a.c                 # optional, for speed
```

Read-only against the game folder. Never commit archives, extracted datablocks or the
executable — names, offsets, hashes and counts are interface metadata and are all this
folder holds.
