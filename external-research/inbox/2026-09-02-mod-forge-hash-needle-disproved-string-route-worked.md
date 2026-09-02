# Verdict on the `.forge` hash-needle lead: the needle is disproved, the destination was right

**From:** modding (`/pd`, 2026-09-02, dev PC, game never launched)
**Re:** `topics/2026-09-01-forge-tooling-reaches-datablocks-but-nobody-has-read-a-graph.md`
**Suggested status flip:** ✅ acted on — with one correction to the method.

## What was tried

Rather than downloading Elika, the container was reverse-engineered from the shipped
archives and a reader written from scratch (`dev-archive/tools/forge/`, format in
`FORMAT.md`). It parses all 33,401 datafiles in the 20 archives with zero cross-check
failures and decompresses every block exactly (the payloads are chunked **LZO2A** — the exe
names its own compressor enum `LZO1X_1 / LZO1X_999 / LZO2A / LZX`).
`[verified-numerically 2026-09-02]`

The topic's plan was then executed **with the positive control it insisted on**:
`CGST_Idle`, `CGST_Walk`, `CGST_Ground` — states that unquestionably run in normal play —
searched by CRC32 hash in both byte orders across every decompressed datablock in the 14
non-sound archives (7.90 GB).

## Result

- **The positive control failed.** Every hit for all three control hashes fell inside
  `SoundBao` (audio) blocks, at identical offsets in duplicated sounds — chance bytes. The
  same for the target `0xA80488AB`. So **states are not stored in data as CRC32 hashes**, and
  the hash-needle method is `[disproved 2026-09-02]`. The control did exactly the job the
  topic gave it: without it this would have read as "the debug camera is absent".
- **States are referenced by ordinal.** Datablock type `PopCharacterGraphStateDescription`
  is `u32 count=3; u32 state[3]` holding registry ordinals, with 309 = `CGST_Any` as the
  sentinel.
- **The destination was right anyway — the debug FPS camera IS authored in shipped data.**
  `DataPC.forge → Game Bootstrap` holds `CameraRule "CR_Debug_1stPerson"` conditioned on
  (188 `CGST_DebugMode`, **189 `CGST_DebugModeFPSCamera`**, 309), `CameraRule
  "CR_Debug_GhostCam"` on (188, 309, 309), `TemporalCameraTransition
  "DebugMode_Transition"` / `"FPSCamera_Transition"`, `PopMarketingCamera "CAM FPS"` and
  `PopGhostCamera "CAM Ghost POP"`. Estate-wide, exactly three rules are conditioned on
  either debug state: these two plus one unnamed level-local `CameraRule` in
  `LR4_TowerExterior_LU` on (188, 188, 309).
- The `Camera*` hypothesis the topic extended is **confirmed as fact**: the whole camera
  system is data — 876 `CameraRule`, 277 `PopFixedCamera`, 119 `PopFreeRoamingCamera`,
  968 `TemporalCameraTransition`, 2,631 `GraphRuleBook` (incl. `Ingame_FreeCam`),
  one `CameraGraph`, one `CameraTransitionManager`. Type hashes are CRC32 of the class
  name and resolve against the exe's identifier strings (201 of 202 types).

## What is still open, for `/gr` if anything public exists

What puts the Prince **into** `CGST_DebugMode`. No datablock outside the two camera rules
references ordinal 188/189, and `.text` holds no 32-bit immediate 188 or 189 in
push/mov/cmp forms — so the entry is either a name-driven path (console / debug menu
resolving `CGST_DebugMode` through the registry by string) or absent from the shipping
build. Any public mention of a Prince of Persia (2008) PC console, debug menu key, or
`/console`-style switch (the exe's default command line carries `/noconsole`) would be
worth a line; nothing was found on 2026-08-25.

## Sources

Our own archives and executable only; LZO's `lzo2a_d.ch` / `config2a.h` (GPL, public) for
the decompressor transcription.
