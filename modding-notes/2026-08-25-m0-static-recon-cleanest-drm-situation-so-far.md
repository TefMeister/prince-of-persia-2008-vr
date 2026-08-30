# 2026-08-25 — First look: no DRM at all, and a real debug menu

Session type: static file analysis (no game launch).

## What we know for sure

- **The renderer is Direct3D 9** (plain, not the "Ex" variant) — the exe directly names
  `d3d9.dll`, `d3dx9_39.dll`, and `Direct3DCreate9`.
- **The engine is Anvil** — Ubisoft's own engine, the same lineage that later became famous
  through the Assassin's Creed series. This 2008 game is an early Anvil-era title.
- **No DRM found anywhere** — no Denuvo, no SecuROM, no StarForce, no Ubisoft
  Connect/Uplay launcher requirement. This is the cleanest result of any project in this
  portfolio so far — a real contrast with Burnout Paradise (which needed the EA App) and Mad
  Max (which has Denuvo, confirmed live via a blocked debugger attach). Nothing here predicts
  that kind of trouble this time, though it's only confirmed by live testing once that
  happens.
- **A real developer debug menu appears to exist** (`DebugMenu`/`DebugMenuHandler_m` classes
  in the binary), plus a console system (`/noconsole` implies a console-enabling flag exists
  too). This is the same category of find that unblocked Psychonauts' investigation elsewhere
  in this portfolio — a dormant dev tool built by the original developers, not something we'd
  have to build ourselves.
- **The exe's own embedded default command line reveals useful launch options**:
  `/world:POP0WORLD /mission:pop0_root /fast /noconsole /startupmenu:on` and others — a
  starting point for launching straight into a known scene later, without navigating menus by
  hand every time.

## What's next

A `d3d9.dll` proxy DLL (same pattern as this portfolio's Psychonauts project) is the natural
M0 injection foothold — plan is to build and live-test it the same way as Burnout
Paradise/Mad Max.

One honest gap: no public-research sweep has happened for this project yet, unlike Mad Max
and Burnout Paradise (both of which got real parallel research mid-session). Community prior
art here is currently unknown.

Full technical detail: `prince-of-persia-2008-vr-dev-archive`, `recon/2026-08-25-m0-static-recon/`.
