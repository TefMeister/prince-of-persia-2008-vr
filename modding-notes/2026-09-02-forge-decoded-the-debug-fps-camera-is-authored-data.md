# 2026-09-02 — `.forge` decoded end to end; the debug FPS camera is authored, shipped data

**Date:** 2026-09-02, dev PC, `/pd` pass. **The game was never launched, nothing was run,
nothing in the game folder was modified.** Everything below comes from reading the 20
shipped archives and the executable.

Yesterday's `[PD]` item was "write a `.forge` container decoder — the single highest-value
static investment on this project". It is written, verified, and it answered the question
it was written for in the same session. The answer is better than the plan expected.

---

## 1. The decoder — `dev-archive/tools/forge/`

`forge.py` (pure Python, optional `lzo2a.dll` from `lzo2a.c` for speed) reads the
container, decompresses the payloads, splits them into typed, named datablocks, and
resolves the types. Layout in `FORMAT.md`. The verification bar, since it is the thing
everything else rests on:

- **Container:** all **33,401 datafiles in all 20 archives** parse with every derived field
  cross-checked against the datafile's own header copy (size, uid, timestamp, name, magic,
  no overlaps, in bounds, linked list complete both ways) — **0 problems**.
  `[verified-numerically 2026-09-02, n=33,401]`
- **Compression:** payloads are chunked **LZO2A**. The exe carries its compressor enum as
  strings (`LZO1X_1`, `LZO1X_999`, `LZO2A`, `LZX`); the chunk header says type 2; a decoder
  transcribed from LZO's `lzo2a_d.ch` + `config2a.h` reproduces every block to the exact
  declared size, consuming exactly the declared input, ending on the EOF marker — **7.90 GB
  of output across the 14 non-sound archives** without one mismatch, and the C and Python
  decoders agree byte for byte. `[verified-numerically 2026-09-02]`
- **Datablocks:** the decompressed stream is `u16 count; {u32 id; u32 size}[count]` then the
  datablocks; sizes sum exactly to the stream on every datafile. Each begins
  `{u32 typeHash; u32 bodySize; u32 nameLen; name}`.
- **Types:** `typeHash` is **CRC32 of the class name** — the same function the exe's state
  registry uses (`crc32("CGST_DebugModeFPSCamera") == 0xA80488AB`, all 313 rows). A CRC32
  dictionary from the exe's 107k identifier strings resolves **201 of the 202 types** seen.
  `[verified-numerically 2026-09-02]`

Elika was never needed. Two things were *not* established: the per-block `u32 checksum`
(not CRC32/Adler-32/CRC-32C/FNV/djb2/sum over either input or output) and the index's
auxiliary table. Neither is needed to read; the checksum matters only for a future repacker.

## 2. The camera system is data — the `[hypothesis]` is now fact

Estate-wide census (`recon/2026-09-02-forge-decode/type-census.tsv`): **876 `CameraRule`,
277 `PopFixedCamera`, 119 `PopFreeRoamingCamera`, 252 `PopSplineCamera`, 968
`TemporalCameraTransition`, 845 `PathAnimationCamera`, 2,631 `GraphRuleBook`** (rule books
named `Ingame_FreeCam`, `Fight_Cameras`, `Prince_States-SuperStates`…), one `CameraGraph`,
one `CameraTransitionManager`, and a dozen camera subclasses — all in `DataPC.forge →
Game Bootstrap` and the level `_LU` datafiles. `FOV` being an `AnimatableCameraParameter`
(2026-09-01) fits this exactly. `[verified-numerically 2026-09-02]`

So the route to owning this game's camera **does** run through data, as filed yesterday —
and the data is now readable.

## 3. The debug FPS camera: authored, shipped, and conditioned on state 189

The `/gr` plan was "search datablocks for hash `0xA80488AB`, with a positive control".
Executed as written, controls first:

- **The control failed, and that is the finding.** `CGST_Idle`, `CGST_Walk`, `CGST_Ground`
  — states that certainly run in normal play — hit only inside `SoundBao` audio blocks, at
  identical offsets in duplicated sounds. So do the target hashes. **States are not stored
  as hashes in data.** The hash-needle method is `[disproved 2026-09-02]`; a null on
  `0xA80488AB` proves nothing, exactly as the topic warned.
- **The literal-string search hit.** `TemporalCameraTransition "DebugMode_Transition"` and
  `"FPSCamera_Transition"` in Game Bootstrap; datablock names then gave `CameraRule
  "CR_Debug_1stPerson"`, `"CR_Debug_GhostCam"`, `"CR_Debug_Marketing"`,
  `PopMarketingCamera "CAM FPS"`, `PopGhostCamera "CAM Ghost POP"`,
  `GraphRuleBook "Ingame_FreeCam"`.
- **States are referenced by ordinal.** Inside a `CameraRule` body the sub-record whose
  class hash resolves to **`PopCharacterGraphStateDescription`** is `u32 3; u32 state[3]`,
  and the registry says **309 = `CGST_Any`**:

  | datablock | states |
  | --- | --- |
  | `CR_Debug_1stPerson` | **188 `CGST_DebugMode`, 189 `CGST_DebugModeFPSCamera`, 309** |
  | `CR_Debug_GhostCam` | 188, 309, 309 |
  | unnamed `CameraRule`, `LR4_TowerExterior_LU` (level-local) | 188, 188, 309 |
  | every other `CameraRule` (873 estate-wide) | 309, 309, 309 |

  Sibling records in the same body resolve to `PopStateRuleCondition`,
  `BooleanRuleCondition`, `CameraExecution`, `CameraHolder`,
  `CameraTransitionSpecification` — the rule → camera → transition chain is complete.

**So `CGST_DebugModeFPSCamera` is not a name that outlived its code: a shipped camera rule
is conditioned on it, with its own camera object and transition.** The 2026-09-01 worry
("do not record 'PoP has a debug FPS camera' as fact") is resolved on the data side:
**the camera side of the debug first-person mode is authored and present.**
`[verified-numerically 2026-09-02]`

## 4. What is NOT established: how the Prince *enters* `CGST_DebugMode`

- Estate-wide (all 14 non-sound archives, 7,830+ `PopCharacterGraphStateDescription`
  records), exactly **three** rules name 188 or 189: the two above and one unnamed
  level-local `CameraRule` in `DataPC_LR.forge → LR4_TowerExterior_LU` on (188, 188, 309).
  All three are camera *consumers* of the state; nothing in data *transitions* into it.
- `.text` contains **no 32-bit immediate 188 or 189** in `push`/`mov reg`/`mov r/m`/`cmp`
  forms. Nothing in code hard-codes the ordinal.
- The exe has an `FPSCamera` class and a `DynamicLoadingDebugModeEvent`; no console or key
  string names debug mode.

Two readings remain, and static work cannot yet pick between them:
(a) entry is **name-driven** — a console command or debug-menu action resolves
`CGST_DebugMode` to 188 through the registry at run time (the registry *descriptor* is
referenced from code; the rows are not), so no immediate would ever appear; or
(b) the entry path was stripped and only the camera data survived. `[hypothesis]` either
way. The bounded static step that decides it: find the function that walks the registry
descriptor at `0x00E53094` for a name → ordinal lookup and enumerate its callers.

## 5. The mod-shaped consequence

Because rules select cameras by state, **a data edit — not a code patch — could make the
FPS camera the live one**: rewrite `CR_Debug_1stPerson`'s state list to (309, 309, 309) and
raise its priority above `Archetype_FreeRoaming`, and the "CAM FPS" `PopMarketingCamera`
would apply in normal play without ever entering debug mode. That needs a repacker. The
format allows **raw (uncompressed) blocks** (`uncompressed == compressed` in the block
table), so no LZO2A *compressor* is required — but the unknown per-block checksum may or may
not be verified by the engine, and every offset in the archive shifts when one datafile
grows. Contingent on the checksum question; not a `[PD]` row until it is decided.

## 6. Method notes worth keeping

- The payload offset was first estimated at +0x1b7 from last-non-zero-byte analysis; the
  chunk walk over-ran by exactly one byte on every file and corrected it to +0x1b8. LZO2A
  streams end in a zero byte. Cross-checks that *must* fit exactly are worth more than
  reading hex.
- The name-table field first labelled "nameHash" is a Unix build time (`0x492333e9` =
  2008-11-18) — values repeated across different names, which a hash cannot do.
- Checking the exe for the compressor's own enum strings beat guessing the LZ variant from
  byte patterns. Filed to the cross-engine library's inbox.

## 7. Evidence rescued

`dev-archive/recon/2026-09-02-forge-decode/` — archive index, type census, camera datablock
listing, sweep hits, re-decoded registry. Names, hashes, offsets and counts only.

🤖 Static analysis only. No launch, no debugger, nothing modified, no game content copied.
