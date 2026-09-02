# 2026-09-02 — `.forge` decoded: generated evidence

`/pd` pass, dev PC, **game never launched**. Everything here was produced by
`dev-archive/tools/forge/forge.py` (+ `lzo2a.dll` built from `lzo2a.c`) reading the
shipped archives read-only. No game content is stored — only names, offsets, hashes and
counts, which are interface metadata. Format write-up: `tools/forge/FORMAT.md`; narrative:
`modding-notes/2026-09-02-forge-decoded-the-debug-fps-camera-is-authored-data.md`.

| file | what |
| --- | --- |
| `archive-index.txt` | `forge.py list *.forge` — all 33,401 datafiles in the 20 archives: index, offset, size, build time, uid, name |
| `type-census.tsv` | datablock count and bytes per resolved type across the 14 non-sound archives (7.90 GB decompressed; 202 types, 201 resolved via CRC32 of exe identifiers) |
| `game-bootstrap-camera-datablocks.txt` | every camera / rule-book / transition / debug-menu datablock in `DataPC.forge → Game Bootstrap`, with resolved type names |
| `sweep-hits.txt` | the estate-wide needle sweep: `HASH` lines are the CRC32 state-hash hits (all inside `SoundBao` audio = noise, including the three positive controls); `STR` lines the literal-string hits (`DebugMode_Transition`, `FPSCamera_Transition`); `NAME` lines the datablock names matching `FPS|Debug|Ghost|FreeCam` |
| `cgst_registry.tsv` | the 313-row `CGST_*` state registry re-decoded from the exe (`ordinal, name, CRC32`) — corrected PE-section parse of the 2026-09-01 decode; identical content |

Reproduce (from the game folder, tool path abbreviated):

```
python forge.py verify *.forge
python forge.py types  --exe PrinceOfPersia_Launcher.exe DataPC*.forge
python forge.py blocks --exe PrinceOfPersia_Launcher.exe --match "Game Bootstrap" \
       --type "Camera|GraphRuleBook|CameraRule|Transition|DebugMenu|Tutorial" DataPC.forge
```
