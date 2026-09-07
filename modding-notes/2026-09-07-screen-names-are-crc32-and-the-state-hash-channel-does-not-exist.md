# 2026-09-07 — Screen names are CRC32, and the state-hash channel does not exist anywhere

`/pd`, dev PC. **The game was not launched, and nothing here has been run.**

Evidence: `dev-archive/recon/2026-09-07-magma-screen-hashes-and-menu-handler-classes/`.
This entry works the `[PD]` row queued on 2026-09-05, both halves of it.

---

## 1. The load-bearing result: the MGB does carry the screen names — hashed

2026-09-05 recorded that `MagmaCommon_MGB` "carries no `P_*` string in ASCII or UTF-16LE",
and concluded from that the item to `CGST_DebugMode` link "can only be in the UI file or the
C++ class". **The measurement was right and the reading of it was too narrow.** The names
are in the UI file. They are stored as **CRC32, little-endian, as a raw `u32`** — the same
hash function §6 of `FORMAT.md` already established for type names.

| screen | crc32 | Common | InGame | Pregame | Fonts | |
| --- | --- | --- | --- | --- | --- | --- |
| `P_PauseMenu` | `0xab726231` | 0 | **36** | 0 | 0 | positive control |
| `P_MainMenu` | `0x9da62dfb` | 0 | 0 | **36** | 0 | positive control |
| `P_Options` | `0x9ab9a8d7` | 0 | 0 | **36** | 0 | positive control |
| `P_PauseMenuDebug` | `0xba8c1f01` | **60** | 0 | 0 | 0 | target |
| `P_MainMenuDebug` | `0xd9c2ab89` | **24** | 0 | 0 | 0 | target |
| `P_CheatMenuDebug` | `0x1524767e` | **60** | 0 | 0 | 0 | target |
| `P_ZzzNotARealScreen` | `0xd5e51b33` | 0 | 0 | 0 | 0 | negative control |
| `P_PauseMenuDebugX` | `0xc00f8ac2` | 0 | 0 | 0 | 0 | negative control |
| `P_QuuxMenu` | `0xbe971180` | 0 | 0 | 0 | 0 | negative control |

`[verified-numerically 2026-09-07, n=9 probes, 3 positive + 3 negative controls]`

Two things make this more than a lucky grep. **Every screen's hash appears only in the MGB
its own handler datablock binds to** — a binding read independently from the datablock
bodies on 2026-09-04b, from the other side of the format. And the counts are **exact
multiples of 12**, which is the `MAGMA` section count each MGB carries; per section the
counts are perfectly flat (`5,5,5,…` / `2,2,2,…` / `3,3,3,…`).
`[verified-numerically 2026-09-07]`

Widget names are hashed the same way: `crc32("List") = 0xe4fa5726` occurs **168 times**
across the four MGBs, and is the name the menu-handler code itself looks up (§3).

## 2. What that does and does not buy — read this before building on it

**It does not enumerate the debug menus' items, and this entry does not claim to.**
Occurrence count is not item count: `P_PauseMenu`, a screen with many visible entries,
occurs 3× per section. These are *references to* a screen, not its contents. Reaching the
items needs the record graph decoded, which is not done.

Recorded so nobody re-derives it: the sections are **language/platform variants**. Only
`MagmaCommon_MGB` kept authoring-tool residue in its section padding, and it shows
`<LANGUAGE>` `CZE`/`FRE`/`GER`/`RUS` and `<PLATFORM>` `PC`/`XBOX360`. Twelve sections
against four observed language tags means the *count* is measured and the *interpretation*
is not. `[verified-numerically 2026-09-07]` for "12 sections"; `[inferred-static 2026-09-07]`
for "12 = language × platform variants".

Also recorded: the authoring format is **XML** (`<WIDGET>`, `<STAGE>`, `<POSITION>`,
`<LOCALIZEDPROPERTIES>`, `<AutonomousAreaInstance>`), surviving only as a few hundred bytes
of uninitialised buffer tail per section. Residue, not a parseable copy.

## 3. The other half: the menu-handler classes, out of decrypted code

`.text` is encrypted at rest — re-measured here rather than assumed: entropy **8.00**,
`.bind` present, entry point `0x011022ED` outside `.text`. `[measured 2026-09-07]`
Steamless v3.1.0.5 unpacks a **copy**, and the result reproduces the 2026-09-03 record on a
different machine: entry point **`0x00B076BD`**, entropy **8.00 → 6.61**, `CC` runs
**0 → 32,491**. `[measured 2026-09-07, n=1 machine, reproducing n=1 from 2026-09-03]`

The class descriptor in `.data` falls out:

```
+0x00 char*  className
+0x04 u32    CRC32 of the BASE class name   (all five: 0xd13edf15 = MagmaMenuHandler_m)
+0x08 u32    CRC32 of THIS class name       (== the datablock typeHash)
+0x0c u32    instance size
+0x48 void*  factory thunk in .text
```

| class | descriptor | size | factory | ctor | vtable |
| --- | --- | --- | --- | --- | --- |
| `DebugMenuHandler_m` | `0x00E73D60` | 0xA0 | `0x007123A0` | `0x0070D740` | **`0x00D5ECF0`** |
| `CheatMenuMagma_m` | `0x00E70160` | 0xA0 | `0x0070E120` | `0x0070C140` | **`0x00D5E040`** |
| `StartMenuDebug_m` | `0x00E7F208` | 0xA8 | `0x007B9CC0` | `0x007B5940` | **`0x00D67FB8`** |
| `MainPauseMenuHandler_m` | `0x00E5E1A0` | 0xA0 | `0x006A56A0` | `0x006A3630` | **`0x00D54478`** |

`crc32(className)` reproduces `+0x08` for all five classes tested, zero mismatches, and
three of those hashes were already read out of the **datablock** bodies on 2026-09-04b — so
the data-side and code-side type identities are now joined.
`[verified-numerically 2026-09-07, n=5]`

**And the answer to "read what its item handlers call" is: nothing debug-specific.** Every
32-bit immediate in the debug classes' class-specific vtable methods was resolved against a
CRC32 dictionary of 29,058 identifier strings from the unpacked exe. Exactly **two** name
hashes resolve across all of them: `0xe4fa5726` = **`List`**, in vtable slot 48 — *the same
slot with the same constant* as `MainPauseMenuHandler_m` — and `0x67a2c4c1` =
**`IExecutionPolicy`**, in slot 63 of `DebugMenuHandler_m` only, which is a generic engine
interface rather than a menu concept. Neither is a state name or an item name. The debug
handlers grab a widget called `List` and dispatch by index, exactly as the ordinary pause
menu does.
`[inferred-static 2026-09-07]` — inferred rather than verified because "no resolvable name
hash" is bounded by the dictionary, and a name that is not an identifier-shaped string in
the exe would be missed.

## 4. ⛔️ The negative that matters: states are not referenced by hash, anywhere

| needle | crc32 | `.text` decrypted | `.text` as shipped | all MGBs |
| --- | --- | --- | --- | --- |
| `CGST_DebugMode` | `0x861D663F` | **0** | 0 | **0** |
| `CGST_DebugModeFPSCamera` | `0xA80488AB` | **0** | 0 | **0** |
| `CGST_Idle` — positive control | `0x407DC47E` | **0** | 0 | **0** |
| `CGST_Ground` — positive control | `0x06F4ECF7` | **0** | 0 | **0** |
| `List` — positive control | `0xE4FA5726` | **9** | 0 | 168 |
| `DebugMenuHandler_m` — positive control | `0x5345255F` | **5** | 0 | 0 |

`[verified-numerically 2026-09-07]`

The method is demonstrably live — `List` and `DebugMenuHandler_m` are found in decrypted
`.text` and **zero times in the same byte range of the shipped file**, which is also the
most concrete demonstration yet of why every pre-2026-09-03 `.text` scan was void. And
`CGST_Idle` / `CGST_Ground` are states that unquestionably run every second of normal play,
so their absence is not "we searched the wrong place".

**So the hash route is closed on both sides at once.** This agrees with `FORMAT.md` §7,
which found data-side state references are by **ordinal**; ordinals are small integers and
are not searchable. Closing the hash route therefore opens nothing — it removes a way to
look, it does not hand over a better one.

## 5. What this means for the mod

The debug-menu route has now been narrowed three times — `ActionBlock`s ruled out
2026-09-05, handler datablocks shown to carry no behaviour field the same day, and now the
handler *classes* shown to carry no debug-specific name reference and the hash channel shown
not to exist. **The data route does not depend on any of this.** `CR_Debug_1stPerson`'s
state list is editable today, the repacker is built and validated, and that row is a
decision for the user rather than a question for the tooling.

## 6. What is NOT established

- The item lists of `P_PauseMenuDebug` / `P_MainMenuDebug` / `P_CheatMenuDebug`. Still open.
- Whether the debug menu can reach `CGST_DebugMode` at all. Nothing here says it can or cannot.
- The 12-section interpretation (§2).
- That item to state is by ordinal. That follows from §4 only by elimination. `[hypothesis]`

**The specific result that would show §1's derivation is wrong**, rather than a detail
needing tuning: a screen whose handler datablock names one MGB but whose CRC32 appears in a
*different* one. That would mean the hash coincidences are chance and the whole table is
noise. Four screens were checked and none did that.

## 7. One correction to the record

The 2026-09-05 `[PD]` row gives `DebugMenuHandler_m`'s class-name string as `0x0095b2fc`.
That is a **file offset**, not an address; the virtual address is **`0x00D5C0FC`**. Both
numbers are correct for what they are, but the row reads as a VA and would send a session
looking in `.text`. `[measured 2026-09-07]`
