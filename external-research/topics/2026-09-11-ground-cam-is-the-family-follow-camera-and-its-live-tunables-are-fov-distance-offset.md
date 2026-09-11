# "Ground Cam" is the Anvil family's ordinary follow camera, and its live tunables are FOV, distance and position offset

**Date:** 2026-09-11 (`/gr` estate sweep, CHECK-IN, home PC)
**Status:** 🆕 new
**Aimed at:** the deferred static step recorded on the board on 2026-09-08 — decoding
`PopFreeRoamingCamera`'s field layout (distance, height, FOV) once the `[FLAT]` follow-camera test
says the repoint works — and, more modestly, at the choice of `Parent Ground Cam` as the repoint
target.

## What was found

A public Assassin's Creed II mod, **"AC2 Customizable Ground Camera"**, lets the player edit
**FOV, camera distance and camera position offset for "the default Ground Cam used in game"**.
It is a **Cheat Engine table**, not a data edit: it writes the live camera object's numbers at
runtime. Its author also notes that shifting the camera position **sideways causes movement
drifting that needs direction correction**, and that the position edit can crash the game.
`[reported 2026-09-11]`

Assassin's Creed II (2009) is the Anvil title one generation after this game (Scimitar, 2008),
on the same engine lineage this dossier already established in §2.

## Why it matters for THIS project

1. **The name transfers.** The camera our 2026-09-08 repoint installs is `Parent Ground Cam`, a
   `PopFreeRoamingCamera`. A sibling title one year later calls its ordinary on-foot follow
   camera "the default Ground Cam". So "Ground Cam" is a **family-wide name for the normal
   follow camera**, not a PoP-local label — a small independent point in favour of the repoint
   target being the right class, before the `[FLAT]` test has been run. `[reported]` for AC2;
   applies here only as `[hypothesis]` until the walk-and-turn test settles it.
2. **The field set is corroborated.** The three things a modder found worth exposing on the
   live ground camera are exactly the three the board's deferred decode names: **FOV, distance,
   position offset**. That does not give offsets or a layout for our 3,608-byte block, but it
   says those three are real, separately writable parameters of this camera class in the family,
   which is what makes the differential-corpus plan (44 blocks of one class, compare the numbers
   that differ) worth running.
3. **A hazard to expect when the camera is moved to the head.** The AC2 author's "movement
   drifting" when the camera is offset sideways is the family's **camera-relative movement**
   showing through: the character controller steers relative to the camera, so moving the camera
   changes where "forward" is. A first-person offset placed on the Prince's head would be a
   *forward* offset rather than a sideways one, so the drift may be small — but any
   first-person step should budget for a movement-direction check, not just a viewpoint check.
   `[hypothesis]`

## What it does NOT do

- It is not a data-layout decode. No datablock, field name, offset or type is documented.
- It is runtime memory editing on a different game; nothing here shortens our own decode.
- The Nexus Mods page itself could not be fetched (HTTP 403 to automated fetch); everything above
  comes from search-engine summaries of the page text and should be re-read by a human before it
  is leaned on. A **same-generation AC1 "Camera and Controls Fix"** mod also exists on Nexus
  (mod 55) and could not be fetched either — its mechanism is **unknown**, and it is listed here
  only so nobody thinks it was not looked for.

## Also checked, still negative

- AnvilToolkit's schema-based exporter (forced by holding Shift on a file) lists resolved
  property names for `BuildTable`, `EntityBuilder`, `EntityGroupBuilder`, `Cloth`,
  `SoftBodySettings` and `Material` — **no camera type is named** in the public description.
  Same negative as 2026-09-07, from a different page of the same source. `[reported 2026-09-11]`
- No page anywhere names `FreeRoamingCamera`, `CameraRule` or `GraphRuleBook` for any Anvil
  title; the engine-identity wikis are the only hits. Same negative as 2026-09-07.

## Suggested next step (static, `[PD]`, contingent on the `[FLAT]` result)

When the differential decode of the 44 `PopFreeRoamingCamera` blocks runs, expect **three**
separately-varying scalar groups (a FOV in degrees or radians, a distance, and a 3-component
offset) and test that reading first. Nothing here is worth doing before the follow-camera test.

## Sources

- AC2 Customizable Ground Camera — Nexus Mods, Assassin's Creed II, mod 161
  (https://www.nexusmods.com/assassinscreedii/mods/161)
- Assassin's Creed Camera and Controls Fix — Nexus Mods, Assassin's Creed, mod 55, mechanism
  unverified (https://www.nexusmods.com/assassinscreed/mods/55)
- AnvilToolkit — Nexus Mods, Assassin's Creed, mod 30, schema-exporter description
  (https://www.nexusmods.com/assassinscreed/mods/30)
