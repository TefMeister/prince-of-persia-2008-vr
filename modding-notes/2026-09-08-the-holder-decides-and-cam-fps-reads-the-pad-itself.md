# The holder decides which camera you get — and `CAM FPS` reads the pad itself

`/pd`, dev PC, 2026-09-08. **The game was not launched. Nothing in this note has been run.**

Evidence: `dev-archive/recon/2026-09-08-camera-holder-decode/`.
Tool: `dev-archive/tools/forge/camera_rules.py` (new, read-only).

## The short version

The `⭐⭐` board row asked which camera rule was actually winning after the
2026-09-07 patch, and whether it could be locked to the Prince's head. Both halves
moved:

- **The rule that won is the one we patched.** `CR_Debug_GhostCam` was never a
  candidate — in the archive we actually ran it is still gated on
  `188 CGST_DebugMode`, which has never been turned on.
- **The free-flying behaviour is the rule's execution, exactly as branch (a) of
  the row proposed.** `CR_Debug_1stPerson` installs `CAM FPS`, and `CAM FPS` is a
  `PopMarketingCamera` that contains its own `PadButtonReader` / `PadAxisReader`
  sub-objects. It flies because it reads the pad and moves itself.
- **The follow cameras are a different class**, `PopFreeRoamingCamera`, held by 36
  ordinary traversal rules.
- **A one-word change repoints our winning rule at a follow camera**, and that
  change is built, verified and deployed.

## How a `CameraRule` decides behaviour

A `CameraRule` body is a flat sequence of `{u32 objectId; u32 classHash; ...}`
sub-records (`FORMAT.md` §6). Decoded, both debug rules have **identical shape** and
differ only in ids and two fields:

```
  +000  CameraRule                          the rule itself
  +00d  PopStateRuleCondition               the gate
  +01b  PopCharacterGraphStateDescription   states (309,309,309)
  +033  PopCharacterGraphStateDescription   states  <-- the half we patched in 2026-09-07
  +055  CameraExecution
  +066  CameraHolder                        -> THE CAMERA OBJECT       <-- decides behaviour
  +077  CameraTransitionSpecification       -> transition, then the same camera again
```

`CameraHolder`'s first tail word is the datablock id of the camera the rule
installs. Stock:

| rule | 2nd state list | `CameraHolder` -> | class |
| --- | --- | --- | --- |
| `CR_Debug_1stPerson` | `188, 189, 309` | `CAM FPS` | **`PopMarketingCamera`** |
| `CR_Debug_GhostCam` | `188, 309, 309` | `CAM Ghost POP` | **`PopGhostCamera`** |

`[verified-numerically 2026-09-08]`

⚠️ Note the naming trap: `/gr`'s inbox drop warned that `*Holder` is an Anvil idiom
for "container of a list" rather than "thing that holds the camera in space". Here
it is neither — in this generation it is a **single object reference**, and it is
the field that matters.

## Why the either/or is settled rather than argued

Read straight out of the **installed** `DataPC.forge`, not a staged copy:

```
CR_Debug_GhostCam    states=[(309,309,309), (188,309,309)]   holder -> PopGhostCamera 'CAM Ghost POP'
CR_Debug_1stPerson   states=[(309,309,309), (309,309,309)]   holder -> PopMarketingCamera 'CAM FPS'
```

GhostCam still demands `CGST_DebugMode`. We never reached debug mode — the whole
debug-menu route was closed on 2026-09-07. So it cannot have been the winner, and
the camera we flew was `CAM FPS`. `[verified-numerically 2026-09-08]`

## The discriminator that explains the behaviour

Camera datablocks nest sub-objects as `<u16 seq><0x9009><u32 classHash>`, the class
hash being the same CRC32 as a datablock `typeHash`. Counting them per class:

| sub-object | `PopMarketingCamera` (3 blocks) | all other camera classes (879 blocks) |
| --- | --- | --- |
| `PadButtonReader` | 56 | **0** |
| `PadAxisReader` | 4 | **0** |
| `BooleanAndReader` | 20 | **0** |
| `AdditiveAndReader` / `MultiplicativeAndReader` | 4 / 6 | **0** |

`[verified-numerically 2026-09-08, n=882 camera datablocks]`

**Only a marketing camera reads input directly.** That is a self-driving camera,
and it matches Tefa's 2026-09-07 description exactly — *"movement keys move BOTH
the camera freely around, i can go up in the sky or through the walls, but they
also move prince still"*. Two consumers of the same keys, which is what you get
when a camera that flies itself is installed over a character controller that is
still running.

## What makes a camera follow the Prince

Every one of the 380 `CameraRule`s holds exactly one camera:

| class held | rules |
| --- | --- |
| `PathAnimationCamera` | 237 |
| `PopFixedCamera` | 63 |
| **`PopFreeRoamingCamera`** | **36** |
| `DuelStruggleCamera` | 10 |
| `DuelProjectionCamera` | 8 |
| `HealingCamera` / `AnimatedFreeRoamingCamera` / `LookAtTargetFreeRoamingCamera` | 4 each |
| `PopMarketingCamera` | 3 |
| `PopGhostCamera`, `PopFlyOnBeamCamera`, `CompassCamera`, `DuelCamera` | 1 each |

`PopFreeRoamingCamera` is the ordinary traversal follow camera —
`Parent_Ground_CR -> Parent Ground Cam`, `Parent_WallingVertical_CR`,
`PrinceCarryElika_CR`. **"FreeRoaming" describes the player's state, not the
camera's freedom.**

### One reading of mine that the data refuted

A `PrinceTargetEntity` sub-object exists and looked exactly like the follow
reference `/gr`'s drop predicted ("what a camera tracks is an object reference").
It is not that. **Zero of the 44 `PopFreeRoamingCamera` blocks contain one**, while
`PopFixedCamera` (8) and `PopMarketingCamera` (2) do. So it is a look-at target for
cameras that need to aim at the Prince from elsewhere, not the mechanism by which a
follow camera follows. Whatever does that is implicit in the class.
`[disproved 2026-09-08]` I am recording this because it is the kind of plausible
name-based inference that reads as a citation once it is written down.

## The patch that is now deployed

Two `u32`s inside `CR_Debug_1stPerson`, repointing it from the self-driving
marketing camera to an ordinary follow camera:

```
forge_write.py patch DataPC.forge out.forge --datafile "Game Bootstrap" \
    --edit 0x56a3d2:3380f7c0=05412a84 \   # body+0x6e  CameraHolder target
    --edit 0x56a3eb:3380f7c0=05412a84     # body+0x87  TransitionSpec back-reference
#   c0f78033 'CAM FPS' (PopMarketingCamera) -> 842a4105 'Parent Ground Cam' (PopFreeRoamingCamera)
```

Checked four ways before deployment `[verified-numerically 2026-09-08]`:

- `verify-layout` PASS on the source archive and again on the output;
- full-archive `diff`: **exactly the 2 intended 4-byte ranges, 0 checksum failures**;
- read back from the output: 9,684 datablocks (unchanged), holder **and** transition
  back-reference both now `PopFreeRoamingCamera 'Parent Ground Cam'`, `CR_Debug_GhostCam`
  untouched;
- read back a second time from the **installed** file after deploying, through
  `camera_rules.py` rather than the script that generated the patch — an independent
  code path, not a re-print of the same buffer.

Backup `DataPC.forge.bak-2026-09-08-pre-followcam` written and `cmp`-verified before
the overwrite; the stock `…bak-2026-09-07-pre-debugcam` is still there untouched.
`deployed.sh record` re-run.

⚠️ **Nothing about this patch has been run.** It is a hypothesis with a build
behind it.

## The four outcomes of the next launch, and what each means

Load a save and walk. `CR_Debug_1stPerson` is `(309,309,309)`, so it is eligible
in every state, exactly as it was for the flycam build.

| what you see | what it means |
| --- | --- |
| **A normal third-person camera that follows the Prince** | The holder is the whole mechanism: our winning rule now installs a follow camera. This is the result that unlocks first person — the next step becomes tuning a `PopFreeRoamingCamera`'s distance to zero. |
| **The flycam again** | The repoint did not take effect. Suspect the transition spec, or a second reference we did not patch. |
| **A camera that follows but is framed oddly** (wrong distance/height for the situation) | Also success — `Parent Ground Cam` is the *ground* camera being used in every state, including ones it was never authored for. Same conclusion as row 1. |
| **No camera change at all / stock behaviour** | Our rule stopped winning. That would contradict 2026-09-07f and needs explaining before anything else is built. |

⚠️ Rows 1 and 4 can look similar standing still. **The discriminating action is to
walk and turn**: a followed camera keeps the Prince framed while he moves. This is
the same trap as 2026-09-07f, where a still frame could not tell a locked camera
from a free one.

## Why this candidate rather than a first-person one directly

Pointing straight at "a first-person camera" is not available: no camera in the
archive is authored as one. `CAM FPS` is named for it but is a marketing flycam.
So the route is two steps, and this is the first: **prove the holder controls what
you get**, using a camera whose correct behaviour is unmistakable. Only then is it
worth editing a `PopFreeRoamingCamera`'s own distance/height fields, which are not
decoded yet.

## Next, and what it needs

- `[FLAT]` the launch above — one command, four distinguishable outcomes.
- `[PD]` decode `PopFreeRoamingCamera`'s field layout (distance, height, FOV) so
  step two is a data edit. `Parent Ground Cam` is 3,608 bytes and its floats are
  not yet identified; the 44 blocks of that class are a good differential corpus,
  since cameras authored for different situations should differ mainly in those
  numbers.
