# A game-specific asset extraction tool ("Elika") and generic .forge tools already exist for this exact game

**Status:** 🆕 new · **Priority:** low-medium — not urgent for the camera/VR work, but closes off
guessing about asset formats and documents what's available for later, matching the pattern already
established on the Mad Max front (Gibbed.MadMax vs. the generic Apex tools).

## What was found

Prince of Persia (2008) packs its data in **`.forge`** archive files (already anticipated in this
project's own `claude-memory` notes prior to this research). Public tooling specific to this format
and this game already exists:

- **"Elika"** — a dedicated extraction tool for Prince of Persia 2008 specifically (named for the
  game's own companion character, mirroring how AC1's equivalent tool is named "Animus" after that
  game's lore) — used for pulling datafiles, textures, and 3D meshes out of the game's archives.
- **[".forge extractor/replacer" by Turfster](https://www.moddb.com/downloads/forge-extractorreplacer-by-turfster)**
  (ModDB) — a more generically-named tool for the same archive format, distributed within the
  "Assassin's Guild" ModDB community group — consistent with the confirmed shared Scimitar/Anvil
  engine lineage (companion topic) between this game and Assassin's Creed (2007), which very
  plausibly uses a related or identical archive format given they're the same engine generation.

This research pass did not get deep technical documentation of the `.forge` format's internal
structure (byte layout, compression, etc.) — only confirmation that dedicated, working extraction
tooling exists and is named specifically for this format/game, unlike the Mad Max front where the
generic engine-family tooling explicitly did *not* cover the target game.

## Why this matters

Not urgent for the camera/projection/VR-rendering work this project's early phases focus on, but
useful to have on record:
- If the mod ever needs to read or reference level/character/vehicle data, Elika (or the Turfster
  `.forge` tool) is the starting point, not something to reverse-engineer from scratch.
- Unlike Mad Max's situation, this project's asset-format prior art is a **positive** finding — a
  dedicated tool for this exact game already exists — worth remembering as a genuine asset if asset
  work becomes necessary later.

## Concrete next step

No immediate action needed. Revisit Elika/the Turfster `.forge` tool only if/when this project needs
to read or modify packaged game data directly.

## Sources

- https://www.moddb.com/downloads/forge-extractorreplacer-by-turfster
- https://www.moddb.com/groups/assassins-creed-fans/downloads/forge-extractorreplacer-by-turfster
- https://www.moddb.com/engines/scimitar
