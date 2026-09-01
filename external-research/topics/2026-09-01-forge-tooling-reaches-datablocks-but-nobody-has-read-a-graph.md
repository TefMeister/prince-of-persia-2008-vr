# `.forge` tooling reaches the datablocks but nobody public has ever read a graph — and our own registry makes that not matter

**Status:** 🆕 new · **Priority:** ⭐ high — this is now the critical-path lead, re-ranked at the
modding side's request, and the answer turns a format-reverse-engineering project into a byte search.

## The two questions asked

From `inbox/2026-09-01-mod-forge-tooling-is-now-critical-path.md`:

> whether the community's Scimitar/`.forge` work has ever touched the *camera graph* or *character
> graph* specifically (as opposed to meshes and textures), and whether Assassin's Creed 1 tooling —
> same engine lineage, far more attention — transfers to this build.

Short answers: **no**, and **no**. Both negatives are worth having, and the second half of this topic
is why neither one blocks the work.

## Q1 — public `.forge` knowledge stops at assets. All of it.

There are two tiers of public work and neither reaches behaviour data.

**The container format** is documented — the best public write-up is the `broadside` project wiki's
AnvilNext `.forge` page `[reported 2026-09-01]`. Useful details from it:

- The file header begins with the literal identifier **`scimitar`** — a free, zero-risk confirmation
  of engine identity straight off the front of any archive, and independent corroboration of
  `ENGINE-DOSSIER.md` §2's Scimitar finding.
- Structure is header → resource index (pointers, sizes, and a descriptions chunk carrying timestamp,
  filename and linked-list indices) → resource data.

And then it stops. **It documents the container and nothing inside it**: no compression scheme, no
type IDs, no resource-type table, no datablock schema. The write-up explicitly ends its analysis at
the resource boundary. Nothing public tells you what *kind* of thing a given resource is beyond its
filename.

**The extraction tools** go one level further but interpret only assets. **Elika v0.85** (Turfster —
the same author as the generic `.forge` extractor/replacer) does, for this exact game
`[reported 2026-09-01]`:

| Elika can | Elika cannot |
| --- | --- |
| extract & replace **datafiles** from archives | tell you what a datablock *means* |
| extract & replace **datablocks** from datafiles | parse any behaviour, state or graph structure |
| extract & replace **textures** | — |
| extract *"most files marked 3D mesh"* to OBJ (+ pre-flipped TGA) | *most*, not all — some mesh types are unsupported |
| extract & replace **localization** files | — |

The wider Assassin's Creed scene is the same shape at larger scale: textures, meshes, and — as one
description of the AC-side work puts it — *"Cell DataBlock files contain the data of how the
individual models are pieced together"*, i.e. **geometry assembly**, not behaviour. Nobody has
published a reading of a character graph, a camera graph, or any state machine from this format, in
this engine generation or any later one.

**So the honest verdict: the format knowledge you would need does not exist in public, and building
it is a real project.**

## Q2 — AC1's tooling does not transfer

**AnvilToolkit** is the modern, actively-maintained toolkit for this family, and it unpacks and
repacks `.forge`. Its published support list is `[reported 2026-09-01]`:

> AC1, AC2, ACB, Revelations, AC3, AC3R, Black Flag, Rogue, Unity, Syndicate

**Prince of Persia (2008) is not on it.** The Anvil scene's gravity is entirely on the Assassin's
Creed titles; the one Ubisoft game in the family that is *not* an Assassin's Creed game gets left out
even though it is the same engine.

What *does* transfer is the older, author-specific lineage: Turfster wrote both the generic `.forge`
extractor/replacer used across AC1/AC2 **and** Elika for this game specifically. That is the tool to
reach for, and this project's earlier topic already had it — the re-ranking, not the identification,
is what changed today.

## ⭐ Why none of that blocks the actual question

The modding side's static work handed this project something the whole public scene never had.

`/pd` decoded a **313-record registry at `0x00E521E8`** of
`{const char *name; int32 ordinal; uint32 nameHash}`, in which **`CGST_DebugModeFPSCamera` is ordinal
189 with hash `0xA80488AB`**, and `CGST_DebugMode` is 188. Nothing in `.text` references either.

A data-driven state machine has to name its states *somehow*, and the executable has just told us the
two encodings the engine itself uses: **a 32-bit hash and a small ordinal.** So the question

> is `CGST_DebugModeFPSCamera` reachable, and from where?

does **not** require understanding the datablock schema. It requires **searching extracted datablock
bytes for a 4-byte value.** Elika supplies exactly the primitive needed — *extract datablocks from
datafiles* — and the search after that is a grep over binary, schema-free.

**Concretely:**

1. Extract datablocks with Elika. No interpretation needed; the raw bytes are the deliverable.
2. Search every extracted datablock for **`0xA80488AB`**, in both byte orders. A 32-bit hash is a
   strong needle — a false positive is roughly a one-in-four-billion coincidence per position, so a
   hit is almost certainly a real reference and its containing file is the character graph.
3. Only then, and only in the file that hit, look at the surrounding structure. You are reverse-
   engineering **one record in one file you have already localised**, not a format.
4. The ordinal `189` (`BD 00 00 00`) is a **weak** needle on its own — a four-byte integer with that
   value will occur everywhere by chance. Use it only to confirm a hit the hash already found, never
   to search with.

**⚠️ Run a positive control before believing any negative.** Pick a state that is unquestionably used
in normal play, take its hash from the same registry, and confirm that hash *is* found in the
extracted set. If the control is not found either, the search proved nothing about
`CGST_DebugModeFPSCamera` — it proved the extraction or the search was wrong. (A hash may be stored
transformed, or the graph may live in a file type Elika does not extract cleanly; both look exactly
like a real negative.)

The same trick applies to the 152 `Camera*` class names, if they also carry hashes: if camera
behaviour is authored as data — `CameraGraph`, `CameraTemplate`, `CameraRule`,
`CameraRuleGraphClip`, `CameraTransitionSpecification` are the vocabulary of authoring, not of code
— then a hash search finds the camera graph the same way, and **the route to owning this game's
camera runs through data rather than through patching D3D9 shader constants.** That remains
`[hypothesis]`, exactly as the modding side filed it, but it is now a *testable* one with a stated
first step.

## Sibling prior art, for context rather than for use

A **prototype build of Assassin's Creed (2007)** that surfaced publicly in January 2023 is documented
as having **debug features enabled**: a Debug Menu opened with START from the main menu, and a
**"Ghost Mode"** that amounts to noclip `[reported 2026-09-01]`. So debug camera and noclip states
were genuinely authored in this engine generation, and shipping builds had the *entry points*
removed — which is precisely the shape our registry shows (the names survive, nothing calls them).

Confidence caveat, stated because the estate's rules require it: **the direct page fetch failed with
HTTP 403**, so this rests on a search-engine summary of The Cutting Room Floor's prototype page, not
on a read of the page itself. It is context, not evidence, and nothing should be planned on it. No
prototype build was sought, downloaded or examined, and none should be.

## Concrete next steps, in order

1. **Elika → extract datablocks.** Online tool, run locally against our own legitimately-owned game
   files; nothing is redistributed.
2. **Hash search for `0xA80488AB`, both byte orders, with a positive control.**
3. If it hits: read the one record. If the control hits and the target does not, that is a real,
   valuable negative — the debug FPS camera state is registered but not present in any authored
   graph, and §6 should go back to the D3D9 route without further data archaeology.
4. Independently and cheaply: confirm the archives begin with the literal `scimitar` identifier.

## Sources

- https://github.com/Mischa-Alff/broadside/wiki/AnvilNext-%60.forge%60-file-format
- https://www.moddb.com/downloads/forge-extractorreplacer-by-turfster
- https://www.moddb.com/groups/assassins-creed-fans/downloads/forge-extractorreplacer-by-turfster
- https://www.nexusmods.com/assassinscreed/mods/30
- https://github.com/gentlegiantJGC/ACExplorer
- https://tcrf.net/Proto:Assassin%27s_Creed (fetch returned HTTP 403; search-summary only)
