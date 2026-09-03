# Engine Dossier — Prince of Persia (2008) (Scimitar engine — pre-2009 name for Ubisoft's Anvil, shares codebase lineage with Assassin's Creed 2007)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 complete AND live-verified (2026-08-25) — the game launches cleanly with the proxy `d3d9.dll` in place, loaded into a level with no issues, and the log confirms it worked exactly as intended (see §4). First project this session to work cleanly on the very first live attempt, no detours needed. **The cleanest project in this portfolio's DRM/launcher terms so far: no Denuvo, no StarForce (checked specifically), no anti-cheat, no third-party launcher requirement found anywhere.** Real prior art exists: a twice-iterated HelixMod stereo-3D fix for this exact game, and dedicated `.forge` extraction tooling ("Elika"). · **VR-readiness verdict:** TBD on the actual camera/projection question, but no environmental blockers found (unlike Burnout Paradise's EA App wall) and no third-party-tool feasibility signal either (unlike Mad Max's vorpX precedent) — genuinely promising starting conditions, still fully unverified live.

## 1. Identity
- Game / build / version: Prince of Persia (2008), Ubisoft Montreal — the reboot, not the Sands of Time trilogy. Steam AppID 19980. The exe Steam actually launches is `PrinceOfPersia_Launcher.exe` (12.7 MB, in the install root) — its name is misleading, it's the real game binary, confirmed via the install's own registry key (`HKLM\SOFTWARE\Ubisoft\Prince of Persia\Executable` = this exact file). A second, genuinely-smaller `Launcher\Launcher.exe` (188 KB) also exists but is not what Steam runs.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Standard Steam release, no known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Scimitar engine, confirmed by literal strings (`AnvilScript`, `CustomAnvilBrush`, `startanvil`) plus external-research (2026-08-25).** "Scimitar" is the historically accurate name for this build specifically — it's the pre-2009 name for what was renamed **Anvil** starting with Assassin's Creed II (2009); this game predates that rename. Per Ubisoft producer Ben Mattes (contemporary press), Prince of Persia (2008) runs on "an adapted version of the engine developed internally... for Assassin's Creed" — i.e. **real, substantial shared codebase lineage with Assassin's Creed (2007)**, not just the same engine family in name. This opens Assassin's Creed's own modding scene (e.g. [EaglePatch](https://github.com/Sergeanur/EaglePatch), an open-source ASI patch for AC1: Director's Cut) as legitimate adjacent (same-engine, different-game) prior art — worth checking when engine/format questions come up that AC1's community may have already solved, while still independently verifying against this game's own binary (two years and studio changes separate the two builds). `Dare` also appears as a literal string, matching the shipped `DARE.INI` config file (audio-buffer/optimization settings) — likely an internal subsystem name, exact meaning not yet confirmed.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Bink** (`binkw32.dll`, video/cutscenes — same middleware as Mad Max). **EAX + DirectSound** (`EAX.DLL`, `DSOUND.dll`, `WINMM.dll`) for audio, with dedicated `DARE.INI` DS3D cache/voice-count tuning. **`Dare` resolved (external-research, 2026-08-25): Ubisoft's own internal "Dare Audio" system — a cross-project audio technology/team, not Scimitar/Anvil-specific** (also used in Splinter Cell's separate Third Echelon engine, in place of OpenAL there). **Havok physics confirmed** (same middleware as Mad Max — extremely common for this console generation, not itself a meaningful coincidence, but now a confirmed fact rather than an open blank).
- Distinctive file formats / build tags / symbol naming: **`.forge`** — large packed data archives (11 files, up to ~1.2 GB each: `DataPC.forge`, `DataPC_HC.forge`, `DataPC_lod.forge`, etc.) — this engine generation's archive format. **Tooling already exists (external-research, 2026-08-25): "Elika"** — a dedicated extraction tool built specifically for this game (named after its own companion character, mirroring AC1's equivalent tool "Animus") — plus a more generic **".forge extractor/replacer" by Turfster** (ModDB, "Assassin's Guild" community group, consistent with the shared Scimitar/AC1 lineage). A positive finding, unlike Mad Max's situation where the generic engine-family tooling explicitly didn't cover the target game — not urgent for the camera/VR work, but the starting point if asset-level work is ever needed.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`), standard MSVC section layout (`.text`/`.rdata`/`.data`/`.tls`/`.rsrc` — no unusual renamed sections, no giant opaque blob like Burnout Paradise's or Mad Max's Denuvo-shaped sections; consistent with the DRM finding below). 12.7 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed.** Static imports include `d3d9.dll` and `d3dx9_39.dll` (D3DX9 helper library, SDK version marker "_39" ≈ June 2010 SDK); literal string `Direct3DCreate9` present. **`Direct3DCreate9Ex` is NOT present** — this game uses plain (non-Ex) D3D9, worth remembering since Ex vs. non-Ex changes some behavior (e.g. windowed flip-model, `GetGPUThreadPriority`) relevant to injection/hooking design later.
- Developer console / cvar system present? how opened?: **A real console AND a real debug menu both appear to exist.** Strings found: `"- unable to open console device"`, `GetConsoleCP`/`GetConsoleMode`/`WriteConsoleA`/`WriteConsoleW`, `consoleout`, and critically a default command-line string embedded in the exe: `/world:POP0WORLD /fast /shadows:on /lightmode:normal /fardist:1500 /noconsole /bink:on /mission:pop0_root /startupmenu:on /localbigfile` — the presence of `/noconsole` strongly implies a console-enabling launch flag exists (untested: try launching without it, or with an explicit `/console`). Separately, `DebugMenu`/`DebugMenuHandler_m` strings confirm an actual developer debug menu class exists in the binary — how it's opened is unconfirmed, but this is the same category of find that unblocked Psychonauts' void investigation elsewhere in this portfolio (a dormant dev tool, not something to reverse-engineer from scratch). **⚠️ CORRECTED 2026-09-03 (`/gr`, superseding this line's 2026-08-25 dismissal): a debug menu is reachable from this game's own pause menu in at least one retail build.** Console players reached a shipped **`Menu Debug`** screen in the Epilogue DLC when the pause list scrolled past its own bounds, with options including turning the corruption effects off `[reported 2026-09-03]`. The PC release never got the Epilogue, so **this is not a route to try on PC as-is** — what it establishes is that **the menu system carries debug entries**, which makes §6's UI/data branch the live one. The earlier text read: *no publicly-documented unlock method found for either … the only "debug menu" hits elsewhere were an unrelated Xbox 360 DLC-specific feature.* That dismissal was wrong, and wrong in the expensive direction — it sat in our own external-research filed as noise while §6 recorded the entry path as an open branch. The `DebugMenu`/`DebugMenuHandler_m` strings and `/noconsole` are unchanged and now read as corroboration rather than curiosities. ⚠️ Both source threads returned HTTP 403 to a direct fetch and were read through search summaries only, so this is `[reported]`, not verified; one read in a human browser would upgrade it.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **Reconciled, 2026-08-25 — appears genuinely DRM-free, on two rounds of evidence.** Initial static pass found no Denuvo/SecuROM/StarForce/Uplay strings. External-research then flagged a real, specific reason to double-check: the 2008 **retail boxed** PC release was famously, publicly made DRM-free (widely covered contemporary press — Ubisoft removed disc-check protection entirely), but digital/downloadable versions weren't confirmed part of that move, and this console-generation's PC ports commonly carried **StarForce** (a kernel-driver-based DRM, architecturally very different from Denuvo — also flagged as having known compatibility problems on modern Windows independent of anti-piracy concerns). **Follow-up check on the actually-installed Steam build, specifically for StarForce**: no `*starforce*`/`*sfdrv*`/`*.sys`/`*protection*` files anywhere in the install directory, no StarForce Windows service installed, no StarForce-related strings anywhere in the exe (broadened search beyond the first pass). **Conclusion: this Steam release appears to have shipped DRM-free, consistent with the retail precedent** — not airtight certainty (no debugger has been attached live yet, unlike Mad Max where live testing was what actually settled the equivalent question), but two independent negative checks plus a real historical precedent make this well-supported.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block this time — genuinely different starting expectation than Mad Max going into its first live test.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy** — matches this portfolio's own precedent on Psychonauts (also D3D9, proxied directly rather than via a carrier DLL) more closely than the winmm-carrier pattern used on The Evil Within/Far Cry 2. Given no DRM found, a direct same-named proxy should be low-risk here. **✅ LIVE-VERIFIED, first attempt, zero issues (2026-08-25):** deployed `staging/prince-of-persia-2008-vr/proxy-d3d9/`'s `d3d9.dll` and launched normally — the game reached the main menu and a real level with no problems. `pop2008_vr_proxy_log.txt` confirms: proxy loaded, real system `d3d9.dll` resolved correctly, `Direct3DCreate9` called once with `SDKVersion=0x20` (the standard `D3D_SDK_VERSION` constant), returned a valid non-null `IDirect3D9*`, clean unload on close. Matches the static "no DRM found" prediction — no EA-App-style detour, no Denuvo-style resistance, worked exactly as expected. **Next injection-side step, whenever resumed:** extend logging to device creation (`IDirect3D9::CreateDevice`) to see the actual backbuffer format/resolution/window handle — the natural M1 step, mirroring the other two fronts.

**No vorpX precedent exists for this specific game** (external-research, 2026-08-25) — vorpX's forums cover only the PS2-era trilogy and Sands of Time, with an explicit caveat that unsupported titles "might or might not hook." Unlike Mad Max, this project doesn't have that class of third-party feasibility signal yet; the HelixMod fix below is this project's actual evidence that D3D9-level hooking works against this exact binary.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ✅ `.forge` IS DECODED, THE CAMERA SYSTEM IS DATA, AND THE DEBUG FPS CAMERA IS AUTHORED AND SHIPPED (2026-09-02, `/pd`, no launch)

**Supersedes the two 2026-09-01 subsections below on method** (the hash-needle plan and "one
container decoder would unblock both"); their *destination* stood. Full write-up:
`modding-notes/2026-09-02-forge-decoded-the-debug-fps-camera-is-authored-data.md`; layout:
`dev-archive/tools/forge/FORMAT.md`; tool: `dev-archive/tools/forge/forge.py` (+ `lzo2a.c`).

- **Reader:** parses all 33,401 datafiles in the 20 archives with every field cross-checked, 0
  problems. Payloads are chunked **LZO2A** (the exe names its compressor enum `LZO1X_1 / LZO1X_999 /
  LZO2A / LZX`; chunk type 2); the transcribed decoder reproduces every block to the exact size and
  input — 7.90 GB across the 14 non-sound archives. Decompressed streams are typed, named
  **datablocks** whose `typeHash` is **CRC32 of the class name**, the same function the state
  registry uses; 201 of 202 types resolve. Elika was not needed. `[verified-numerically 2026-09-02]`
- **The camera system is data — the 2026-09-01 `[hypothesis]` is now fact:** 876 `CameraRule`, 277
  `PopFixedCamera`, 119 `PopFreeRoamingCamera`, 968 `TemporalCameraTransition`, 2,631
  `GraphRuleBook` (`Ingame_FreeCam`, `Fight_Cameras`, …), one `CameraGraph`, one
  `CameraTransitionManager`, mostly in `DataPC.forge → Game Bootstrap`. Owning this camera can run
  through data. `[verified-numerically 2026-09-02]`
- **States are referenced in data by ORDINAL, not hash.** The positive control (`CGST_Idle`,
  `CGST_Walk`, `CGST_Ground` by CRC32) hit only inside audio blocks — so the hash needle is
  `[disproved 2026-09-02]` and any null on `0xA80488AB` is meaningless. The real reference is
  `PopCharacterGraphStateDescription` = `u32 3; u32 state[3]`, sentinel **309 = `CGST_Any`**.
- **The debug first-person camera is authored:** `CameraRule "CR_Debug_1stPerson"` is conditioned on
  (**188 `CGST_DebugMode`, 189 `CGST_DebugModeFPSCamera`**, 309); `"CR_Debug_GhostCam"` on (188, 309,
  309); one unnamed level-local rule in `LR4_TowerExterior_LU` on (188, 188, 309); all other 7,800+
  state descriptions estate-wide never name 188 or 189. Its chain — `TemporalCameraTransition
  "FPSCamera_Transition"` / `"DebugMode_Transition"`, `PopMarketingCamera "CAM FPS"`,
  `PopGhostCamera "CAM Ghost POP"` — is all present. **`CGST_DebugModeFPSCamera` did not outlive its
  data.** `[verified-numerically 2026-09-02]`
- **NOT established — how the Prince enters `CGST_DebugMode`.** No datablock *transitions* into
  188/189; `.text` has no 32-bit immediate 188/189. Either a name-driven path (console / debug menu
  resolving the name through the registry — the exe's default command line carries `/noconsole`) or
  stripped. `[hypothesis]` The deciding static step: find the registry-descriptor (`0x00E53094`)
  walker that does name → ordinal and enumerate its callers.
- **Mod-shaped consequence:** rules select cameras by state, so rewriting `CR_Debug_1stPerson`'s
  list to (309, 309, 309) with a raised priority would make "CAM FPS" live in normal play with no
  code patch. Needs a repacker; raw blocks are legal (no compressor needed) but the per-block
  `u32 checksum` is unidentified (not CRC32/Adler/CRC-32C/FNV/djb2/sum) and may be verified.

### ✅ THE SHADER PACK IS DECODED AND §6 IS ANSWERED (2026-09-03, `/pd`, no launch) — the block below was a correct measurement with a WRONG conclusion

**`ekshaderspccompress.bin` is the SAME LZO2A container as `.forge`.** The magic
`33 AA FB 57 99 FA 04 10` sits at offset **5**, behind a five-byte preamble. The only structural
difference is that there is **no block table** — sizes are inline per block, each header carrying a
leading flag byte:

```
u8[5] preamble f5 9f 37 a8 02 | u8[8] magic | u16 ver=1 | u8 type=2 (LZO2A)
u16 0x8000 | u16 0x0000        (.forge has 0x8000 in that last field)
then per block: u8 flag(=1) ; u32 compressed ; u32 uncompressed ; u32 checksum ; data
```

`[verified-numerically 2026-09-03, n=1361 blocks]` — **1,361 blocks, ZERO decompression failures,
the file consumed exactly**, 9,784,709 → 44,578,719 bytes (4.56×), yielding **17,464 `CTAB`** and
**0 `DXBC`**. Tool: `dev-archive/tools/forge/ekshaderspc.py` (reuses `forge.py`'s LZO2A; output
byte-identical to the ad-hoc decode that found the format).

**§6's answer, from 17,270 parsed constant tables** (8,700 `vs_3_0`, 8,570 `ps_3_0`):

| constant | class | registers | shaders |
| --- | --- | --- | --- |
| **`g_WorldViewProj`** | `MATRIX_ROWS` | **`vs c0 ×4`** (6,292) · **`c128 ×4`** (2,016) · `c8` (96) · `c12` (24) | **8,428** |
| `g_World` | `MATRIX_ROWS` | `vs c4 ×4` · `c132 ×4` | 7,992 |
| `g_WorldView` | `MATRIX_ROWS` | `vs c4 ×3` · `c132 ×3` | 688 |
| `g_ViewerPosition` | `VECTOR` | `ps c10`/`c7`/`c13` | 6,417 |
| `g_WorldToLightProj` | `MATRIX_ROWS` | `ps c10 ×3` · `c3 ×3` | 2,588 |
| `g_Bones` | `MATRIX_ROWS` | **`vs c0 ×128`** | 2,016 |

**⚠️ The `c0` ⇄ `c128` split is the skinning palette**, exactly: all 2,016 shaders with the matrix at
`c128` carry `g_Bones` at `c0..c127`, and **none of the 6,292 at `c0` has any large array**.
`[inferred-static 2026-09-03, n=8428]` **A proxy must resolve the register per shader** — a fixed
`c0` corrupts 2,016 shaders. Same displacement `alan-wake-vr` has (192 registers there).

**Convention established two ways**, because metadata alone nearly misled on another project the
same day: the CTAB class says `MATRIX_ROWS`, and the bytecode agrees — the simplest shader carrying
it does `dp4 o0.x, c0, r0` / `dp4 o0.y, c1, r0` / `dp4 o0.z, c2, r0` / `dp4 o0.w, c3, r0`, i.e.
**registers are ROWS**, column-vector convention. `[inferred-static 2026-09-03, two independent
reads]` (`alice-madness-returns-vr` is `MATRIX_COLUMNS` and needs a *transposed* implementation of
the identical formula; this game is on `alan-wake-vr`'s side of that line.)

**Consequence: `g_WorldViewProj` is FUSED**, so the per-eye edit is the clip-space form
`row0 += S·row3 ; row0.w -= S·C` — which is `alan-wake-vr`'s `aw_stereo_apply_fused_clip`, written
and verified 2026-09-03, and it ports here unchanged.

⚠️ **Open, and specific to this game:** there is **no standalone projection constant**, so `p00`
cannot be recovered the way it is elsewhere — and the `|row0.xyz|` trick fails on a fused
`World→Clip` whenever the object has scale. Where `p00` comes from here is a real unanswered
question. Also unanswered: which draws are the camera's rather than the light's
(`g_WorldToLightProj` shows a shadow path exists). Write-up:
`modding-notes/2026-09-03-the-shader-pack-is-the-same-lzo2a-container-and-section-6-is-answered.md`;
evidence in `dev-archive/recon/2026-09-03-shaderpack-decoded/`.

<details>
<summary>The superseded 2026-09-01 block, kept because the measurements are still true and the
reasoning failure is worth seeing (click to expand)</summary>

### ⛔️ [SUPERSEDED 2026-09-03] The shipped shader pack is LZ-compressed — the CTAB route does not work here (2026-09-01, `/pd`)

**The game was not launched.** Tried the technique that settled `alice-madness-returns-vr` the same
day — read constant names and register indices straight out of the shipped compiled shaders — and it
**fails on this game**, for a reason worth recording so nobody spends the afternoon on it twice.

`ekshaderspccompress.bin` (9.3 MB, install root) is this game's shader pack, and it does contain D3D9
shaders: the literal bytes `CTAB` occur **830 times**, far above chance for a 4-byte pattern in 9.3 MB,
and `DXBC` occurs **zero** times (so it is Direct3D 9 bytecode, not D3D10+ — consistent with the rest
of this dossier). `[inferred-static 2026-09-01]`

**But not one of the 830 parses.** Reading the CTAB header at each hit gives nonsense — constant
counts in the billions, offsets past the end of the file. The reason is visible in the surviving
strings: constant names come out **shredded by inserted bytes** —

```
ViewPro*j    ViewPrToj    ViewPProj    Vi@ewProj    UVMatrixJ1    onMatrix
```

Those stray characters mid-word are LZ match/literal tokens breaking up the literal stream. The file
name says `compress` and it means it. So: **fragments of the constant vocabulary leak through
(`ViewProj…`, `…Matrix`, `WorldView`, `UVMatrix`, `LightProj`), but no register index is recoverable**,
because the numeric fields are exactly what the compressor encodes away. `[inferred-static 2026-09-01]`

**What this does and does not tell us.** It confirms the game's shaders use a
`WorldViewProjection`-family constant vocabulary — nothing more. It says nothing about which register
holds it, which is the question §6 actually asks.

**Next step for this section, and the choice is now explicit:** either decode the `ekshaderspc`
container (or the `.forge` archives) far enough to decompress one shader, or get the registers at
runtime from the proxy. Given the proxy already loads cleanly (below), the runtime route is likely
cheaper — but it needs a launch, and the static route does not.

**This converges with the other open thread.** Earlier the same day this project filed an inbox drop
saying **`.forge` tooling is now critical path** for the `CGST_DebugModeFPSCamera` question (ordinal
189, nothing in the code dispatching it). The shader pack is a second, independent reason to want a
container decoder: **one piece of tooling would unblock both the debug-camera question and the whole
of §6.** If anything on this project deserves static effort, it is that decoder.

*(That last paragraph called it right — and the decoder, written for `.forge` on 2026-09-02,
turned out to decode this file too the next day. What the block above got wrong was only the
inference that the compression made the pack unreadable.)*

</details>

### 🎯 The `.forge` route has a plan now: the state HASH is a schema-free needle (`/gr`, folded 2026-09-01)

The two questions this project filed came back **negative**: no public `.forge` work has ever touched
a camera or character graph, and the best format documentation (the `broadside` wiki) covers the
**container only** — no compression scheme, no type IDs, no datablock schema. Prince of Persia is
absent from the AC-focused tooling scene entirely. `[reported 2026-09-01]` **So building schema
knowledge from public sources is not possible.**

**But the schema is not needed.** `Elika v0.85` extracts and replaces datablocks, and the registry
already decoded gives the needle: **`CGST_DebugModeFPSCamera`, ordinal 189, hash `0xA80488AB`.** A
data-driven state machine must reference its states by *something*, and the executable has told us
both of the engine's own encodings. Plan:

1. **Elika → extract datablocks** (raw bytes; no interpretation needed).
2. **Search every datablock for `0xA80488AB` in both byte orders.** A 32-bit hash is a strong needle;
   a hit is almost certainly real, and its containing file **is** the character graph.
3. Reverse-engineer **one record in one already-localised file** — not a format.
4. **Do NOT search on the ordinal.** `189` as a four-byte integer (`BD 00 00 00`) occurs everywhere by
   chance; use it only to confirm a hit the hash already found.

**⚠️ Run a positive control first — the negative here is the dangerous one.** Take a state that
unquestionably runs in normal play, take its hash from the same registry, and confirm **that** hash is
found in the extracted set. If the control is not found either, a null result on `0xA80488AB` proves
nothing about the debug camera — it proves the extraction or the search was wrong. A hash stored
transformed, or a graph in a file type Elika does not extract cleanly, looks **exactly** like a real
negative.

If the control hits and the target does not, that is itself valuable: the state is registered but
present in no authored graph, and §6 should return to the D3D9 route rather than spend more time on
data archaeology.

**The same test extends the `Camera*` class hypothesis** — if those 152 class names also carry hashes,
an identical search locates the camera graph, which would make the *data* route rather than the D3D9
shader-constant route the way to own this game's camera. `[hypothesis]`, but now with a stated first
step.

**✅ Free confirmation, verified on this install:** `.forge` archives begin with the literal ASCII
identifier **`scimitar`** at offset 0 — checked on `DataPC.forge`, `DataPC_Default.forge` and
`DataPC_RC.forge`, all three byte-identical for the first 16 bytes.
`[inferred-static 2026-09-01, n=3 files]` An independent confirmation of §2's engine identification,
readable off the front of any archive.

### Confirmed the same day, for free: this game creates a plain D3D9 device

`pop2008_vr_proxy_log.txt`, still sitting in the install folder from the 2026-08-25 live test, records
`Direct3DCreate9` (not `…Ex`) called once with `SDKVersion=0x20`, returning a valid `IDirect3D9*`.
Same conclusion as `enslaved-vr`, and it carries the same consequence for any future compositor
submission path — see that project's §9 for the D3D9-vs-D3D9Ex bridge problem and the
`D3DPOOL_MANAGED` trap that comes with upgrading a device. The log has been rescued into
`dev-archive/recon/` (it existed only in the game folder). `[verified-live 2026-08-25, n=1]`

- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: (D3D9 note: no unified cbuffer model — expect shader
  constant registers via `SetVertexShaderConstantF`/similar, not D3D11-style constant buffers;
  §7's template language below needs adapting accordingly once live investigation starts.)
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):
- **Honest negative check (external-research, 2026-08-25): no dedicated FOV/free-camera tool exists, unlike Mad Max.** A Cheat Engine table (FearLess forums, "mul0") advertises a "Camera Manager" feature, but it's narrower than it sounds — hotkeys teleport the player relative to camera-facing direction, not a true free-cam/FOV slider. Useful takeaway anyway: confirms the camera's facing/direction vector is at least memory-readable via ordinary CE scanning (no unusual obfuscation), consistent with this project's other "not unusually defended" findings — but this is not a shortcut for §6 the way Mad Max's AOB table was. Treat this section as needing full from-scratch investigation.
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
- **⚠️ Reading the ordinal/immediate searches as evidence of ABSENCE — correct searches, wrong layer (2026-09-03).** `.text` carries no 32-bit immediate 188/189 for `CGST_DebugMode`, and that was taken as a point against the feature being reachable. **A name-driven menu route leaves no literal by construction** — the state is named in data and resolved through the registry, so the search was looking in the one place such a route guarantees is empty. The negatives are real and carry **no weight** against the UI/data branch (§3, §6). Search for the state NAMES in the `.forge` data instead.
- **Searching `.forge` data for a `CGST_*` state by its CRC32 hash** (`/gr` plan, 2026-09-01) — states are stored as **ordinals**; the three positive-control hashes hit only audio bytes. `[disproved 2026-09-02]`
- **Reading register indices out of `ekshaderspccompress.bin`** — the pack is LZ-compressed; 830 `CTAB`s, none parse. The `.forge` decoder's LZO2A code may apply to it (same engine, untested). `[inferred-static 2026-09-01]`
- **Scanning `.text` for a state-machine dispatch on ordinal 189** — the machine is data-driven; no dispatch exists, so "no reference" meant nothing (2026-09-01).
- **Elika / Turfster tooling as a prerequisite** — never needed; the container took one session to decode from the archives themselves (2026-09-02).

## 12. Open risks toward the North Star
- **No vorpX (or equivalent live-VR-tool) precedent exists for this specific game** (external-research, 2026-08-25) — unlike Mad Max, there's no third-party confirmation that a full stereo/head-tracking conversion is achievable here, only the HelixMod 3D-Vision fix (a different, more limited technique) as evidence the renderer isn't unusually resistant to hooking.
- D3D9 (non-Ex) means this project's camera/projection work will look more like Psychonauts' (SetTransform/vertex-shader-constant based) than the constant-buffer-based D3D11 titles elsewhere in this portfolio — §6/§7's template language (written for D3D11) will need adapting once live investigation starts.
- No comfort/motion-sickness-specific risks identified yet (not a driving game, third-person action-platformer with acrobatics — camera behavior during wall-runs/ledge-grabs etc. may need particular VR-comfort attention, worth watching for once gameplay is seen).
