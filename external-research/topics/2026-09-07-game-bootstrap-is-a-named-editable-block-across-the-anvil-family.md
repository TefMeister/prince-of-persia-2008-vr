# "Game Bootstrap" is a named, routinely-edited block across the Anvil family — weak corroboration for the repacker route, not a MAGMA decode

**Status:** 🆕 new · **Priority:** low-medium — it does **not** decode `MagmaCommon_MGB`, and it must
not be read as if it does. What it does is put the `[USER]` repacker decision on slightly firmer
ground by showing the sibling community edits the same class of block, the same way.

## Why this was looked up

The board's `[PD]` row targets a specific block:

> "decode `MagmaCommon_MGB` (`DataPC.forge → Game Bootstrap` block 419, id `081b8052`,
> 1,338,945 bytes, `MAGMA` magic at +0x30) far enough to enumerate the items of `P_PauseMenuDebug` /
> `P_MainMenuDebug` / `P_CheatMenuDebug`"

The 2026-09-05 pass spent ~4 targeted searches on the file format and found nothing. This pass asked a
narrower question — not *"what is MAGMA"* but *"does the Anvil family treat 'Game Bootstrap' as a
thing people open and edit?"*

## The finding

**Yes, and by that name.** A public Assassin's Creed IV modding guide instructs readers to open
**`DataPC.forge → 51-Game Bootstrap Settings.data`** and replace it, as a routine step, alongside
edits to a `PlayerProgressionManager` block and per-character `VisualMaster` and `tag_rules` files
`[reported 2026-09-07]`.

Three things follow, all modest:

1. **"Game Bootstrap" is a persistent, named engine concept across the Anvil/Scimitar line**, not a
   Prince-of-Persia oddity — it is present and named in a 2013 title as it is in this 2008 one. That
   is mild evidence the block is *structural* rather than an incidental blob.
2. **The community edits it by whole-block export → edit → reimport**, which is **exactly the shape of
   the workflow this project has already built and validated**: `dev-archive/tools/forge/forge_write.py`,
   whose null-op self-test produced byte-identical output on three archives up to 752 MB. The `[USER]`
   row's route is the one the sibling community actually uses.
3. **The AC-side edits to that block are references and IDs** — ship identifiers, a progression-manager
   block reference — rather than opaque binary. That is faint evidence that a Game Bootstrap block is
   a table of references, which is the shape `P_PauseMenuDebug` / `P_MainMenuDebug` /
   `P_CheatMenuDebug` entries would need to be enumerable. `[hypothesis]`, and deliberately weak.

## ⚠️ What this is NOT — read this before quoting the above

- **It is not a MAGMA decode.** Nothing public describes the `MAGMA` structure at `+0x30`, and this
  pass did not change that.
- **The block numbering does not transfer.** AC4's is `51`; ours is `419`. Nothing suggests a shared
  index.
- **Prince of Persia is still excluded from the tooling**, exactly as this lane established on
  2026-09-01: AnvilToolkit's support list omits it. The AC4 guide names AC4, AC3 and Rogue as tested,
  and Unity / Syndicate / Origins / Odyssey as supported-but-untested. **PoP 2008 appears nowhere.**
- **The gap is five years and several engine revisions.** AC4 (2013) is far downstream of Scimitar-era
  PoP (2008). Structural continuity of a *name* is not continuity of a *format*.
- The guide itself is **deprecated and was removed from Steam Community for violating guidelines**;
  it is cited only for the block name and workflow shape it documents, both of which are corroborated
  by the tools it names.

## Method note, because it nearly went the other way

The `51-Game Bootstrap Settings.data` name first appeared in a **search-engine summary**. Under this
lane's own rule from earlier today — *a claim that appears only in summarizer prose is not
`[reported]`* — it was then **verified by fetching the page with an open-ended question** ("list every
file or datablock name this guide tells the reader to open or replace") rather than by asking whether
the page contained the string. It came back in the page's own content, with surrounding detail
(specific ship IDs, the progression-manager block, the tag_rules identifier) that a summarizer would
not invent. That is why it is tagged `[reported]` and not `[hypothesis]`.

## The concrete next step

None on its own — this does not unblock the `[PD]` row. Its only actionable content is a small
increase in confidence for the **`[USER]`** row: the export-edit-reimport route the repacker
implements is the same route the sibling community uses on the same class of block, which is a point
in favour of deploying it. The decision remains the user's.

If the `[PD]` row is picked up later, the one thread worth pulling is whether any AC-side tool exposes
a *schema* for a Game Bootstrap block rather than treating it as a replaceable blob. Nothing found so
far suggests one does.

## Sources and credit

- The deprecated public AC modding guide on Steam Community, cited for the block name and workflow:
  <https://steamcommunity.com/sharedfiles/filedetails/?id=2288998586>
- **Delutto** — the original `.forge` and data tools named in that guide.
- **AnvilToolkit** authors and contributors — the successor tooling, already credited in this lane.
- **Turfster** (Elika, `.forge` extractor/replacer) and **gentlegiantJGC** (ACExplorer) — already
  credited; re-checked this pass and unchanged.

Read online only; nothing downloaded, installed or copied.

## What came back empty

Two searches on the `MAGMA` magic and on `MagmaCommon` in an Anvil/Scimitar context returned **no
format documentation at all** `[checked 2026-09-07]` — the same result as 2026-09-05. The searches
were capable of positives: they returned the correct engine-identity pages (Scimitar as Anvil's 2006
codename, the PoP 2008 and AC engine wikis), the ZenHAX Anvil `.forge` thread, ACExplorer's *Forge
File System* wiki page and the ModDB tool listings — i.e. they reached the right corpus and it simply
does not contain a MAGMA description. Also noted in passing: `.magma_localization` files exist in the
AC series, so the `MAGMA` magic is a **family-wide container tag**, not a PoP-specific one — which
makes the absence of any public description of it more surprising, not less.
