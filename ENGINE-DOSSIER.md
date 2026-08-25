# Engine Dossier — Prince of Persia (2008) (proprietary Ubisoft Montreal engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, no external research yet (flagged as a gap — first project this session with none). **The cleanest project in this portfolio's DRM/launcher terms so far: no Denuvo, no anti-cheat, no third-party launcher requirement found anywhere in the binary.** · **VR-readiness verdict:** TBD on the actual camera/projection question, but no environmental blockers found (unlike Burnout Paradise's EA App wall) — genuinely promising starting conditions.

## 1. Identity
- Game / build / version: Prince of Persia (2008), Ubisoft Montreal — the reboot, not the Sands of Time trilogy. Steam AppID 19980. The exe Steam actually launches is `PrinceOfPersia_Launcher.exe` (12.7 MB, in the install root) — its name is misleading, it's the real game binary, confirmed via the install's own registry key (`HKLM\SOFTWARE\Ubisoft\Prince of Persia\Executable` = this exact file). A second, genuinely-smaller `Launcher\Launcher.exe` (188 KB) also exists but is not what Steam runs.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Standard Steam release, no known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Anvil engine, confirmed by literal strings — `AnvilScript`, `CustomAnvilBrush`, `startanvil`.** This is the same engine family Ubisoft's Assassin's Creed series later became known for; this 2008 title is an early Anvil-era game. `Dare` also appears as a literal string, matching the shipped `DARE.INI` config file (audio-buffer/optimization settings) — likely an internal subsystem name, exact meaning not yet confirmed.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Bink** (`binkw32.dll`, video/cutscenes — same middleware as Mad Max). **EAX + DirectSound** (`EAX.DLL`, `DSOUND.dll`, `WINMM.dll`) for audio, with dedicated `DARE.INI` DS3D cache/voice-count tuning. No physics/animation middleware self-identified yet (not yet investigated).
- Distinctive file formats / build tags / symbol naming: **`.forge`** — large packed data archives (11 files, up to ~1.2 GB each: `DataPC.forge`, `DataPC_HC.forge`, `DataPC_lod.forge`, etc.) — Ubisoft's Anvil-era archive format. Not yet parsed or understood; no public tooling checked yet (unlike Mad Max, no external-research pass has happened for this project — see the gap noted at the top).

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`), standard MSVC section layout (`.text`/`.rdata`/`.data`/`.tls`/`.rsrc` — no unusual renamed sections, no giant opaque blob like Burnout Paradise's or Mad Max's Denuvo-shaped sections; consistent with the DRM finding below). 12.7 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed.** Static imports include `d3d9.dll` and `d3dx9_39.dll` (D3DX9 helper library, SDK version marker "_39" ≈ June 2010 SDK); literal string `Direct3DCreate9` present. **`Direct3DCreate9Ex` is NOT present** — this game uses plain (non-Ex) D3D9, worth remembering since Ex vs. non-Ex changes some behavior (e.g. windowed flip-model, `GetGPUThreadPriority`) relevant to injection/hooking design later.
- Developer console / cvar system present? how opened?: **A real console AND a real debug menu both appear to exist.** Strings found: `"- unable to open console device"`, `GetConsoleCP`/`GetConsoleMode`/`WriteConsoleA`/`WriteConsoleW`, `consoleout`, and critically a default command-line string embedded in the exe: `/world:POP0WORLD /fast /shadows:on /lightmode:normal /fardist:1500 /noconsole /bink:on /mission:pop0_root /startupmenu:on /localbigfile` — the presence of `/noconsole` strongly implies a console-enabling launch flag exists (untested: try launching without it, or with an explicit `/console`). Separately, `DebugMenu`/`DebugMenuHandler_m` strings confirm an actual developer debug menu class exists in the binary — how it's opened is unconfirmed, but this is the same category of find that unblocked Psychonauts' void investigation elsewhere in this portfolio (a dormant dev tool, not something to reverse-engineer from scratch).

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found at all — the cleanest result in this portfolio so far.** Zero hits for Denuvo, SecuROM, StarForce, Uplay/Ubisoft-Connect-launcher-requirement, or any activation/link2-style handoff string anywhere in the binary (the only "Activation"-named strings found are unrelated gameplay systems — trap/puzzle/zone activation logic, not DRM). Section structure is completely standard/unobfuscated (see §3), consistent with no anti-tamper wrapper being present. Not yet tested live (no debugger attach attempted), but nothing here predicts the Denuvo-style resistance seen on Burnout Paradise or Mad Max.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block this time.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy** — matches this portfolio's own precedent on Psychonauts (also D3D9, proxied directly rather than via a carrier DLL) more closely than the winmm-carrier pattern used on The Evil Within/Far Cry 2. Given zero DRM found, a direct same-named proxy should be low-risk here.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

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
- **No external-research pass has happened for this project yet** (unlike Mad Max/Burnout Paradise) — flagged as a real gap, not a risk about the game itself. Community prior art (camera/FOV mods, injection precedent, any existing stereo-3D work) is unknown until that sweep runs.
- D3D9 (non-Ex) means this project's camera/projection work will look more like Psychonauts' (SetTransform/vertex-shader-constant based) than the constant-buffer-based D3D11 titles elsewhere in this portfolio — §6/§7's template language (written for D3D11) will need adapting once live investigation starts.
- No comfort/motion-sickness-specific risks identified yet (not a driving game, third-person action-platformer with acrobatics — camera behavior during wall-runs/ledge-grabs etc. may need particular VR-comfort attention, worth watching for once gameplay is seen).
