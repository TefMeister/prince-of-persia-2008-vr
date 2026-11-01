# 2026-11-01 (`/pd`, dev PC): the follow camera's position curve, and a close-up build to tell our camera apart

**The game was not launched; nothing here has been run.** Static reading of `DataPC.forge` only.
Evidence and every script: `dev-archive/recon/2026-11-01-follow-camera-curves/`.

## Why

The 2026-10-16 note left one open question: when `CR_Debug_1stPerson` holds `Parent Ground Cam`, is that camera
really ours, or does a holder from the `842a41xx` id range fail to resolve so the game falls back to its own rule
(both look like a normal follow camera)? The way to separate them is to give our rule a camera that looks clearly
different and that no rule active during ordinary walking also holds.

## 1. What a `PopFreeRoamingCamera` is made of

44 blocks, 18 different sizes (1,965 to 3,876 bytes), so there is no single fixed layout to diff. But each is a
chain of named sub-objects whose class hashes resolve through the exe dictionary, ~100 per camera
(`ground-vs-archetype-fields.txt`, `frc_hex.py`). The chain, in order, for `Parent Ground Cam`:

`PrinceTargetTracker` (target, with `BoundingVolume`, `PrinceTargetEntity`, a bone target) → `MainDampingModifier`
→ a second tracker → `VerticalCompensationModifier` → `FreeRoamingModifier` → `PolarControlsModifier` (with
`PadButtonReader`/`PadAxisReader`: the orbit control) → **`PolarCurveModifier`** (with `TrajectoryImpl` +
`TrajectoryPoint`s) → `FreeRoamingCollisionModifier` → `CameraTargetModifier` → `ExplorationModifier` →
`ScreenFramingModifier` → `EulerModifier` → `RollModifier` → `TargetFramingModifier` →
`PopMarioModeAttenuatorModifier` → `ExtremeAzimuthModifier` → state conditions.
`[verified-numerically 2026-11-01, n=3 cameras walked in full]`

⚠️ The 2026-09-08 note said `PadAxisReader`/`PadButtonReader` occur only inside `PopMarketingCamera`. That count came
from `camera_rules.py subs`, which only finds the `<u16 seq><0x9009><hash>` tag form. Read as plain class hashes,
`Parent Ground Cam` holds 4 `PadAxisReader` and 2 `PadButtonReader` (the orbit control). The discriminator still
stands for the **tagged** form; it is not true of the class itself. The same goes for the 2026-09-08
`[disproved]` line "zero of the 44 follow cameras carry a `PrinceTargetEntity`": `Parent Ground Cam` holds 3 as plain
records. `[verified-numerically 2026-11-01, n=1 camera]` Corrected in `FORMAT.md` §6c.

## 2. The position curve: `PolarCurveModifier`, first trajectory

Each `TrajectoryPoint` carries a 3-float vector at +5 after its class hash (repeated at +117; the third float is
always 0). Read across all 44 cameras (`polar-curves-44-blocks.txt`), the first trajectory behaves exactly like a
camera-position curve in a vertical plane (along, up), in metres, from "low" to "high":

| camera | first trajectory points |
| --- | --- |
| `Parent Ground Cam` (and the archetype, slide, tremor, ...) | (1.10, 0.44) (-3.14, 3.21) (2.15, 6.81) |
| `PrinceCarryElika_CAM` (carrying Elika) | (1.45, 0.45) (0.49, 1.72) (1.78, 3.19): much closer |
| the `Prince_CloseUp_CR` camera `99d3ca72` | (0.02, -0.17) (-0.10, 0.32): almost at the target |
| `Headbump Cam` (under a low ceiling) | (0.12, -3.91) (-2.58, -1.33) (-2.08, 1.79): low |
| `Parent WallVerti Cam` (climbing) | (1.07, -3.28) (-3.31, -1.12) (-2.79, 9.73): a tall sweep |

The magnitudes match each situation. `[inferred-static 2026-11-01]`: this reading (along/up offsets from the
target) is not proven; build B below tests it. The second trajectory has x ≈ 3.13 in every camera and y between
-1.3 and 2.6; its meaning is open `[hypothesis]` (a look-at height is one guess).

`PrinceTargetTracker`'s bone target is a CRC32 of a bone name: `Parent Ground Cam` aims at `Reference`, the close-up
camera aims at **`Head`** `[verified-numerically 2026-11-01]` (both names resolve through the exe dictionary).

## 3. Which camera to give our rule

`frc_refs.py` lists who holds each camera (`who-holds-each-camera.txt`). Two candidates were rejected:

- `Parent Ground Cam`: held by 25 rule references, including the game's own `Parent_Ground_CR`. Editing it would
  change the fallback too, so it cannot tell the two readings apart.
- `Archetype Vanille Free Cam`: held only by `Archetype_FreeRoaming`, but that rule is gated `(309,309,309)`, eligible
  everywhere exactly like ours, so it could itself be the fallback.

Chosen: **`99d3ca72`, the close-up camera of `Prince_CloseUp_CR`**. Its rule is gated on states `(150, 257, 145)`,
not ordinary walking; it aims at the head bone; its curve sits almost on the target. If it shows while walking,
our rule installed it. It is also the nearest thing the game has to a first-person framing.

## 4. The two builds

Both made from the installed archive (the `Parent Ground Cam` repoint) with `forge_write.py patch`, each checked
four ways: `verify-layout` PASS; full-archive `diff` showing only the intended 4-byte ranges with 0 checksum
failures; our rule read back through `camera_rules.py` (holder `99d3ca72`); the curve read back through
`frc_curves.py`. `[verified-numerically 2026-11-01]` for the edits, `[hypothesis]` for what they do in game.

| build | edits | sha256 | where |
| --- | --- | --- | --- |
| **A** | `CR_Debug_1stPerson` holder + transition camera → `99d3ca72` (`0x56a3d2`, `0x56a3eb`; the same two fields as the 2026-09-08 edit, found again independently by `make_edits.py`) | `475ff840763d…` | **installed** on the dev PC, stamped |
| **B** | A + the close-up camera's first trajectory, every point's height +3.0 (4 floats, `edits_B.txt`) | `e341b5c2a8c7…` | local archive `prince-of-persia-2008-vr\DataPC.forge.2026-11-01-closeup-raised3m` |

Backup of what was installed before: `DataPC.forge.bak-2026-11-01-pre-closeup` (the `Parent Ground Cam` build,
`cmp`-verified). Either build can be rebuilt from `edits_*.txt` in one command.

## 5. What each outcome means

**Build A, load the save and walk:**
- The view jumps to a close-up at the Prince's head or shoulder → our rule installs the held camera from any id range
  (reading 1). The follow-camera result of 2026-10-16 was our camera.
- An ordinary follow camera, unchanged → the holder did not resolve and the game fell back (reading 2). Then the
  2026-10-16 marketing-camera result only proves the `c0f780xx` range.
- Something else (a frozen or odd view) → write down what it shows; the close-up camera may need its rule's other
  holder (a `FixedCamera`) first.

**Build B, only if A gave the close-up:** the same close-up but clearly higher (about 3 m) proves the first
trajectory is the camera's position curve, and that is the lever for a first-person framing (the curve put on the
head). No change from A means that trajectory is something else.

## Not established

- What the second to fourth trajectories do, and what the other ~95 sub-objects' numbers mean.
- Why `CR_Debug_1stPerson` wins arbitration (unchanged from 2026-09-08).
