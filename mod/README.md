# Prince of Persia (2008) VR

A VR conversion mod for **Prince of Persia (2008)** — the Ubisoft Montreal
reboot (Steam AppID 19980), not the Sands of Time trilogy. Goal: real stereo
rendering and 6DOF head tracking, with motion-controlled combat and traversal
as a stretch target once the core is solid.

> **Status: just starting out — repos created, no code written yet, nothing
> playable released.** This folder holds releases only; watch it if
> you want to know the moment there is something to try.

## What this will be

The Prince of Persia (2008) engine is a proprietary Ubisoft Montreal
in-house engine (its public name, if any, is not yet confirmed — engine
research has not started). This mod's approach — injection method, renderer
API, and patch points — will be worked out from scratch via reverse
engineering, and documented as we go. The playable mod is almost the
by-product; the real goal is the knowledge gained on the way there, written
down and shared so anyone can do the same for any game — see the
[engine dossier](../engine-research/)
and the cross-engine
[flat-to-VR library](https://github.com/TefMeister/flat-to-vr-cross-engine-research).

## What you will need

- Your own legitimate copy of **Prince of Persia (2008)** (this mod contains
  **no** game files).
- A PC VR headset (target runtime TBD as engine research progresses).

## The folders for Prince of Persia (2008) VR

Everything for this game lives in one repository, one folder per job — so you
always know where to look. You are in **`mod/`**.

| Folder | What lives here |
| --- | --- |
| **`mod/`** ← you are here | The mod itself — VR renderer/injection code, once it exists. |
| [`dev-archive/`](../dev-archive/) | Full development history — snapshots, probes, dead ends, raw recon. |
| [`modding-notes/`](../modding-notes/) | Readable field notes / progress ledger. |
| [staging/prince-of-persia-2008-vr](https://github.com/TefMeister/staging/tree/main/prince-of-persia-2008-vr) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| [`engine-research/`](../engine-research/) | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [`external-research/`](../external-research/) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Credits, scope, and legality

Non-commercial fan project; requires an owned copy; redistributes no original
assets. We credit everyone whose work this builds on — see
[`CREDITS.md`](CREDITS.md) — and we honour correction/removal requests from
rights holders promptly.

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
