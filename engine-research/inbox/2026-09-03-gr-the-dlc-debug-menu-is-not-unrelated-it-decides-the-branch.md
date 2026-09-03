# The DLC debug menu is NOT unrelated — it decides §6's open branch

**From:** `/gr` (2026-09-03, estate sweep)
Supersedes: ENGINE-DOSSIER.md §3, the sentence *"the only 'debug menu' hits elsewhere were an
unrelated Xbox 360 DLC-specific feature"* (2026-08-25)
**Topic:** [`external-research/topics/2026-09-03-the-debug-menu-is-a-pause-menu-entry-not-a-console.md`](../../external-research/topics/2026-09-03-the-debug-menu-is-a-pause-menu-entry-not-a-console.md)

## What I got wrong on 2026-08-25, and what it costs

On 2026-08-25 `/gr` found the reports of a debug menu in this game's Epilogue DLC and **dismissed
them as an unrelated console-DLC feature.** That dismissal is recorded in §3 and has been standing
ever since. It was wrong, and it was wrong in the expensive direction: §6 has since recorded the
entry into `CGST_DebugMode` as an open branch between *"a name-driven path"* and *"absent from the
shipping build"*, and this finding **settles that branch** — it had been sitting in our own
external-research the whole time, filed as noise.

## What the reports actually say

In the Epilogue DLC, scrolling down in the **pause menu** past the normal options exposes repeated
text entries; selecting the first opens a **"Menu Debug"** screen with options including turning the
corruption effects off. Players hit it by accident — the DLC's pause-menu list scrolls past its own
bounds. `[reported 2026-09-03]`

Two things follow, and neither depends on the DLC:

1. **A debug menu is shipped in this game's retail UI stack** — same engine, same menu system. So
   §6's second branch, *"absent from the shipping build"*, is the weaker one.
2. **Nobody typed anything.** It is a **menu entry reached by menu navigation**, not a console. And a
   name-driven UI route is precisely what leaves **no 32-bit immediate 188 or 189 in `.text`** —
   the state is named in data and resolved through the registry, never pushed as a literal by
   compiled code.

So §6's static negative — *"`.text` has no 32-bit immediate 188/189"* — is **not evidence of
absence**. It is the expected signature of the mechanism this finding points at. The search was
looking in the one place a data-driven menu route guarantees is empty.

## Suggested dossier changes

1. **§3**, replace the dismissal with: *"A debug menu is reachable from this game's own pause menu in
   at least one retail build — console players reached a shipped `Menu Debug` screen in the Epilogue
   DLC when the pause list scrolled past its bounds `[reported 2026-09-03]`. The PC release never
   got the Epilogue, so this is not a route to try on PC as-is; it establishes that the menu system
   carries debug entries, which is what makes §6's UI/data branch the live one."*
   Keep the rest of the line — the `DebugMenu`/`DebugMenuHandler_m` strings and `/noconsole` are
   unchanged and now read as corroboration rather than as isolated curiosities.
2. **§6's "NOT established" bullet**, add: *"The UI/data branch is now the favoured one — see §3. The
   ordinal-and-`.text` searches cannot see a name-driven menu route by construction, so their
   negatives carry no weight against it."*
3. **§11 (dead ends)**, if it lists the ordinal/immediate searches, annotate them as *"correct
   searches, wrong layer — a menu route leaves no literal"* rather than as evidence the feature is
   absent.

## The three static follow-ups this opens — all `[PD]`

The `.forge` reader already parses all 33,401 datafiles and resolves 201 of 202 type hashes.

1. **Census the menu classes** exactly as the camera classes were censused, and look for a debug
   entry among the pause-menu entries.
2. **Search for the state NAMES, not the ordinals or hashes.** A name-driven setter references the
   string `CGST_DebugMode` / `CGST_DebugModeFPSCamera`; the registry that maps those names to 188/189
   holds the strings too. This is the search the drop's own reasoning implies, and the hash needle
   displaced it.
3. **Read `GraphRuleBook` `Ingame_FreeCam` in full.** If a rule book can be entered directly, a
   state-ordinal switch may not be needed at all.

With a positive control on each, for the reason the 2026-09-02 drop documented better than I could.

## ⚠️ Confidence, stated plainly

Both source threads returned HTTP 403 to a direct fetch this pass and were read through search-result
summaries only, so the claim is `[reported]`, not verified. It is two independent community threads
saying the same thing, which is why it is worth acting on — but one confirming read in a human
browser would cost a minute and would upgrade it.
