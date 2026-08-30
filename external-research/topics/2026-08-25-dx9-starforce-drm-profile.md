# Renderer confirmed D3D9; DRM is StarForce (not Denuvo) — a genuinely different risk profile, and no vorpX precedent

**Status:** 🆕 new · **Priority:** high — directly seeds `ENGINE-DOSSIER.md` §3/§4, and flags an
honest gap (no VR-tool precedent found, unlike Mad Max/Burnout Paradise) rather than overselling.

## Renderer

Confirmed **DirectX 9** — community binary analysis (referenced on PCGamingWiki's talk page) found
D3D9 API references and explicitly *no* D3D10 references anywhere in the executable. This is an
older renderer generation than either of this portfolio's other current fronts (Mad Max and Burnout
Paradise Remastered are both D3D11) — expect this project's own §6/§7 camera/projection work to look
more like classic fixed-function-adjacent D3D9 patterns (little/no unified shader constant-buffer
model — D3D9 uses shader constant registers rather than D3D11-style cbuffers) than like the other
two fronts' tooling assumptions. The companion HelixMod topic (this same sweep) independently
confirms D3D9 too, since HelixMod itself (as opposed to 3Dmigoto) is specifically the D3D9-era tool
in that tool family.

## DRM: StarForce, with a genuinely two-track history

- The **retail boxed PC version was famously, deliberately DRM-free** — a notable, PR-covered
  moment in 2008 where Ubisoft removed disc-check DRM from Prince of Persia's retail release
  entirely (contemporary press: HotHardware, bit-tech, Slashdot all covered it as a real
  DRM-relaxation story).
- **Digital/downloadable versions (and, per one source, console versions) were not part of that
  DRM-free move** — implying the Steam release plausibly still carries **StarForce** protection,
  the disc-check/driver-based DRM system common in that console generation's PC ports. This
  research pass could not get a definitive, dated confirmation of the *current* Steam build's exact
  DRM status (community discussion threads specific to this exact game's current state didn't
  surface); treat this as **likely StarForce present, not confirmed** — resolve for certain via this
  project's own static binary recon, same discipline already applied on the Mad Max front.
- **StarForce is architecturally very different from Denuvo** — historically it involved a
  kernel-level driver component (not just userspace anti-tamper), and PCGamingWiki-referenced
  community notes specifically flag that **StarForce 5.0 may not function correctly on modern
  Windows (8.1/10/11) without a manual driver update via `SFUPDATE`** — a compatibility problem for
  legitimate players, not just an anti-piracy hurdle. This is worth treating as its own distinct risk
  category in `ENGINE-DOSSIER.md` §4/§12: not primarily an anti-debug concern the way Denuvo is, but
  a potential launch/compatibility fragility concern specific to this older DRM generation, on
  modern OS versions.

## No vorpX precedent (an honest gap, unlike Mad Max)

Checked directly: **vorpX has no dedicated profile for Prince of Persia (2008)** — its forums only
cover the classic PS2-era trilogy (Prince of Persia 1/2/3) and Sands of Time specifically, with an
explicit "as always with unsupported games they might or might not hook" caveat for anything outside
that list. This is worth recording plainly rather than assuming feasibility by analogy with this
portfolio's other fronts — this project doesn't currently have the kind of third-party-tool
feasibility signal Mad Max (vorpX Geometry-3D + head tracking) or even Burnout Paradise (community
DLL-injection loader) already has. The companion HelixMod topic is the closest equivalent evidence
this project has that D3D9-level hooking works against this exact game at all.

## Concrete next step

When static recon begins, specifically check for StarForce signatures/driver dependencies (not
Denuvo-style exports) and treat any launch/compatibility fragility as potentially StarForce-related
before assuming it's this project's own injection code causing it. Don't assume vorpX-class
feasibility without independent evidence — the HelixMod precedent (companion topic) is this
project's actual evidence base for now.

## Sources

- https://www.pcgamingwiki.com/wiki/Prince_of_Persia_(2008)
- https://hothardware.com/news/prince-of-persia-2008-for-pc-is-drm-free
- https://games.slashdot.org/story/08/12/13/0517233/ubisoft-testing-pc-prince-of-persia-without-drm
- https://www.vorpx.com/forums/topic/prince-of-persia-1-2-3/
