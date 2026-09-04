# 2026-09-04 — the shipped debug pause-menu screens, located in PC data

`/pd` pass, home PC, **game never launched**. Follows up `/gr`'s 2026-09-03 topic
(`external-research/topics/2026-09-03-the-debug-menu-is-a-pause-menu-entry-not-a-console.md`),
which reported a console-only account of a "Menu Debug" screen. This pass checked the PC build's
own `DataPC.forge` data directly.

Reproduce (from the game install folder, tool path abbreviated to `forge.py`):

```
python forge.py types --match "Game Bootstrap" --exe PrinceOfPersia_Launcher.exe DataPC.forge \
  | grep -iE "menu|screen"
python forge.py blocks --match "Game Bootstrap" \
  --type "StartMenuDebug_m|DebugMenuHandler_m|MainPauseMenuHandler_m|PauseMenuHandler_m" \
  --exe PrinceOfPersia_Launcher.exe DataPC.forge
python forge.py grep --value 0x96e48045 --value 0x81358011 --match "Game Bootstrap" \
  --exe PrinceOfPersia_Launcher.exe DataPC.forge
```

## Findings

**`type-census.tsv` (already on disk from 2026-09-02) names two debug-menu handler types
verbatim** — `StartMenuDebug_m` (1 instance, 94 bytes) and `DebugMenuHandler_m` (1 instance,
91 bytes) — sitting alongside every other real menu handler (`MainPauseMenuHandler_m`,
`OptionsMenuHandler_m`, `SaveGameMenuHandler_m`, 27 more). Both class names match strings already
known from the exe's own RTTI table (dossier §3). `[inferred-static 2026-09-04, n=1 each]`

**The two blocks carry their own screen names as embedded strings**, read straight out of the
decompressed payload:

| block | type | id | embedded string |
| --- | --- | --- | --- |
| 31 | `StartMenuDebug_m` | `0x81358011` | `P_MainMenuDebug` |
| 40 | `DebugMenuHandler_m` | `0x96e48045` | `P_PauseMenuDebug` |
| 33 (for comparison) | `MainPauseMenuHandler_m` | `0x96e48031` | `P_PauseMenu` |

**Both debug-menu ids are directly registered in the game's own top-level UI registry.** `grep
--value 0x81358011 --value 0x96e48045` finds both inside `InterfaceManager 'Interface Manager'`
(block 11, id `0x00000808`) — a 41-entry id table read at every launch, the same registration
pattern already confirmed for the CGST state registry and the CameraRule chain. **This is the load-
bearing new fact: the debug menu screens are not orphaned or stripped data — they are wired into
the live interface system the PC build actually uses**, at the same registration layer as every
ordinary menu. `[verified-numerically 2026-09-04, n=2 ids found via independent grep]`

## What this does NOT establish

**No direct link from these menu blocks to the `CGST_DebugMode` character-graph state (188) was
found.** Checked the raw bytes of all four debug/pause-menu handler blocks (31, 32, 33, 40) against
every known camera/rule-book id (`CR_Debug_1stPerson`, `CR_Debug_GhostCam`, `FunkyCameras`,
`CameraGraph`, `Ingame_FreeCam`, `MENU RuleBook` and its two children) — zero matches. So selecting
the debug menu item, if that is how it is entered, must act through an intermediate layer not yet
located (see below), not by naming the camera rule chain directly.

**One side-branch chased and closed as a dead end:** `MENU RuleBook` (block 505, `GraphRuleBook`)
turned out to be part of a *different* system — it lists `Menu InGame` and `Menu NavigationMap`
(two more `GraphRuleBook`s), and `Menu InGame` in turn lists `FXRule`s named literally `Entering
Menu` and `Leaving Menu`. This is the menu-open/close **visual-FX** graph (referenced from an
`FXGraph 'FX Graph'` block), unrelated to character state. Recorded so nobody re-walks this chain
expecting it to reach `CGST_DebugMode`.

**The likely next static step, not attempted this session:** the wiring from "player selects the
debug menu item" to "character graph enters state 188" almost certainly runs through an
`ActionBlock` (2,464 estate-wide — cutscene/UI action lists) triggered by the menu selection, not a
direct id reference from the handler block itself. Locating the *specific* `ActionBlock` wired to
block 31/40 is a materially bigger search than this session's and is the right next `[PD]` item.

## Raw evidence

- `menu-type-census-excerpt.txt` — the `type-census.tsv` rows matching `menu|screen|ui` (regenerated
  view of already-committed data, for convenience)
- `debug-menu-blocks-hex.txt` — raw hex + extracted ASCII strings for blocks 11 (`InterfaceManager`),
  31 (`StartMenuDebug_m`), 32 (`PauseMenuHandler_m`), 33 (`MainPauseMenuHandler_m`), 40
  (`DebugMenuHandler_m`)
- `interface-manager-registration-grep.txt` — the `forge.py grep` output showing both debug ids
  registered inside block 11
