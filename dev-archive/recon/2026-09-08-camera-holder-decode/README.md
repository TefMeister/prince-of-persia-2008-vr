# Which camera rule wins, and what makes a camera follow the Prince

`/pd`, dev PC, 2026-09-08. **THE GAME WAS NOT LAUNCHED. Nothing here was run.**

Everything in this folder is produced by `dev-archive/tools/forge/camera_rules.py`,
which was written this session and is read-only against the game folder.

## The question this closes

The board asked whether the free-flying camera we got on 2026-09-07 meant
(a) `CR_Debug_1stPerson`'s *execution* is a free camera in this build, or
(b) opening its state gate let a **different** rule win — `CR_Debug_GhostCam`
being the obvious suspect, since a ghost cam is what the behaviour looked like.

**It is (a).** Two independent legs:

1. **The two rules hold different camera objects of different classes.**
   `CR_Debug_1stPerson`'s `CameraHolder` points at `CAM FPS`, a
   **`PopMarketingCamera`**; `CR_Debug_GhostCam`'s points at `CAM Ghost POP`, a
   **`PopGhostCamera`**. They are not interchangeable and never were.
2. **`CR_Debug_GhostCam` is still gated shut in the archive we actually ran.**
   `debug-rules-deployed-2026-09-08.txt` was read from the installed
   `DataPC.forge` and shows GhostCam's second state list is still
   `(188, 309, 309)` — it still requires `CGST_DebugMode`, which we have never
   turned on. Only `CR_Debug_1stPerson` was patched to `(309, 309, 309)`.

So the rule that won is the one we patched, and what it installs is a marketing
camera. `[verified-numerically 2026-09-08]`

## Why a "marketing camera" flies around under the movement keys

`camera-subobject-census.txt` counts the nested `<u16 seq><0x9009><u32 classHash>`
sub-objects inside every camera datablock. The result is a clean discriminator:

| sub-object | `PopMarketingCamera` (3 blocks) | every other camera class (879 blocks) |
| --- | --- | --- |
| `PadButtonReader` | 56 | **0** |
| `PadAxisReader` | 4 | **0** |
| `BooleanAndReader` | 20 | **0** |

**Pad readers occur only in `PopMarketingCamera` — 0 occurrences across the other
879 camera datablocks** `[verified-numerically 2026-09-08, n=882 camera datablocks]`.
That is a camera which reads the pad itself and moves itself, which is exactly the
behaviour Tefa described on 2026-09-07: the keys drove the camera *and* the Prince,
because the character controller was still running independently.

## What makes a camera follow the character

`camera-holder-census.txt`: every one of the 380 `CameraRule`s has a
`CameraHolder`, and the class it holds is what the rule does.

| class held | rules | what it is |
| --- | --- | --- |
| `PathAnimationCamera` | 237 | scripted camera moves |
| `PopFixedCamera` | 63 | fixed viewpoints |
| **`PopFreeRoamingCamera`** | **36** | **ordinary traversal follow cameras** — `Parent_Ground_CR -> Parent Ground Cam` |
| `DuelStruggleCamera` | 10 | combat |
| `PopMarketingCamera` | 3 | the three debug fly cams, `CAM FPS` among them |
| `PopGhostCamera` | 1 | `CR_Debug_GhostCam` |

"FreeRoaming" names the **player's** state (free traversal), not a free camera.

⚠️ **One guess of mine that the data refuted, recorded so it is not repeated.**
A `PrinceTargetEntity` sub-object exists and looked like the follow reference. It
is not: **zero of the 44 `PopFreeRoamingCamera` blocks contain one**, while
`PopFixedCamera` and `PopMarketingCamera` do. Whatever makes a
`PopFreeRoamingCamera` track the Prince is implicit in the class, not an explicit
target reference in the data. `[disproved 2026-09-08]`

## Files

| file | what it is |
| --- | --- |
| `debug-rules-stock.txt` | both debug rules decoded from `DataPC.forge.bak-2026-09-07-pre-debugcam` (stock) |
| `debug-rules-deployed-2026-09-08.txt` | the same two read from the **installed** archive after this session's patch |
| `camera-holder-census.txt` | which camera class each of the 380 rules holds |
| `camera-subobject-census.txt` | nested sub-objects per camera class — the pad-reader discriminator |

## What is NOT established

- That repointing the rule at a `PopFreeRoamingCamera` produces a working follow
  camera. That is this session's patch and **it has not been run.** `[hypothesis]`
- Why `CR_Debug_1stPerson` outranks the ordinary gameplay rules once eligible.
  873 other rules are also `(309,309,309)` in stock and do not win, so eligibility
  alone does not decide it; arbitration order does, and we have not read the order
  out. The `FunkyCameras` rule book being listed last of four in `CameraGraph` is
  a plausible reason and nothing more. `[hypothesis]`
- Anything about `CAM FPS`'s internal field layout beyond its sub-object list.
