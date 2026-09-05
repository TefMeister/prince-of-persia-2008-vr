# The ActionBlock census, searched: menus and ActionBlocks never reference each other

`/pd`, home PC, no launch. Closes the `[PD]` row from 2026-09-04b: search the 2,464-block
`ActionBlock` census for one referencing `StartMenuDebug_m` (`0x81358011`) or
`DebugMenuHandler_m` (`0x96e48045`).

## The answer

**Neither id appears in any `ActionBlock`, anywhere in the shipped PC data.**
`[verified-numerically 2026-09-05, n=2,464 blocks, 0 hits]`

Nor does the id of a third debug screen found on the way (`CheatMenuMagma_m`, `0x96e48049`).
**Nor do any of the 19 ordinary menu-handler ids used as controls, `MainPauseMenuHandler_m`
included.** `[verified-numerically 2026-09-05, n=2,464 x 19, 0 hits]` So this is not the debug
menus being stripped or special: **the `ActionBlock` system and the menu system do not reference
each other at all in this game's data.** The 2026-09-04 guess was structurally wrong rather than
unlucky, and the branch is closed rather than merely unproductive.

## Why the search can be trusted

18 archives (every `.forge` in the install), **33,401 datafiles** — matching
`archive-index.txt`'s own total exactly — **9.28 GB decompressed and searched**, zero decompress
failures, zero datablock-split failures. **2,464 `ActionBlock`s enumerated, matching the
independent 2026-09-02 `type-census.tsv` count exactly**, which is the cross-check that the
population searched was the whole one.

A negative only counts if the test could produce a positive. Three controls did:

- The identical scan, run against each `ActionBlock`'s own datafile id table, found **2,439 of
  2,464 (99.0%) DO carry other datablocks' raw ids** — `Animation`, `BodyPartTemplate`,
  `SoundBao`, up to 63 in one block. `[verified-numerically 2026-09-05, n=2,439]`
- The needle sweep rediscovered all three known sites of each debug id without being told where.
- Magma UI files store ids as ASCII text (`"0x081b8052"`), which a binary needle would miss, so a
  second full pass swept the text form: `MagmaCommon_MGB`'s id **274** hits, `MagmaFonts_MGB`'s
  **2,390** — the debug ids **zero**, in any case or prefix variant.
  `[verified-numerically 2026-09-05, n=2,664 control hits, 0 target hits]`

## What the pass found instead — and it is the better finding

**Every menu-handler datablock has the same body: `{u32 own id; u32 typeHash; u32 MagmaMgbFile id;
u32 nameLen; char screenName[]}`.** `[verified-numerically 2026-09-05, n=39 handler blocks; 36
resolve the third field to a real MagmaMgbFile in the same datafile, 3 hold 0 and carry no screen
name]`

| block | type | id | Magma UI file | screen |
| --- | --- | --- | --- | --- |
| 31 | `StartMenuDebug_m` | `81358011` | `MagmaCommon_MGB` (`081b8052`) | `P_MainMenuDebug` |
| 40 | `DebugMenuHandler_m` | `96e48045` | `MagmaCommon_MGB` | `P_PauseMenuDebug` |
| **56** | **`CheatMenuMagma_m`** | **`96e48049`** | **`MagmaCommon_MGB`** | **`P_CheatMenuDebug`** |
| 33 | `MainPauseMenuHandler_m` | `96e48031` | `MagmaInGame_MGB` (`082ac02a`) | `P_PauseMenu` |

Two consequences.

- **There is a THIRD shipped debug screen**, `P_CheatMenuDebug`, entry 30 of the 41-entry
  `InterfaceManager` registry, bound to the same UI file and registered exactly like the other
  two. The type was in the 2026-09-04 census excerpt but was not read as a debug screen.
  `[verified-numerically 2026-09-05]`
- **A menu-handler datablock carries no behaviour at all.** It is a binding of a screen name to a
  Magma UI file — there is no field where an `ActionBlock` id or a state name would go. So what a
  debug menu ITEM does lives either inside `MagmaCommon_MGB` (block 419, 1,338,945 bytes, holding
  all three debug screens) or in the C++ handler class in the exe. That is where the link to
  `CGST_DebugMode` has to be. `[inferred-static 2026-09-05]`

Corroborating the "in the exe" half: the exe carries the class names `DebugMenuHandler_m`,
`StartMenuDebug_m`, `CheatMenuMagma_m` in its reflection table but **none** of the `P_*` screen
names, and `MagmaCommon_MGB` contains no `P_*MenuDebug` string in ASCII or UTF-16LE — the screen
names exist only in the handler datablocks. `[verified-numerically 2026-09-05]`

## Limit worth recording

The needles were the 32-bit id (both byte orders), the screen-name strings (ASCII and UTF-16LE),
and the ASCII text form of each id. **A reference by registry INDEX rather than id would not have
been caught** — `DebugMenuHandler_m` is entry 14 of 41, and a one-byte ordinal is unsearchable.
`[hypothesis]`

## Verification of this write-up

The census row count was re-checked independently of the search that produced it:
`actionblock-census.tsv` holds 2,464 rows plus a header, and the 2026-09-02 `type-census.tsv`
line for `ActionBlock` reads `2464`. The two counts come from different passes over the archives
on different days, so the agreement bounds the population rather than restating it.

## Evidence

`dev-archive/recon/2026-09-05-actionblock-census-search/` — the full 2,464-row census, the run
log, every needle hit, the text-form sweep, the decoded menu-handler layout table, the decoded
41-entry `InterfaceManager` registry, and the three scripts that produced them.

**The game was not launched; nothing here was run.**
