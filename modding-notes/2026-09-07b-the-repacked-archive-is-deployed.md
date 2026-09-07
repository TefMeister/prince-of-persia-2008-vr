# 2026-09-07b — The repacked `DataPC.forge` is DEPLOYED (user-approved)

`/pd`, dev PC. **The game was still not launched.** This entry covers a file deployment only.

The `[USER]` row opened on 2026-09-03 — "deploy the validated repacked `DataPC.forge`, or say
no" — was answered **yes** by Tefa on 2026-09-07. Deployed the same session.

## What was deployed

`CR_Debug_1stPerson`'s state-condition list, in `DataPC.forge → Game Bootstrap`:

```
(188 CGST_DebugMode, 189 CGST_DebugModeFPSCamera, 309 CGST_Any)  ->  (309, 309, 309)
```

309 is `CGST_Any`, the don't-care sentinel, so the rule's state gate becomes unconditional.

## It was regenerated, not lifted out of a temp folder

The 2026-09-03 staged file was four days old and sitting in `%TEMP%`. Rather than trust it, the
patch was **regenerated from the currently-installed archive** and then checked four ways:

1. `verify-layout` on the installed archive — `PASS: 30 entries, layout formula holds exactly,
   padding is all zero`.
2. **Full-archive diff**, original vs freshly patched — decompressing and byte-comparing every
   datafile, not spot checks:
   ```
   DIFF  Game Bootstrap  byte-range  0x56a3a3 .. 0x56a3a5  (2 bytes)
   DIFF  Game Bootstrap  byte-range  0x56a3a7 .. 0x56a3a9  (2 bytes)
   2 differing range(s) across 2 entries; 0 checksum failure(s) in b
   ```
   Identical to the 2026-09-03 result.
3. The freshly generated file is **byte-identical to the 2026-09-03 staged file** — an independent
   reproduction of that output, four days and one session apart.
4. Read-back from the **live install after deployment**: `CR_Debug_1stPerson states = (309, 309,
   309)`, and the datafile still splits into **9,684 datablocks**, the same count as before the
   edit. `verify-layout` passes on the deployed file.

`[verified-numerically 2026-09-07, n=1 production edit, full-archive diff + post-deploy read-back]`

## Reverting — one file copy

```
copy "DataPC.forge.bak-2026-09-07-pre-debugcam" "DataPC.forge"
```

The backup sits beside the archive in the game folder, was written before the overwrite, and was
`cmp`-verified byte-identical to the original at the time it was taken. **Nothing else in the
install was touched.**

⚠️ **Steam's "verify integrity of game files" will replace the patched archive**, silently and
without warning, because it no longer matches Steam's manifest. If the debug camera stops working
for no apparent reason, check that first — and note this also means the deployment is trivially
undoable by anyone, including by accident.

## ⚠️ What this does NOT establish, and what to actually watch for

**Only the state-list half of the recorded mod is done.** The 2026-09-02 plan was "rewrite the
state list **and raise its priority**". The priority half has never been located and was not
touched. So the honest position is that this edit makes `CR_Debug_1stPerson` *eligible* in every
state; it does not make it *win*. `[hypothesis]`

The next launch decides it, and the outcomes are distinguishable:

| what you see | what it means |
| --- | --- |
| first-person camera in normal play, `CAM FPS` behaviour | the state list was the only gate — the mod works with no code patch at all |
| camera unchanged, game otherwise normal | the rule is eligible but **losing to a higher-priority rule**; the priority field is the next target, and it is a static hunt, not a live one |
| camera flickers or fights between first and third person | two rules now both satisfy their conditions — that is the priority problem showing itself directly, and it is *informative*, not a failure |
| crash or hang on load | the archive edit is not being read as intended; revert with the one copy above and say so, because the full-archive diff says this should not happen |

**A crash would be the surprising outcome**, given every block's checksum verifies and the layout
formula holds on the deployed file. Say which of the four happened — the middle two are the
interesting ones and they are easy to confuse.

## Status of the debug-menu line

Unchanged and unaffected. This route was always independent of it; 2026-09-07's earlier entry
closed the hash channel and left item enumeration open, and none of that matters if the camera
simply appears.

---

# RESULT (added 2026-09-07, same day) — the edit did NOT produce a first-person camera

Tefa played through the opening by hand and handed back live gameplay. Read in ordinary
player-controlled play (the "PRESS [SPACE] TO JUMP ON TO THE WALL" tutorial prompt on screen,
Prince standing still):

**The camera is steady behind-the-shoulder third person.** Three captures a second apart show no
flicker and no fighting. `[verified-live 2026-09-07, n=1]` Evidence:
`dev-archive/recon/2026-09-07-windowed-and-input/gameplay-camera-still-third-person.png`.

**The archive was re-read from the live install at the same moment** and is still patched —
`CR_Debug_1stPerson states = (309, 309, 309)` — so this is not Steam having restored the stock
file. That alternative is eliminated, not assumed.

## What this does and does not tell us

The predicted "camera unchanged" outcome was **"eligible but losing to a higher-priority rule"**.
That is the leading candidate *by design* — the recorded mod was always "rewrite the state list
**and raise its priority**", and only the first half was ever done. But it is a candidate, not a
conclusion, and two others fit the same observation:

| possibility | the observation that would separate it |
| --- | --- |
| (a) the rule is eligible but **loses on priority** | locate and raise the priority field in the same datablock, repack, relaunch — first person appears |
| (b) the state list is **not the only gate**: the camera executor needs the game genuinely in debug mode | (a) is tried and fails even at maximum priority |
| (c) `CR_Debug_1stPerson` is **not wired to the player camera path** in retail at all | the control below comes back negative |

## ⭐ The control that should run BEFORE (a) — does our archive edit reach the camera system at all?

Everything above assumes the game reads camera rules from the archive we patched. That has never
been demonstrated: **the edit changed nothing observable, which is exactly what a completely
ignored edit also looks like.** A negative is only evidence if the test could have produced a
positive.

So: take a `CameraRule` that unquestionably runs in normal play, rewrite *its* state list to
something impossible, repack, relaunch.

- **the normal camera visibly breaks** ⇒ archive camera edits do reach the running game, the
  pipeline works, and (a) is the right next move
- **nothing changes** ⇒ our edits are not reaching the camera system, (c) is live, and raising a
  priority field would have been wasted work

This costs one repack and one launch, and it is worth more than trying (a) blind.


---

# ✅✅ RESOLVED, SAME DAY — THE EDIT WORKS. IT GIVES A FREE DEBUG CAMERA.

The `RESULT` section above is **superseded**. It said the edit did not produce a first-person
camera and read the camera as unchanged. That reading was taken **standing still**, and it was
wrong.

Tefa took the controls in the loaded save and reported:

> *"movement keys move BOTH the camera freely around, i can go up in the sky or through the walls,
> but they also move prince still, so normal gameplay is impossible right now as camera is not
> locked to Prince. the characterless camera is just you panning the camera away so far that
> prince just dissapears from view."*

`[verified-live 2026-09-07, n=1, observed by Tefa at the controls]` Evidence:
`dev-archive/recon/2026-09-07-camera-after-load/6-FREE-CAMERA-CONFIRMED-top-down-on-prince.png`
— the camera parked high above the Prince, who is a small figure far below. No third-person camera
in this game produces that.

## The result, stated plainly

**Rewriting `CR_Debug_1stPerson`'s state list to `(309, 309, 309)` takes over the camera in normal
gameplay, with no code patch of any kind.** The 2026-09-02 plan works, through pure data, and the
repacker was the only thing that was ever missing.

What it yields is a **free / detached camera**:

| behaviour | consequence |
| --- | --- |
| camera flies freely — sky, through walls | a usable flycam for VR recon, immediately |
| the same keys still drive the Prince | camera and character move together |
| camera is not locked to the Prince | **normal play is impossible on this build** |

⚠️ So this build is a **modding build, not a playable one.** Reverting is one file copy:
`copy DataPC.forge.bak-2026-09-07-pre-debugcam DataPC.forge`.

## My two wrong readings, and the lesson

1. **"The edit did nothing"** — standing still is the one state where a free camera happens to sit
   in a plausible third-person position.
2. **"A character-less camera"** — that was me flying the camera away from him.

Both frames were real; both interpretations were mine and both were wrong. **A still frame cannot
distinguish a locked camera from a free one.** The discriminating action is to *move the camera and
see whether the subject stays* — which a human at the controls settled in seconds, after I had
spent several captures on it.

## What is open now — a much better problem than this morning's

- **Which rule is actually winning?** `CR_Debug_1stPerson`'s recorded states were `188
  CGST_DebugMode, 189 CGST_DebugModeFPSCamera, 309`, but the behaviour is a ghost/free cam, which
  is what `CR_Debug_GhostCam` (`188, 309, 309`) sounds like. Either this rule's *execution* is a
  free camera in this build, or opening the gate let a different rule win. `[hypothesis]`
- **Locking the camera to the Prince's head** is the remaining step to the North Star — and it is
  now a **data** question against a validated repacker, not a code question.
- The old "raise its priority" half of the mod may be unnecessary: the rule is evidently already
  winning.
