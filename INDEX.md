# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [HelixMod 3D Vision fix — major camera prior art](topics/2026-08-25-helixmod-3d-vision-major-camera-prior-art.md) | 🆕 new | A twice-iterated (2012, 2016) HelixMod fix already solves skybox/lens-flare/UI-depth for this exact D3D9 game, and confirms separate cutscene-vs-gameplay convergence handling — the strongest camera/projection prior art found so far. |
| 2026-08-25 | [Engine identity: Scimitar/Anvil + AC1 prior art](topics/2026-08-25-engine-identity-scimitar-anvil-and-ac1-prior-art.md) | 🆕 new | Engine confirmed as the Scimitar engine (pre-2009 Anvil), sharing real codebase lineage with Assassin's Creed (2007) — opens AC1's modding scene (EaglePatch, Anvil engine hub) as adjacent prior art. |
| 2026-08-25 | [D3D9 + StarForce DRM profile](topics/2026-08-25-dx9-starforce-drm-profile.md) | 🆕 new | Renderer confirmed D3D9. DRM is StarForce, not Denuvo — retail was famously DRM-free but digital/Steam likely isn't; StarForce 5.0 has known modern-Windows compatibility issues. No vorpX profile exists for this specific game (honest gap, unlike Mad Max). |
| 2026-08-25 | [Elika / .forge asset extraction tools](topics/2026-08-25-elika-forge-asset-extraction-tools.md) | 🆕 new | Dedicated extraction tooling ("Elika", Turfster's .forge tool) already exists for this exact game's archive format — a positive finding, unlike Mad Max's Apex-tools gap. Not urgent, filed for later. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
