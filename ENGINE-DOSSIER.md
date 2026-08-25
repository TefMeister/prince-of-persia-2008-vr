# Engine Dossier — Prince of Persia (2008) (Scimitar engine — pre-2009 name for Ubisoft's Anvil, shares codebase lineage with Assassin's Creed 2007)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. **The cleanest project in this portfolio's DRM/launcher terms so far: no Denuvo, no StarForce (checked specifically), no anti-cheat, no third-party launcher requirement found anywhere.** Real prior art exists: a twice-iterated HelixMod stereo-3D fix for this exact game, and dedicated `.forge` extraction tooling ("Elika"). · **VR-readiness verdict:** TBD on the actual camera/projection question, but no environmental blockers found (unlike Burnout Paradise's EA App wall) and no third-party-tool feasibility signal either (unlike Mad Max's vorpX precedent) — genuinely promising starting conditions, still fully unverified live.

## 1. Identity
- Game / build / version: Prince of Persia (2008), Ubisoft Montreal — the reboot, not the Sands of Time trilogy. Steam AppID 19980. The exe Steam actually launches is `PrinceOfPersia_Launcher.exe` (12.7 MB, in the install root) — its name is misleading, it's the real game binary, confirmed via the install's own registry key (`HKLM\SOFTWARE\Ubisoft\Prince of Persia\Executable` = this exact file). A second, genuinely-smaller `Launcher\Launcher.exe` (188 KB) also exists but is not what Steam runs.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Standard Steam release, no known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Scimitar engine, confirmed by literal strings (`AnvilScript`, `CustomAnvilBrush`, `startanvil`) plus external-research (2026-08-25).** "Scimitar" is the historically accurate name for this build specifically — it's the pre-2009 name for what was renamed **Anvil** starting with Assassin's Creed II (2009); this game predates that rename. Per Ubisoft producer Ben Mattes (contemporary press), Prince of Persia (2008) runs on "an adapted version of the engine developed internally... for Assassin's Creed" — i.e. **real, substantial shared codebase lineage with Assassin's Creed (2007)**, not just the same engine family in name. This opens Assassin's Creed's own modding scene (e.g. [EaglePatch](https://github.com/Sergeanur/EaglePatch), an open-source ASI patch for AC1: Director's Cut) as legitimate adjacent (same-engine, different-game) prior art — worth checking when engine/format questions come up that AC1's community may have already solved, while still independently verifying against this game's own binary (two years and studio changes separate the two builds). `Dare` also appears as a literal string, matching the shipped `DARE.INI` config file (audio-buffer/optimization settings) — likely an internal subsystem name, exact meaning not yet confirmed.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Bink** (`binkw32.dll`, video/cutscenes — same middleware as Mad Max). **EAX + DirectSound** (`EAX.DLL`, `DSOUND.dll`, `WINMM.dll`) for audio, with dedicated `DARE.INI` DS3D cache/voice-count tuning. No physics/animation middleware self-identified yet (not yet investigated).
- Distinctive file formats / build tags / symbol naming: **`.forge`** — large packed data archives (11 files, up to ~1.2 GB each: `DataPC.forge`, `DataPC_HC.forge`, `DataPC_lod.forge`, etc.) — this engine generation's archive format. **Tooling already exists (external-research, 2026-08-25): "Elika"** — a dedicated extraction tool built specifically for this game (named after its own companion character, mirroring AC1's equivalent tool "Animus") — plus a more generic **".forge extractor/replacer" by Turfster** (ModDB, "Assassin's Guild" community group, consistent with the shared Scimitar/AC1 lineage). A positive finding, unlike Mad Max's situation where the generic engine-family tooling explicitly didn't cover the target game — not urgent for the camera/VR work, but the starting point if asset-level work is ever needed.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`), standard MSVC section layout (`.text`/`.rdata`/`.data`/`.tls`/`.rsrc` — no unusual renamed sections, no giant opaque blob like Burnout Paradise's or Mad Max's Denuvo-shaped sections; consistent with the DRM finding below). 12.7 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed.** Static imports include `d3d9.dll` and `d3dx9_39.dll` (D3DX9 helper library, SDK version marker "_39" ≈ June 2010 SDK); literal string `Direct3DCreate9` present. **`Direct3DCreate9Ex` is NOT present** — this game uses plain (non-Ex) D3D9, worth remembering since Ex vs. non-Ex changes some behavior (e.g. windowed flip-model, `GetGPUThreadPriority`) relevant to injection/hooking design later.
- Developer console / cvar system present? how opened?: **A real console AND a real debug menu both appear to exist.** Strings found: `"- unable to open console device"`, `GetConsoleCP`/`GetConsoleMode`/`WriteConsoleA`/`WriteConsoleW`, `consoleout`, and critically a default command-line string embedded in the exe: `/world:POP0WORLD /fast /shadows:on /lightmode:normal /fardist:1500 /noconsole /bink:on /mission:pop0_root /startupmenu:on /localbigfile` — the presence of `/noconsole` strongly implies a console-enabling launch flag exists (untested: try launching without it, or with an explicit `/console`). Separately, `DebugMenu`/`DebugMenuHandler_m` strings confirm an actual developer debug menu class exists in the binary — how it's opened is unconfirmed, but this is the same category of find that unblocked Psychonauts' void investigation elsewhere in this portfolio (a dormant dev tool, not something to reverse-engineer from scratch).

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **Reconciled, 2026-08-25 — appears genuinely DRM-free, on two rounds of evidence.** Initial static pass found no Denuvo/SecuROM/StarForce/Uplay strings. External-research then flagged a real, specific reason to double-check: the 2008 **retail boxed** PC release was famously, publicly made DRM-free (widely covered contemporary press — Ubisoft removed disc-check protection entirely), but digital/downloadable versions weren't confirmed part of that move, and this console-generation's PC ports commonly carried **StarForce** (a kernel-driver-based DRM, architecturally very different from Denuvo — also flagged as having known compatibility problems on modern Windows independent of anti-piracy concerns). **Follow-up check on the actually-installed Steam build, specifically for StarForce**: no `*starforce*`/`*sfdrv*`/`*.sys`/`*protection*` files anywhere in the install directory, no StarForce Windows service installed, no StarForce-related strings anywhere in the exe (broadened search beyond the first pass). **Conclusion: this Steam release appears to have shipped DRM-free, consistent with the retail precedent** — not airtight certainty (no debugger has been attached live yet, unlike Mad Max where live testing was what actually settled the equivalent question), but two independent negative checks plus a real historical precedent make this well-supported.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block this time — genuinely different starting expectation than Mad Max going into its first live test.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy** — matches this portfolio's own precedent on Psychonauts (also D3D9, proxied directly rather than via a carrier DLL) more closely than the winmm-carrier pattern used on The Evil Within/Far Cry 2. Given no DRM found, a direct same-named proxy should be low-risk here. **No vorpX precedent exists for this specific game** (external-research, 2026-08-25) — vorpX's forums cover only the PS2-era trilogy and Sands of Time, with an explicit caveat that unsupported titles "might or might not hook." Unlike Mad Max, this project doesn't have that class of third-party feasibility signal yet; the HelixMod fix below is this project's actual evidence that D3D9-level hooking works against this exact binary.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: (D3D9 note: no unified cbuffer model — expect shader
  constant registers via `SetVertexShaderConstantF`/similar, not D3D11-style constant buffers;
  §7's template language below needs adapting accordingly once live investigation starts.)
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):
- **The single best prior art found for this project (external-research, 2026-08-25): a mature, twice-iterated HelixMod 3D Vision fix already exists for this exact game and renderer.** [2012 original](https://helixmod.blogspot.com/2012/03/prince-of-persia-2008-written-by-chiz.html) (by "Chiz") + [2016 update](https://helixmod.blogspot.com/2016/04/prince-of-persia-2008-updated.html) — the update specifically rebuilt to fix collateral damage the original caused (its skybox/lens-flare shader fixes had also broken unrelated combat effects), using a newer HelixMod version that distinguishes shader/texture *pairs* rather than blanket-matching. **Key structural finding: separate convergence presets for cutscenes vs. exploration gameplay** — concrete evidence to expect distinct camera/projection code paths for cinematics vs. normal play, not one shared path; this should directly shape how this section's live investigation is scoped (check both early, don't assume one covers the other). (Studied for scope/mechanism only, per policy — never copying its actual shader code.)

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):
- **Starter pass inventory, third-party-confirmed (external-research, 2026-08-25, from the HelixMod fix's own issue list — see §6):** skybox depth (needs correction for **both dark and sunny weather variants** — not a single static case), lens/sun-flare doubling (needs to respond correctly to convergence changes), UI rendered flat at screen depth (the 2016 update added adjustable 2D-to-3D conversion at a deliberately mild setting), background-landscape depth. A known residual issue even in the mature 2016 fix: brief flickering on some "magic effects" — worth expecting similar edge cases in a true-VR approach too.

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `/world:<name>` | selects the game world to load (e.g. `POP0WORLD`) | launch-arg, from the exe's own default command-line string |
| `/mission:<name>` | selects the starting mission (e.g. `pop0_root`) | same source |
| `/fast` | unconfirmed, likely skip-intro/fast-boot | same source |
| `/shadows:on\|off`, `/lightmode:normal`, `/fardist:<n>` | render quality/distance tuning | same source |
| `/noconsole` (implies a console-enabling counterpart exists, untested) | suppresses the console | same source — try omitting or an explicit `/console` |
| `/bink:on\|off` | toggle Bink video playback (cutscenes) | same source — useful to disable for faster iteration |
| `/startupmenu:on\|off` | toggle the startup menu | same source — `off` may allow skipping straight into gameplay |
| `/localbigfile` | unconfirmed, likely a local-vs-streamed `.forge` data flag | same source |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used): untested, but the exe's own embedded default command line (`/world:POP0WORLD /fast /shadows:on /lightmode:normal /fardist:1500 /noconsole /bink:on /mission:pop0_root /startupmenu:on /localbigfile`) is a strong starting template — likely usable close to as-is via Steam launch options or a direct exe launch with args.
- In-process input / camera drive method that worked: not yet investigated.
- Frame-capture method; where images land: not yet investigated.

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- **No vorpX (or equivalent live-VR-tool) precedent exists for this specific game** (external-research, 2026-08-25) — unlike Mad Max, there's no third-party confirmation that a full stereo/head-tracking conversion is achievable here, only the HelixMod 3D-Vision fix (a different, more limited technique) as evidence the renderer isn't unusually resistant to hooking.
- D3D9 (non-Ex) means this project's camera/projection work will look more like Psychonauts' (SetTransform/vertex-shader-constant based) than the constant-buffer-based D3D11 titles elsewhere in this portfolio — §6/§7's template language (written for D3D11) will need adapting once live investigation starts.
- No comfort/motion-sickness-specific risks identified yet (not a driving game, third-person action-platformer with acrobatics — camera behavior during wall-runs/ledge-grabs etc. may need particular VR-comfort attention, worth watching for once gameplay is seen).
