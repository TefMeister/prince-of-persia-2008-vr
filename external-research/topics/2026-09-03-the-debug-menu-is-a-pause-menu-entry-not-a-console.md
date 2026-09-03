# The debug menu is reached through the pause menu, not a console — which is why `.text` has no 188/189

**Date:** 2026-09-03 · **Status:** 🆕 new · **Answers:** the open question at the end of
`external-research/inbox/2026-09-02-mod-forge-hash-needle-disproved-string-route-worked.md`

## The question this answers

The modding side wrote its own `.forge` reader, parsed all 33,401 datafiles, and found that the
debug first-person camera really is authored in shipped PC data — `DataPC.forge → Game Bootstrap`
holds `CameraRule "CR_Debug_1stPerson"` conditioned on states 188 (`CGST_DebugMode`) and **189
(`CGST_DebugModeFPSCamera`)**, plus `CR_Debug_GhostCam`, two transitions, `PopMarketingCamera
"CAM FPS"` and `PopGhostCamera "CAM Ghost POP"`. `[verified-numerically 2026-09-02]`

What it could not find is the way **in**:

> What puts the Prince **into** `CGST_DebugMode`. No datablock outside the two camera rules
> references ordinal 188/189, and `.text` holds no 32-bit immediate 188 or 189 in push/mov/cmp
> forms — so the entry is either a name-driven path (console / debug menu resolving `CGST_DebugMode`
> through the registry by string) or absent from the shipping build. Any public mention of a Prince
> of Persia (2008) PC console, debug menu key, or `/console`-style switch (the exe's default command
> line carries `/noconsole`) would be worth a line.

## What was found — and it is the first of those two branches, not the second

**There is a debug menu, it is a real entry in the game's own pause menu, and players reached it by
accident.** In the game's *Epilogue* DLC, scrolling down in the pause menu past the normal options
exposes repeated text entries; selecting the first reveals a **"Menu Debug"** screen carrying, among
other things, options for **turning the corruption effects off**. It was reported by console players
(Xbox 360 / PS3) as a bug in the DLC's pause-menu implementation, not as a cheat — the menu was
shipped and the list bounds were wrong. `[reported 2026-09-03]`

That is a small finding with a large consequence for this project, because it decides between the
drop's two branches:

- **Not "absent from the shipping build".** A debug menu exists in the shipped UI stack of at least
  one retail build of this game, on the same engine and the same menu system.
- **Not a console either.** Nobody reaching it typed anything. It is a **menu item in the pause-menu
  list** — a UI/data path, exactly the kind of route that leaves **no 32-bit immediate 188 or 189 in
  `.text`**, because the state is named in data and resolved through the registry, never pushed as a
  literal by compiled code.

So the static negative the modding side recorded is not evidence of absence. It is what a
data-driven menu route looks like from the code side, and the search was looking in the one place
this mechanism guarantees is empty.

## ⚠️ The honest caveats — three of them, and they matter

1. **The report is about the Epilogue DLC, and the PC version never received it.** The Epilogue was
   released for Xbox 360 and PS3 only. So this does **not** say "scroll down in your PC pause menu
   and you will find it".
2. **What it does say is that the menu system carries debug entries at all**, and the PC data
   independently proves the *camera* half of the debug path is shipped on PC —
   `CR_Debug_1stPerson` and `CGST_DebugModeFPSCamera` are in `DataPC.forge`, measured on our own
   files. Two halves of the same feature, one confirmed on PC, one confirmed to exist in the menu
   system on console.
3. **The overflow is the reason it was visible, not the reason it exists.** A pause-menu list that
   scrolls past its own bounds is a DLC bug; the entries it scrolled *into* were already there. On
   PC the equivalent entries may be present but unreachable, present but bounded correctly, or
   stripped. Only our own data can settle which — and now we know what to look for.

## What this makes worth doing, and it is all static

The drop searched for the entry point in `.text` and in datablocks referencing ordinal 188/189.
Neither is where a menu route lives. The three targets this reframing opens are all inside the
archives already parsed:

1. **The menu/UI datablocks.** The reader parses all 33,401 datafiles and resolves 201 of 202 type
   hashes against the exe's identifier strings. Enumerate the **menu-related types** the same way
   the camera types were enumerated, and look for a debug entry among the pause-menu entries. The
   camera census (876 `CameraRule`, 968 `TemporalCameraTransition`, 2,631 `GraphRuleBook`, …) is the
   template; run it over the menu classes.
2. **The registry itself.** The states are referenced by **ordinal**, and 188/189 are their ordinals
   in a registry that maps names to indices. Whatever holds that registry also holds the **strings**
   `CGST_DebugMode` / `CGST_DebugModeFPSCamera` — and a *name*-driven setter would reference the
   string, not the number. Search the decompressed blocks and the exe's identifier strings for the
   names rather than the ordinals. This is the search the drop's own reasoning implies and the hash
   needle prevented.
3. **`GraphRuleBook`, including `Ingame_FreeCam`.** The census already found one by that name. A
   rule book that can put the game into a free camera is worth reading in full before hunting for a
   switch that flips a state ordinal — the switch may be unnecessary if a rule book can be entered
   directly.

None of this needs the game running. **All three stay `[PD]`.**

## What is still genuinely negative

No public source describes a **PC console** for this game, a **debug-menu key**, or a
`/console`-style command-line switch, and none appeared this pass either. The exe's default command
line carrying `/noconsole` remains suggestive and unexplained — a `/noconsole` default implies a
console the shipping configuration disables — but nothing public documents what removing it does.
That specific negative now stands at two independent passes (2026-08-25 and 2026-09-03) and should
be treated as settled unless someone goes looking in the binary rather than on the web.

The 2026-08-25 finding that no dedicated FOV/free-cam tool exists for this game also still stands.
Community camera work on this title is Cheat Engine tables and trainers — memory-poking a camera
that is already running, which confirms the camera is memory-reachable but tells us nothing about
entering debug state.

## Sources

- ["DLC Debug Menu"](https://www.xboxachievements.com/forum/topic/115001-dlc-debug-menu/) —
  XboxAchievements forum thread reporting the pause-menu route in the Epilogue DLC and the
  corruption-toggle options it exposes.
- ["Debug menu/cheats in DLC"](https://www.giantbomb.com/prince-of-persia/3030-20961/forums/debug-menucheats-in-dlc-233454/) —
  Giant Bomb forum thread on the same finding.
- [Prince of Persia (2008 video game)](https://en.wikipedia.org/wiki/Prince_of_Persia_(2008_video_game))
  — Wikipedia, for the Epilogue DLC's platform availability (Xbox 360 / PS3) and the Scimitar engine
  lineage.

Both forum threads were reachable only through search-result summaries this pass; the sites returned
HTTP 403 to a direct fetch. The claim is tagged `[reported]` accordingly and would be worth one
confirming read by a human browser before anything is built on it.

## The concrete next step

Run the existing `.forge` reader's type census over the **menu** classes, and search the
decompressed blocks for the literal strings `CGST_DebugMode` and `CGST_DebugModeFPSCamera` rather
than their ordinals or CRC32 hashes. With a positive control, as ever — the last search failed
silently for want of one, and the drop's own account of that is the best argument for it.
