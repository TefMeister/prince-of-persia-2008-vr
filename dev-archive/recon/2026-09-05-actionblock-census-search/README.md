# 2026-09-05 — the ActionBlock census, searched: no ActionBlock references the debug menus

`/pd` pass, home PC, **the game was never launched**. Closes the `[PD]` row opened by
`modding-notes/2026-09-04b-debug-menu-screens-confirmed-in-pc-data.md`: *search the 2,464-block
`ActionBlock` census for one referencing `StartMenuDebug_m` (`0x81358011`) or `DebugMenuHandler_m`
(`0x96e48045`).*

Everything here was produced by `dev-archive/tools/forge/forge.py` (+ `lzo2a.dll` built from
`lzo2a.c`) reading the shipped archives read-only. No game content is stored — only ids, offsets,
block names, type names and counts, which are interface metadata.

## Answer: a clean negative, with the search proved to work

**No `ActionBlock` anywhere in the shipped PC data references `StartMenuDebug_m`,
`DebugMenuHandler_m` or `CheatMenuMagma_m`.** `[verified-numerically 2026-09-05, n=2,464 blocks,
0 hits]`

**And no `ActionBlock` references ANY of the 19 menu-handler ids either** — including the ordinary
`MainPauseMenuHandler_m` / `P_PauseMenu`. So this is not the debug menus being special: the
`ActionBlock` system and the menu system simply do not reference each other in this game's data.
`[verified-numerically 2026-09-05, n=2,464 blocks x 19 control ids, 0 hits]`

## How the enumeration was made complete

| | |
| --- | --- |
| archives scanned | **18** — every `.forge` under the install folder, matching the 18 in `2026-09-02-forge-decode/archive-index.txt` |
| datafiles scanned | **33,401** — matches `archive-index.txt`'s own total exactly |
| decompressed bytes searched | **9,279,242,190 (9.28 GB)** |
| decompress failures | **0** |
| datablock-split failures | **0** |
| `ActionBlock`s enumerated | **2,464** — matches the independent 2026-09-02 `type-census.tsv` count exactly |

`ActionBlock` was identified by `type_hash == crc32("ActionBlock") == 0xef82fce4`, the same
resolution the 2026-09-02 census used; the two counts agreeing at 2,464 is the cross-check that
the enumeration is the whole population and not a subset.

Every ActionBlock found is listed in `actionblock-census.tsv` (archive, datafile, block index, id,
size, name, and how many other datablock ids its bytes contain).

## Why the negative is evidence — three positive controls

A negative only counts if the same test can produce a positive. Three did:

1. **Control A — id references inside `ActionBlock`s exist and are detected.** The identical
   byte scan, applied to each `ActionBlock`'s own bytes against the id table of its own datafile,
   found that **2,439 of 2,464 (99.0%)** carry at least one other datablock's id — typically
   `Animation` and `BodyPartTemplate` ids, up to 63 of them in one block. So `ActionBlock` bodies
   *do* hold raw 32-bit datablock ids, and the scan finds them.
   `[verified-numerically 2026-09-05, n=2,439]`
2. **Control B — the same needle sweep finds the debug ids where they really are.** It reproduced
   all three known sites per id (the datafile's own datablock index table, the `InterfaceManager`
   registry, and the block's own body header) without being told where to look.
   `[verified-numerically 2026-09-05, n=3 ids x 3 sites]`
3. **Control C — the text-form sweep works too.** Magma UI files store datablock ids as ASCII
   (`"0x081b8052"`), which a binary needle would miss, so a second full pass swept for the text
   form. It found the `MagmaCommon_MGB` id **274** times and the `MagmaFonts_MGB` id **2,390**
   times — and the three debug menu ids, and the control `MainPauseMenuHandler_m` id, **zero**
   times, in any case or `0x`-prefix variant. `[verified-numerically 2026-09-05, n=2,664 control
   hits, 0 target hits]`

## What the search found instead — the menu handler block layout

Falling out of the same pass, and the more useful result: **every menu-handler datablock has the
same three-field body — `{u32 own id; u32 typeHash; u32 MagmaMgbFile id; u32 nameLen; char
screenName[]}`.** `[verified-numerically 2026-09-05, n=39 handler blocks in DataPC.forge -> Game
Bootstrap; 36 of the 39 resolve their third field to a real `MagmaMgbFile` datablock in the same
datafile, the other 3 hold 0 and carry no screen name — `PauseMenuHandler_m`,
`PreGameMenuHandler_m` and one `MagmaMenuHandler_m`, which look like base classes]` Full table in `menu-handler-block-layout.txt` (its
40th row, block 11, is the `InterfaceManager` registry itself, which has a different body and is
shown only because it was caught by the same type filter). The relevant rows:

| block | type | id | Magma UI file | screen |
| --- | --- | --- | --- | --- |
| 31 | `StartMenuDebug_m` | `81358011` | `MagmaCommon_MGB` (`081b8052`) | `P_MainMenuDebug` |
| 40 | `DebugMenuHandler_m` | `96e48045` | `MagmaCommon_MGB` | `P_PauseMenuDebug` |
| **56** | **`CheatMenuMagma_m`** | **`96e48049`** | **`MagmaCommon_MGB`** | **`P_CheatMenuDebug`** |
| 33 | `MainPauseMenuHandler_m` | `96e48031` | `MagmaInGame_MGB` (`082ac02a`) | `P_PauseMenu` |
| 54 | `HudMenuHandler_m` | `81358015` | `MagmaHUD_MGB` | `P_HUD` |

Two things follow.

- **There is a THIRD shipped debug screen: `CheatMenuMagma_m` / `P_CheatMenuDebug`,** entry 30 of
  the 41-entry `InterfaceManager` registry, bound to the same `MagmaCommon_MGB` and registered
  exactly like the other two. The type was already in the 2026-09-04 census excerpt but was not
  identified as a debug screen; its screen name and its registration are new.
  `[verified-numerically 2026-09-05]`
- **A menu-handler datablock carries no behaviour at all** — it is a 91–290 byte binding of a
  screen name to a Magma UI file. Nothing in it could ever have named `CGST_DebugMode`, and there
  is no field where an `ActionBlock` id would go. The menu *item* and what selecting it does live
  either inside the Magma UI file (`MagmaCommon_MGB`, 1,338,945 bytes, holds all three debug
  screens) or in the C++ handler class in the exe. `[inferred-static 2026-09-05]`

`interface-manager-41-entries.txt` decodes the full registry: 41 entries, all resolving to
handler datablocks in the same datafile, with the three debug screens at entries 5, 14 and 30.

## Known limits of this search

- Needles were the 32-bit id in both byte orders, the ASCII and UTF-16LE screen-name strings, and
  the ASCII text form of each id. **A reference that is neither of those** — an index into the
  registry table rather than an id, a hash of the id, or a name stored in the Magma files'
  quoted-printable-looking encoding — **would not have been caught.** The registry-index
  possibility is real and cheap to think about: `DebugMenuHandler_m` is entry 14 of 41, and a
  one-byte ordinal is not searchable. `[hypothesis]`
- Of the 33,401 datafiles, 33,000 are not datablock-chunked (almost all of them the streamed-sound
  archives). Their raw bytes were still swept for every needle; they simply cannot contain an
  `ActionBlock`.
- Every needle hit outside `DataPC.forge -> Game Bootstrap` landed inside `SoundBao` audio payloads
  — the same false-positive class the dossier already records for hash sweeps. See
  `needle-hits.txt`.

## Files

| file | what |
| --- | --- |
| `actionblock-census.tsv` | all 2,464 `ActionBlock`s: archive, datafile, block index, id, size, name, id-reference count |
| `search-log.txt` | the full run log: per-archive totals, the control-A histogram, per-needle hit counts |
| `needle-hits.txt` | every target hit and a capped sample of control hits, with the containing datablock named |
| `text-id-sweep.txt` | the second pass, for ids written as ASCII text |
| `menu-handler-block-layout.txt` | all 40 menu-handler datablocks decoded to `{id, Magma file, screen name}` |
| `interface-manager-41-entries.txt` | the `InterfaceManager` registry table, resolved |
| `ab_search.py`, `textid_sweep.py`, `menu_layout.py` | the scripts that produced the above |

Reproduce (from the game folder; the scripts take the output directory as `argv[1]`):

```
gcc -O2 -shared -o lzo2a.dll lzo2a.c        # in dev-archive/tools/forge, once
python ab_search.py    <outdir>             # ~4 min, 9.28 GB
python textid_sweep.py <outdir>             # ~2 min
python menu_layout.py
```
