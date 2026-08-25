# Camera direction is memory-readable (per a Cheat Engine table), but no dedicated FOV/free-cam tool or public debug-menu unlock exists — two honest, modest findings

**Status:** 🆕 new · **Priority:** low-medium — a calibration check for `ENGINE-DOSSIER.md` §6 and
§3's open "how is the console/debug menu opened" question. Follows the same pattern that turned up
a major lead on Mad Max (the AOB cheat table) and a direct answer on Mad Max again (MMConsole) — for
this game, the equivalent checks came back modest/negative, which is itself worth recording honestly
rather than skipped.

## What was checked

**Cheat Engine tables**: FearLess Cheat Engine hosts multiple community tables for Prince of Persia
(2008) (e.g. "+20 [Steam license] {mul0}," "+14 {fearlessrevolution}"). The mul0 table's own
published feature list includes a **"Camera Manager"** — but on inspection, this isn't a true
free-camera/FOV tool like the one found on the Mad Max front. It's narrower: hotkey `F` teleports the
player to the side the camera is currently facing (with adjustable distance), and `G` teleports back,
relative to camera direction. **Useful takeaway**: this confirms the camera's facing/direction vector
is at least readable in memory via ordinary Cheat Engine scanning (no unusual obfuscation defeating
that class of tool, consistent with this project's other "not unusually defended" findings) — but
**no dedicated FOV slider, free-camera mode, or camera-mode-switching function** was found published
for this game, unlike Mad Max's much more capable AOB table. Treat §6 as still needing to be solved
from scratch — this isn't a shortcut the way Mad Max's table was.

**Debug menu / console access**: `ENGINE-DOSSIER.md` §3 already found real static evidence of both
a console system (`"- unable to open console device"`, `WriteConsoleA/W`, a `/noconsole` launch flag
implying an enabling counterpart) and an actual `DebugMenu`/`DebugMenuHandler_m` class in the binary.
This research pass searched specifically for a publicly-documented way to open either on PC —
nothing found. The only "debug menu" references turned up were unrelated: an Xbox 360 DLC-specific
debug menu (a different, console-only, DLC-content feature, not the same thing), and general
cheat-code pages with no console/debug-menu instructions. **Unlike Mad Max (where MMConsole solved
this exact problem publicly), there is currently no known third-party tool that unlocks this game's
console or debug menu.**

## Why this matters

Sets honest expectations rather than assuming a shortcut exists: this project's camera/projection
investigation and its console/debug-menu access will both need to be solved through this project's
own live work (likely starting from the `/noconsole` flag lead already in §3 — try omitting it or an
explicit counterpart flag), not by finding and adapting a third party's already-published answer, the
way parts of the Mad Max front could.

## Concrete next step

No external shortcut found — proceed with `ENGINE-DOSSIER.md` §3's own plan (test launching without
`/noconsole`, or with a guessed explicit console-enabling flag) as the first live step for console/
debug-menu access, and treat §6 (camera/projection) as needing full from-scratch investigation, with
the HelixMod fix (companion topic, previous sweep) remaining this project's best actual lead there.

## Sources

- https://fearlessrevolution.com/viewtopic.php?t=26099
- https://mul0.com/trainer/prince-of-persia-2008-trainer/
