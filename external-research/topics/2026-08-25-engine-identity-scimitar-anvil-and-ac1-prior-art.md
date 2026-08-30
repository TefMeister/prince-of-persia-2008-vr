# Engine identity confirmed: Scimitar (early Anvil) — shared with Assassin's Creed (2007), whose modding scene is a real prior-art source

**Status:** 🆕 new · **Priority:** high — resolves `ENGINE-DOSSIER.md` §2's completely open engine
question with a specific, named, well-documented engine, and opens a genuine adjacent prior-art
line (AC1 modding).

## What was found

This project's `ENGINE-DOSSIER.md` currently lists the engine as an "unconfirmed proprietary
Ubisoft Montreal engine." Public sources are actually unambiguous and specific here: Prince of
Persia (2008) runs on the **Scimitar engine** — the pre-2009 name for what later became known as
**Anvil**, Ubisoft Montreal's long-running proprietary engine family. Per Ubisoft's own producer
Ben Mattes (quoted in contemporary press) the 2008 Prince of Persia was built on "an adapted
version of the engine developed internally at Ubisoft for Assassin's Creed" — i.e. this game
shares real, substantial codebase lineage with **Assassin's Creed (2007)**, the engine's first
shipped title, not just a naming coincidence. (Shaun White Snowboarding, from the same era, is the
third confirmed Scimitar title.) The engine was renamed to Anvil starting with Assassin's Creed II
(2009) — this project's target predates that rename, so "Scimitar" is the historically accurate
name for the exact build in play, even though "Anvil" is the more commonly recognized modern name
for the lineage.

## Why the Assassin's Creed (2007) connection matters

AC1 has a real, still-active community reverse-engineering/modding scene that this project can draw
on as adjacent (same-engine, different-game) prior art:

- **[EaglePatch](https://github.com/Sergeanur/EaglePatch)** — an open-source ASI-plugin patch fixing
  numerous issues in AC1: Director's Cut, with public source on GitHub. Worth reading (not copying)
  for how it hooks/patches this engine generation's executable.
- **"Animus"** and **"Elika"** — dedicated data/texture/mesh extraction tools for AC1 and Prince of
  Persia 2008 respectively (see the companion asset-tooling topic) — named after each game's own
  lore, confirming these were built specifically for their respective titles rather than being one
  generic Scimitar-wide tool, though they target the same underlying archive technology.
- A **"Anvil engine" ModDB/IndieDB hub page** exists aggregating engine-wide community knowledge and
  downloads across multiple Scimitar/Anvil-era titles.

## Why this matters for this project

- Confirms this is a **real, historically well-documented engine with a genuine (if scattered)
  modding community**, not an obscure one-off — meaningfully better starting position than this
  project's dossier currently assumes.
- Any camera/projection/rendering-architecture insight gained from AC1's modding community, or from
  the same engine's later, better-documented titles (Assassin's Creed II onward, once renamed
  Anvil), is a legitimate, real lead to check — even though this project's binary (PoP2008's
  `.exe`) will still need its own independent verification, since two years and studio-internal
  changes separate PoP2008's Scimitar build from AC2's renamed Anvil build.

## Concrete next step

Record "Scimitar engine (pre-2009 Anvil), shares Assassin's Creed (2007) codebase lineage" directly
in `ENGINE-DOSSIER.md` §2. When engine/format questions come up that AC1's community has already
solved (e.g. archive format quirks, executable patching patterns), check EaglePatch and the Anvil
engine ModDB hub before assuming nothing transfers.

## Sources

- https://princeofpersia.fandom.com/wiki/Anvil_(game_engine)
- https://assassinscreed.fandom.com/wiki/Anvil_(game_engine)
- https://en.wikipedia.org/wiki/Scimitar_(game_engine)
- https://www.videogamer.com/news/prince-of-persia-based-on-assassins-creed-game-engine/
- https://github.com/Sergeanur/EaglePatch
- https://www.moddb.com/engines/scimitar
