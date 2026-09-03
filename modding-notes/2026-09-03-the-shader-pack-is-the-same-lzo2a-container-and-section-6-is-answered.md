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
- The **five-byte preamble** is still unidentified. (The per-block `u32` checksum was unidentified
  when this section was written and is **solved in the addendum below** — Adler-32 seeded 0.)

**The diagnostic that would show the container decode is wrong** rather than incomplete: it consumes
the file to the byte and every block reproduces its declared uncompressed size, so a wrong format
would have to be wrong in a way that is self-consistent across 1,361 independent blocks. If a future
shader read produces nonsense, suspect the CTAB interpretation, not the decode.

---

# ADDENDUM — the block checksum is solved, the exe is unpacked, and the state registry is decoded

Same session, still **no launch**.

## 1. The `.forge` block checksum: Adler-32 seeded 0

**It is Adler-32 with the accumulators seeded to 0 instead of 1, over the block's stored
(compressed) bytes** — `zlib.adler32(stored, 0)`. That is LZO's own `lzo_adler32(0, buf, len)`: LZO
documents the seed idiom as `lzo_adler32(0, NULL, 0)`, which *returns* 1, and whoever wrote the
packer initialised the running value to a literal `0` and never made that call.

**That one-bit difference is precisely why "Adler-32" was correctly ruled out on 2026-09-02.** The
standard function matches no block at all. A negative result on the right family, for the wrong
parameter.

`[verified-numerically 2026-09-03, n=241758 blocks across 10 archives]` — every block of every
chunk-compressed datafile in the game, 100% match. I re-checked it here independently over 1,500
blocks (495 raw-stored, 1,005 compressed) from `DataPC_OB.forge`, an archive not used in the
original demonstration, with two implementations: all matched, and standard Adler-32 matched zero.

**The diagnostic that would have shortcut it:** both 16-bit halves are always `< 65521`, so no
checksum has a half in `0xFFF1..0xFFFF`. That gap is an Adler fingerprint and the seed is then a
two-value guess. Recorded in `FORMAT.md`.

⚠️ **A method note on my own error while verifying this.** My first check reported "0 chunked
datafiles found" across three archives — a clean negative that was entirely my bug: I called
`Forge.payload()`, which does not exist (the method is `read()`), inside a bare `except Exception:
continue`. Every entry was silently skipped. **A negative result is only evidence if the test could
have produced a positive one**, and that one could not. Fixed, re-run, and only then believed.

## 2. The exe is SteamStub **Variant 2.1** — and unpacks

`PrinceOfPersia_Launcher.exe` has the same signature Alice had: a `.bind` section holding the entry
point, `.text` at entropy **8.00**, zero `CC` padding runs. It carries **no `0xC0DEC0DF` magic**,
because it is **Variant 2.1**, not 3.x. Steamless unpacks it: entropy **8.00 → 6.61**, `CC` runs
**0 → 2**, `.bind` removed, entry point `0x011022ED` → **`0x00B076BD`** in `.text`.
`[measured 2026-09-03]`

That matters beyond convenience: **every static claim ever made about this exe's `.text` was made
against encrypted bytes.** Strings in `.rdata` were always readable (which is why the state names
were findable), but code searches — including the "no 32-bit immediate 188/189 in `.text`" result
that §6 leaned on — could not have returned a positive. `/gr` reached the same conclusion from the
other direction on 2026-09-03: the searches were correct, at the wrong layer.

⚠️ The unpacked exe is **game content and is not committed**. It regenerates in one command.

## 3. The state registry, decoded

With readable code, the structure falls out. The registry is a table of **12-byte records,
`{char* name; u32 ordinal; u32 hash}`**, based at **`0x00E521E8`**:

```
[  0] 'CGST_Ground'                 ordinal 0    hash 0x06F4ECF7
[  1] 'CGST_Idle'                   ordinal 1    hash 0x407DC47E
...
[188] 'CGST_DebugMode'              ordinal 188  hash 0x861D663F
[189] 'CGST_DebugModeFPSCamera'     ordinal 189  hash 0xA80488AB
```

Both ordinals **and** both hashes reproduce `cgst_registry.tsv` exactly — two independent
confirmations of the layout, from a source (unpacked code) that did not exist when that file was
made. `[inferred-static 2026-09-03]`

**How it is reached, which is the question the board asked.** `0x00E53094` — the descriptor named on
the board — has **exactly one** reference in `.text`, and it is a registration thunk:

```
0x0065D710:  push 1 ; push 0xE53094 ; mov ecx, 0xE48380 ; call 0x505E90 ; ret
0x0065D6F0:  push 1 ; push 0xE521B4 ; mov ecx, 0xE48380 ; call 0x505E90 ; ret   <- the CGST enum
```

There are **258 such thunks**, each registering one enum descriptor into a global registry object at
`0xE48380`; that object is touched from **2,758** sites. **The CGST name table itself has ZERO
references in `.text`** — nothing walks it by a hardcoded pointer, so every lookup goes through the
registry.

**That confirms `/gr`'s reading and answers the board's branch.** A name-driven registry exists, it
is populated at startup for 258 enums including this one, and the absence of an ordinal literal for
188/189 is the *expected* signature of that design rather than evidence the state is unreachable.

## What is still NOT established

- **Which caller looks `CGST_DebugMode` up by name.** Following `0x505E90`'s object API through
  2,758 use sites is the next step, and it is real work rather than a lookup — I have identified the
  mechanism, not the trigger.
- The descriptor header layout is only partly read: the 12-byte entry records are confirmed by the
  CGST table's ordinals and hashes, but the header preceding the entries is not fully decoded, and I
  have deliberately not guessed at its fields.
- Nothing about the debug camera being *usable* follows from any of this. It is authored and
  registered; whether the shipping build can enter it is unanswered.

---

# ADDENDUM 2 — the debug-state entry path is DATA, not code

Same session, still **no launch**. This narrows the board's remaining question and redirects it.

## Two checks the unpack made possible, and their honest results

**1. Neither state name is referenced by code.** `CGST_DebugMode` (`0x00D4D67C`) and
`CGST_DebugModeFPSCamera` (`0x00D4D664`) each have **exactly one** absolute reference in the whole
image, and it is their own entry in the registry table in `.data` — **zero references from
`.text`.** `[inferred-static 2026-09-03]` No compiled code names these states.

**2. The old "no immediate 188/189 in `.text`" negative is formally void — and the positive is
uninformative.** That claim was made against encrypted `.text` and could not have returned a
positive. On the unpacked image the immediates appear **1,196** and **592** times — which tells us
nothing either, because 188 and 189 are ordinary small integers that occur all over any binary.
The question simply cannot be answered by immediate-scanning in either direction.

## Where that leaves the entry path

The registry itself is fully mapped: 258 enum descriptors registered at startup into a global object
at `0xE48380`, reached through **13 distinct methods**, the busiest being `0x0050A2B0` (2,352 call
sites) with registration at `0x00505E90` (258) and two plausible lookup helpers at `0x00505E10` (66)
and `0x00503760` (53).

I checked whether either lookup helper is ever called with a **string literal**: across all 119 call
sites between them, **not one pushes a readable string**. `[inferred-static 2026-09-03]`

Put together with the name having no code reference at all, the conclusion is:

> **Nothing in the executable names this state. If it is reachable, the name or ordinal arrives from
> DATA — a `.forge` datablock — and the UI resolves it generically through the registry.**

That is exactly what `/gr` predicted from the other direction (a pause-menu entry is a *data* route,
so it leaves no literal in code), and it is now established from the binary rather than inferred
from community reports.

## What this changes about the next step

**Stop searching the exe.** The remaining question — *what enters `CGST_DebugMode`* — is a search of
the decoded `.forge` data for a menu/UI datablock that carries the state name or its ordinal, and
the `.forge` reader already parses all 33,401 datafiles. That is a different, cheaper search than
following 2,758 call sites, and it is where `/gr`'s three suggested follow-ups pointed:

1. census the menu classes as the camera classes were censused;
2. search the data for the state NAMES (not the ordinals, not the hashes);
3. read `GraphRuleBook` `Ingame_FreeCam` in full — if a rule book can be entered directly, the state
   ordinal may not be needed at all.

⚠️ **What is NOT established:** that the state is reachable. Everything here establishes only that
*if* it is, the trigger lives in data. A negative result from the data search would be genuinely
meaningful, unlike the immediate-scan negatives, because the `.forge` reader can produce a positive
— it resolves 201 of 202 type hashes and reads every datafile.
