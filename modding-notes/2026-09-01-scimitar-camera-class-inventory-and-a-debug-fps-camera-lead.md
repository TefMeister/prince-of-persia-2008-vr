# 2026-09-01 — The whole Scimitar camera architecture is named in the exe, and there is a debug FPS-camera state

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of the shipped executable; nothing modified.

---

## The binary is an open book

`PrinceOfPersia_Launcher.exe` (despite the name, this is the game: 9.5 MB of `.text`, ImageBase
`0x400000`) is **clean, unpacked, and full of class-name strings** — Scimitar keeps a reflection/RTTI
name table in the shipping build. A single scan turns up **152 distinct camera-related identifiers.**

That matters for route selection. The dossier's planned next step was D3D9 shader-constant
reflection; this says the **engine-level** route (dossier's option 2 in the general playbook) is
unusually well-signposted here, because the camera system's own vocabulary is readable without a
debugger.

Representative names, grouped:

* **Core objects:** `CameraComponent`, `CameraHolder`, `CameraActor`, `CameraGraph`,
  `CameraTemplate`, `CameraExecution`, `CameraTransitionManager`, `CameraTrajectory`
* **Behaviour/policy:** `CameraModifier`, `CameraRule`, `CameraRuleGraphClip`,
  `BasicCameraTransitionPolicy`, `CameraProximityExecutionPolicy`,
  `CameraRelevanceExecutionPolicy`, `CameraTargetFacingExecutionPolicy`, `CameraResetCondition`,
  `CameraSuccessionCondition`, `CutCameraTransition`, `DistanceSpringDampedCameraTransition`
* **Tunables:** `ACP_CameraFOV`, `ACP_CameraTargetDistance`, `AnimatableCameraParameter`,
  `CameraParameterAnimationFloat`, `CameraParameterAnimationVector4`
* **Specific cameras:** `AnimatedFreeRoamingCamera`, `DuelCamera`, `DuelProjectionCamera`,
  `ColumnCamera`, `CompassCamera`, `AxisCamera`, `CameraZone`, `CameraBarrier`, `CameraClip`

`AnimatableCameraParameter` + `ACP_CameraFOV` together mean **FOV is a first-class animatable
parameter of the camera system**, not a hardcoded projection constant — relevant later, since FOV
override is usually an early VR need.

## The lead worth chasing: `CGST_DebugModeFPSCamera`

Among the `CGST_*` enum names (Character Graph STate — the Prince's state machine) sit:

```
CGST_DebugMode
CGST_DebugModeFPSCamera
```

alongside ordinary gameplay states (`CGST_Air`, `CGST_Column_Move`, `CGST_Attack`, …) and
`CGST_COUNT`.

**A debug free/first-person camera state exists in the shipping build's state machine.** For a
project whose goal is a first-person VR view, an engine-native FPS camera state is the most valuable
kind of lead there is — it is the same shape as the Psychonauts dormant-debug-menu finding, which
turned out to be real and toggleable.

### ⚠️ What this does and does not establish

`[inferred-static 2026-09-01, n=1]`

* **Established:** the strings `CGST_DebugMode` and `CGST_DebugModeFPSCamera` are present in the
  shipped executable, in a contiguous, ordered `CGST_*` enum-name table.
* **NOT established:** that the state is reachable, that its implementation survived the shipping
  build (name tables routinely outlive the code they described), or that it does what its name
  suggests. **Do not record "PoP has a debug FPS camera" as fact.** The name table is evidence the
  enum existed at compile time and nothing more.

Psychonauts is the cautionary precedent in both directions: its debug menu was real and toggleable,
*and* a published listing of its contents turned out to be wrong for the actual build — four of four
debug toggles tested did nothing useful. Names are a hypothesis generator, not a result.

### The cheap way to settle it

The enum-name table gives every state an index. Find the table, get `CGST_DebugModeFPSCamera`'s
ordinal, then find the state-machine dispatch that switches on it. If the dispatch has a real case
for that ordinal, the state is implemented; if it falls through, the name outlived the code. **That
is entirely static** — the binary is unpacked and `flat-to-vr-RE-toolkit/tools/static-disasm.py`
handles it directly — and it is the obvious next session's work here.

## Next

1. Resolve the `CGST_DebugModeFPSCamera` ordinal and check the dispatch (static, no launch).
2. In parallel, the planned D3D9 shader-constant reflection remains valid — the two routes are
   complementary, and the class inventory above is what makes the engine-level one worth pricing at
   all.

🤖 Static analysis of the shipped executable only. The game was not launched, no game file was
modified, and no game content was copied into this repository — only identifier names, which are
interface metadata.
