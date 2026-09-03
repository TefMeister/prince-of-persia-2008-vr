# The shader pack is the same LZO2A container — §6 is answered, and a recorded dead end was wrong

**Session:** `/pd`, dev PC, 2026-09-03. **The game was not launched, and nothing here has been
run.** Everything below is read off files already on this disk.

## The blocker that was never real

On 2026-09-01 this dossier recorded a hard stop:

> **⛔️ The shipped shader pack is LZ-compressed — the CTAB route does not work here.** …
> `CTAB` occurs **830 times** … **But not one of the 830 parses.** … constant names come out
> **shredded by inserted bytes** — `ViewPro*j`, `Vi@ewProj`, `UVMatrixJ1` … **no register index is
> recoverable**.

Every one of those measurements is correct. **The conclusion drawn from them was not.** The file is
not opaque — it is the **same LZO2A container the `.forge` archives use**, and the decoder written
for `.forge` on 2026-09-02 decodes it almost unchanged. `[disproved 2026-09-03]`

That is the third recorded blocker on this estate to dissolve on inspection, and the pattern is the
same each time: a correct observation, a plausible inference, and nobody re-tested the inference
once new tooling existed. The `.forge` decoder had been sitting beside this file for a day.

## The container

The magic is the giveaway: `33 AA FB 57 99 FA 04 10` — byte-identical to `.forge` — sits at offset
**5**, behind a five-byte preamble.

```
u8[5]  preamble          f5 9f 37 a8 02      (unidentified, skipped)
u8[8]  magic             33 AA FB 57 99 FA 04 10
u16    version           1
u8     compression       2 = LZO2A
u16    max block size    0x8000
u16    ?                 0x0000              (.forge has 0x8000 here)
  then per block, to EOF:
u8     flag              1 on all 1,361 blocks
u32    compressed size
u32    uncompressed size
u32    checksum          the same unidentified u32 as .forge
u8[]   data
```

**The only structural difference from `.forge` is that there is no block table** — the sizes are
inline per block, each header carrying a leading flag byte. LZO2A, the 32 KiB block size and the
trailing checksum are all shared.

Getting there took two wrong turns worth recording, because both looked right: parsing it with the
`.forge` header gave `nblk = 56065` and a garbage block table, and assuming 4-byte alignment between
blocks decoded exactly two blocks before failing. What settled it was scanning the whole file for
`u32 == 0x8000` (a full uncompressed block) and reading off the **actual** spacing, which came out
as a constant 1-byte gap — the flag byte belonging to the *next* header.

**Result** `[verified-numerically 2026-09-03, n=1361 blocks]`: 1,361 blocks, **zero decompression
failures**, the file consumed **exactly** (0 bytes left over), 9,784,709 → 44,578,719 bytes (4.56×),
containing **17,464 `CTAB`** and **0 `DXBC`** — D3D9, as the dossier already had it.

Tool: `dev-archive/tools/forge/ekshaderspc.py`, which reuses `forge.py`'s verified LZO2A decoder
rather than duplicating it. Its output is byte-identical (sha256) to the ad-hoc decode that found
the format.

## §6: the camera constant, and the register that carries it

`d3d9-ctab.py` parses **17,270 constant tables** out of the decoded stream (8,700 `vs_3_0`,
8,570 `ps_3_0`).

| constant | class | registers | shaders |
| --- | --- | --- | --- |
| **`g_WorldViewProj`** | `MATRIX_ROWS` | **`vs c0 ×4`** (6,292) · **`c128 ×4`** (2,016) · `c8` (96) · `c12` (24) | **8,428** |
| `g_World` | `MATRIX_ROWS` | `vs c4 ×4` (5,274) · `c132 ×4` (1,582) | 7,992 |
| `g_WorldView` | `MATRIX_ROWS` | `vs c4 ×3` (287) · `c132 ×3` (261) | 688 |
| `g_ViewerPosition` | `VECTOR` | `ps c10`/`c7`/`c13` | 6,417 |
| `g_WorldToLightProj` | `MATRIX_ROWS` | `ps c10 ×3`/`c3 ×3` | 2,588 |
| `g_Bones` | `MATRIX_ROWS` | **`vs c0 ×128`** | 2,016 |

**The `c0` ⇄ `c128` split is the skinning palette**, and the correlation is exact: every one of the
2,016 shaders with `g_WorldViewProj` at `c128` has `g_Bones` occupying `c0..c127`, and **not one of
the 6,292 at `c0` has any large array at all**. `[inferred-static 2026-09-03, n=8428]` This is the
same displacement `alan-wake-vr` has (there a 192-register palette), and it means **a proxy must
resolve the register per shader; a fixed `c0` would corrupt 2,016 shaders.**

### The convention, established two ways — because metadata alone nearly caught me out today

1. **CTAB type metadata:** `g_WorldViewProj` is `D3DXPC_MATRIX_ROWS`.
2. **The shipped bytecode agrees.** The simplest vertex shader carrying it, in full:

```
def c4, 3.05185e-05, 1, 0, 0
dcl v0
dcl o0
mul r0.x, c4.x, v0.w
mul r0.xyz, r0.x, v0
mov r0.w, c4.y
dp4 o0.x, c0, r0
dp4 o0.y, c1, r0
dp4 o0.z, c2, r0
dp4 o0.w, c3, r0
```

Four consecutive `dp4`s against `c0..c3` ⇒ **registers are ROWS**, column-vector convention.
`[inferred-static 2026-09-03, two independent reads]`

This check is not ceremony. Earlier today `alice-madness-returns-vr` turned out to be
`MATRIX_COLUMNS` — accumulating `mul`/`mad` rather than `dp4` — so the identical-looking formula
needed a **transposed** implementation there. Prince of Persia is on Alan Wake's side of that line.

## What this means for the per-eye maths — and it is already written

`g_WorldViewProj` is **fused** (world → clip in one matrix; there is no standalone projection to
shear, and `g_World`/`g_WorldView` are separate but do not carry the projection). So this needs the
**clip-space form**, not a view/projection split:

```
row0 += S · row3 ;  row0.w -= S · C        with S = p00 · eye_dx / C
```

That is exactly `alan-wake-vr`'s `aw_stereo_apply_fused_clip`, written and verified **today** —
same `MATRIX_ROWS` convention, same fused shape. It ports directly. `[verified-numerically
2026-09-03]` covers the maths; nothing about *this game's* use of it is verified.

The three projects now sit at three different points of the same design space, which is why the
matrix-class check earned its keep:

| project | class | shape | implementation |
| --- | --- | --- | --- |
| `alan-wake-vr` | `MATRIX_ROWS` | split view + projection | two single-float edits |
| `alan-wake-vr` (515 fused shaders) | `MATRIX_ROWS` | fused | `row0 += S·row3` |
| `alice-madness-returns-vr` | **`MATRIX_COLUMNS`** | fused | **transposed**: `c[i].x += S·c[i].w` |
| **`prince-of-persia-2008-vr`** | `MATRIX_ROWS` | fused | **Alan Wake's fused form, unchanged** |

## What is NOT established

- **Nothing has been run.** The container decode is verified against the file itself; the *stereo*
  is not, on this game.
- **`p00` recovery is doubtful here, more so than elsewhere.** For a fused `World→Clip` the
  `|row0.xyz| = p00` trick needs everything after the projection to be rigid, and `g_WorldViewProj`
  has the object's world transform baked in — **object scale breaks it**. The Alan Wake module
  already documents this and takes `p00` as a parameter for exactly this reason, so a proxy here
  must source `p00` some other way (there is no standalone projection constant to read it from,
  which is a real open question for this game specifically).
- **Which draws are the camera's** is unanswered, as it was for Alan Wake's fused paths:
  `g_WorldToLightProj` shows a shadow/light path exists, and a camera shear applied to it would
  corrupt shadows. The orthographic guard is a fail-safe, not an answer.
- The **five-byte preamble** and the **per-block `u32` checksum** are both still unidentified. The
  checksum is unchanged from `.forge` and is the subject of its own open item.

**The diagnostic that would show the container decode is wrong** rather than incomplete: it consumes
the file to the byte and every block reproduces its declared uncompressed size, so a wrong format
would have to be wrong in a way that is self-consistent across 1,361 independent blocks. If a future
shader read produces nonsense, suspect the CTAB interpretation, not the decode.
