# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and documentation of many people who came before us. None of
this would be possible without their work. We list every source we've drawn
on below — including work that helped only as inspiration — by name or
handle, as accurately as we could verify it.

## The game itself

This mod modifies, at runtime, the original **Prince of Persia** (2008) by
**Ubisoft Montreal**, published by **Ubisoft** (https://www.ubisoft.com). The
game, its engine, and all of its assets are theirs, and the game is the
entire reason this project exists. **No game files, code, or assets are
distributed in any of this project's repositories** — only code, notes, and
tools we wrote ourselves, plus third-party components whose licenses permit
redistribution (noted below).

## Prior art, tools, and research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| Helix Mod: Prince of Persia 2008 (2012 fix) | Chiz, Helix Mod community | https://helixmod.blogspot.com/2012/03/prince-of-persia-2008-written-by-chiz.html |
| Helix Mod: Prince of Persia 2008 (2016 updated fix) | Helix Mod community | https://helixmod.blogspot.com/2016/04/prince-of-persia-2008-updated.html |
| Anvil/Scimitar engine background & Assassin's Creed lineage reporting | VideoGamer.com, Ubisoft (Ben Mattes interview) | https://www.videogamer.com/news/prince-of-persia-based-on-assassins-creed-game-engine/ |
| EaglePatch (Assassin's Creed 1 & 2 patches) | Sergeanur | https://github.com/Sergeanur/EaglePatch |
| Anvil engine community hub | ModDB/IndieDB contributors | https://www.moddb.com/engines/scimitar |
| .forge extractor/replacer | Turfster | https://www.moddb.com/downloads/forge-extractorreplacer-by-turfster |
| PCGamingWiki (Prince of Persia 2008 technical notes) | PCGamingWiki community | https://www.pcgamingwiki.com/wiki/Prince_of_Persia_(2008) |
| MobyGames (technical/middleware specs) | MobyGames contributors | https://www.mobygames.com/game/38110/prince-of-persia/ |
| Prince of Persia (2008) Cheat Engine table | mul0 | https://fearlessrevolution.com/viewtopic.php?t=26099 |
| AnvilNext `.forge` container-format documentation (header magic `scimitar`, resource index and descriptions chunk) | GenuineAster / Mischa-Alff and the `broadside` project contributors | https://github.com/Mischa-Alff/broadside/wiki/AnvilNext-%60.forge%60-file-format |
| Elika (Prince of Persia 2008 `.forge` datafile/datablock/texture/mesh/localization tool) | Turfster | https://www.moddb.com/groups/assassins-creed-fans/downloads/forge-extractorreplacer-by-turfster |
| AnvilToolkit (`.forge` unpack/repack for the Assassin's Creed titles; its support list is what shows PoP 2008 is excluded) | AnvilToolkit authors and contributors | https://www.nexusmods.com/assassinscreed/mods/30 |
| ACExplorer (open-source `.forge` explorer, corroborating how far public format knowledge reaches) | gentlegiantJGC | https://github.com/gentlegiantJGC/ACExplorer |
| The Cutting Room Floor (documentation of the Assassin's Creed prototype's debug menu and Ghost Mode) | TCRF contributors | https://tcrf.net/Proto:Assassin%27s_Creed |
| "DLC Debug Menu" thread (the Epilogue pause-menu route into a shipped "Menu Debug" screen) | XboxAchievements forum members | https://www.xboxachievements.com/forum/topic/115001-dlc-debug-menu/ |
| "Debug menu/cheats in DLC" thread (independent report of the same pause-menu route) | Giant Bomb forum members | https://www.giantbomb.com/prince-of-persia/3030-20961/forums/debug-menucheats-in-dlc-233454/ |
| Wikipedia — Prince of Persia (2008 video game) (Epilogue DLC platform availability; Scimitar lineage) | Wikipedia contributors | https://en.wikipedia.org/wiki/Prince_of_Persia_(2008_video_game) |
| LZO (`lzo2a_d.ch` / `config2a.h`, GPL) — the decompressor our own `.forge` reader was transcribed from | Markus F.X.J. Oberhumer | http://www.oberhumer.com/opensource/lzo/ |

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
