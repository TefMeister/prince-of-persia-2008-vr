# Research index

**Last `/gr` pass: 2026-09-02 (estate sweep) — CHECK-IN** (board OPEN block + INDEX; the dossier was not read in full)**.** Inbox empty. **Nothing new.** The `.forge` decoder and the hash search are static work that yesterday's re-ranked topic already scoped; no public source has appeared since that reads a behaviour or camera graph. Not searched.
_Previous: Last `/gr` pass: 2026-09-01 — CHECK-IN (inbox + INDEX in full + the re-ranked topic; the dossier was not read in full). Inbox drained (the `.forge` re-ranking). The `.forge` topic is promoted to ⭐ critical path a…_

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-01 | [`.forge` tooling reaches the datablocks, but nobody has read a graph](topics/2026-09-01-forge-tooling-reaches-datablocks-but-nobody-has-read-a-graph.md) | 🆕 new | **⭐ Critical path.** Answers both questions from the modding side with honest negatives — public `.forge` documentation covers the container only (no type IDs, no datablock schema; header magic is the literal `scimitar`), Elika reaches datablocks but interprets only textures/meshes/localization, and **AnvilToolkit's support list omits Prince of Persia entirely**. Then the way through: `CGST_DebugModeFPSCamera`'s **hash `0xA80488AB`** is a schema-free needle to search extracted datablocks with — with a mandatory positive control, since a bad extraction looks exactly like a real negative. |
| 2026-08-25 | [Middleware confirmed: DARE audio + Havok physics](topics/2026-08-25-middleware-confirmed-dare-audio-havok-physics.md) | ✅ incorporated | "Dare" resolved as Ubisoft's own cross-project audio system (also used in Splinter Cell, not Anvil-specific); Havok physics confirmed. Fills two open §2 blanks. |
| 2026-08-25 | [Cheat table camera check + debug-menu gap](topics/2026-08-25-cheat-table-camera-check-and-debug-menu-gap.md) | ✅ incorporated | Camera direction is memory-readable (per a Cheat Engine table) but no dedicated FOV/free-cam tool exists, unlike Mad Max. No public debug-menu/console unlock found either — both honest negative results, sets expectations for from-scratch work. |
| 2026-08-25 | [HelixMod 3D Vision fix — major camera prior art](topics/2026-08-25-helixmod-3d-vision-major-camera-prior-art.md) | 👀 reviewed | A twice-iterated (2012, 2016) HelixMod fix already solves skybox/lens-flare/UI-depth for this exact D3D9 game, and confirms separate cutscene-vs-gameplay convergence handling — the strongest camera/projection prior art found so far. Factored into ENGINE-DOSSIER.md §6/§8. |
| 2026-08-25 | [Engine identity: Scimitar/Anvil + AC1 prior art](topics/2026-08-25-engine-identity-scimitar-anvil-and-ac1-prior-art.md) | ✅ incorporated | Engine confirmed as the Scimitar engine (pre-2009 Anvil), sharing real codebase lineage with Assassin's Creed (2007) — opens AC1's modding scene (EaglePatch, Anvil engine hub) as adjacent prior art. Factored into ENGINE-DOSSIER.md §2. |
| 2026-08-25 | [D3D9 + StarForce DRM profile](topics/2026-08-25-dx9-starforce-drm-profile.md) | ✅ incorporated | Renderer confirmed D3D9. DRM is StarForce, not Denuvo — retail was famously DRM-free but digital/Steam likely isn't; StarForce 5.0 has known modern-Windows compatibility issues. No vorpX profile exists for this specific game (honest gap, unlike Mad Max). **Follow-up: the modding session directly checked the installed Steam build for StarForce (driver files, service, exe strings) and found none** — see ENGINE-DOSSIER.md §4; this build appears genuinely DRM-free. |
| 2026-08-25 | [Elika / .forge asset extraction tools](topics/2026-08-25-elika-forge-asset-extraction-tools.md) | ✅ incorporated | Dedicated extraction tooling ("Elika", Turfster's .forge tool) already exists for this exact game's archive format — a positive finding, unlike Mad Max's Apex-tools gap. **⭐ 2026-09-01: re-ranked from "not urgent" to the critical path** by the modding side — the character state machine turned out to be data-driven, so the answer to the debug-camera question is inside the archives. Followed up in the 2026-09-01 topic above. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
