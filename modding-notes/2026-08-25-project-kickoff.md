# 2026-08-25 — Project kickoff

Project started today. Repos created per the standard six-repo layout; no
reverse engineering has happened yet — this is the "first look" phase.

## Game identity

**Prince of Persia (2008)**, developed by Ubisoft Montreal, published by
Ubisoft. Steam AppID **19980**. Confirmed via the installed folder's `.forge`
packed archives and `DARE.INI` file, and the `PrinceOfPersia_Launcher.exe`
launcher.

**This is deliberately disambiguated from the Sands of Time trilogy** (Sands
of Time / Warrior Within / The Two Thrones), which are different games on a
different engine. The repo prefix `prince-of-persia-2008-vr` exists
specifically so a future Sands of Time VR project (if one ever happens) gets
its own clean namespace.

Engine: a proprietary Ubisoft Montreal in-house engine. No public name for
it has been confirmed yet — that's an open question for the first real
research session, not something to guess at here.

## Next step

First engine-recon pass: confirm renderer API (D3D9/10/11), check for
launch-time DRM/anti-debug behaviour, and see whether the `.forge` archive
format has any existing public documentation or extraction tools (online
study only, per the standing research rules).
