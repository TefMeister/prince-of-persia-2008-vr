# The debug pause-menu screens are shipped, live-registered, in the PC's own data

`/pd`, home PC, no launch. Follows up `/gr`'s 2026-09-03 topic (console-only "Menu Debug" report,
Epilogue DLC) by checking the PC build's own `DataPC.forge → Game Bootstrap` data directly.

## What's new

- **Two debug-menu datablock types exist verbatim**, matching class names already known from the
  exe's own RTTI table (dossier §3): `StartMenuDebug_m` (block 31, id `0x81358011`) and
  `DebugMenuHandler_m` (block 40, id `0x96e48045`).
- **Each carries its own screen name as an embedded string**: `P_MainMenuDebug` and
  `P_PauseMenuDebug` respectively — the latter sitting right next to the normal `P_PauseMenu`
  (block 33, `MainPauseMenuHandler_m`).
- **★ The load-bearing part: both debug ids are directly registered in the game's own top-level
  `InterfaceManager 'Interface Manager'` datablock** (block 11, a 41-entry id table read at every
  launch) — the same registration pattern already confirmed for the CGST state registry and the
  CameraRule chain. `[verified-numerically 2026-09-04]` **This means the debug menus are not
  orphaned or stripped data: they are wired into the live interface system the PC build actually
  uses**, exactly like every ordinary menu screen. That is a materially stronger claim than the
  2026-09-03 topic's console-only report could support on its own.

## What is still NOT established

- **No direct reference from these menu blocks to `CGST_DebugMode` (state 188).** Checked the raw
  bytes of blocks 31, 32, 33 and 40 against every known camera/rule-book id (`CR_Debug_1stPerson`,
  `CR_Debug_GhostCam`, `FunkyCameras`, `CameraGraph`, `Ingame_FreeCam`, `MENU RuleBook`) — zero
  matches. Selecting the debug menu item, if that's the entry path, must act through an
  intermediate layer not yet located — most likely one of the estate's 2,464 `ActionBlock`
  datablocks (cutscene/UI action lists), which this session did not search.
- **Dead end closed:** chased `MENU RuleBook` (block 505) → `Menu InGame` / `Menu NavigationMap` →
  `FXRule`s literally named `Entering Menu` / `Leaving Menu`. That's the menu-open/close **visual
  FX** graph (referenced from `FXGraph 'FX Graph'`), unrelated to character state. Recorded so this
  isn't re-walked expecting it to reach `CGST_DebugMode`.

## Next static step (not attempted this session)

Search the `ActionBlock` census for one that references block 31 or 40's id (`0x81358011` /
`0x96e48045`) — that would be the action fired on selecting the debug menu item, and is the
remaining link to whatever sets state 188. This is a bigger search (2,464 candidates) than fit in
this session.

## Evidence

`dev-archive/recon/2026-09-04-debug-menu-datablocks/` — reproduce commands, hex dumps of all five
blocks discussed, and the registration grep output.
