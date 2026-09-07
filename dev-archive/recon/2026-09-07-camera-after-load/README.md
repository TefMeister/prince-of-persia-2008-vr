# 2026-09-07 — full menu automation, and the camera does something after all

`/lm`, dev PC. The save was loaded **entirely by injected input** — no hardware, no human.

## The automated route, end to end

Steam URL -> `BM_CLICK` the launcher -> main menu -> `UP`/`DOWN` to highlight -> confirm ->
save entry -> confirm -> in gameplay. Every keystroke came from the injector.

**The confirm key is `SPACE`, and it must be HELD (~700 ms).** A 140 ms tap is ignored. That is
attributable rather than guessed: the same key failed as a short tap and worked as a long press,
twice in a row. `RETURN` and `LCONTROL` were never going to work — they are **not bound at all**.

The binding table was read out of `HKCU\Software\Ubisoft\Prince of Persia\1.0\Game` value `1`:
16 keyboard records at a 56-byte stride, `[u32 actionId][u8 DIK][0x22][01][01][36-byte GUID]`.
Bound keys: `W A S D`, the four arrows, `SPACE`, `E`, `R`, `T`, `TAB`, `ESC`, `PAUSE`.

## ⚠️ The camera observation, which complicates the earlier reading

| shot | what it shows |
| --- | --- |
| `2-on-load-...` | immediately on load, standing still: **ordinary third person, the Prince plainly in frame** |
| `3-while-walking-...` | holding `S`: view swings, **no character anywhere in frame** |
| `4-stopped-...` | key released, settled: **still no character** |
| `5-walked-forward-...` | holding `W`: **the view TRANSLATES through the canyon, still no character** |

So the pattern is **third person at rest, and a character-less camera that moves with input after
the character moves.** A view that responds to movement with nobody in it is what a first-person
or detached debug camera looks like.

**This is NOT a conclusion.** Earlier today the same build read as plain third person while
standing, and that was recorded as "the edit did nothing". Both observations are real; the
standing one was just incomplete.

### What would separate the possibilities

| possibility | the observation that separates it |
| --- | --- |
| `CR_Debug_1stPerson` is winning once a state transition occurs | press a key with an unmistakable character animation (`SPACE`) and see whether ANY character appears in frame |
| the Prince simply walked out of shot and the camera lagged | keep walking — an ordinary third-person camera snaps back to its subject within a second or two, and this one did not across three captures |
| a scripted camera for this spot | reload the same save and repeat at a different location |

The middle one is already weakened: the camera did not re-acquire the character across three
captures spanning several seconds and two directions of travel.

**Do not record "the mod works" until one of those runs.** The honest state is: the camera behaves
differently from an ordinary third-person camera after movement, on a build with the state list
patched, and nobody has yet checked what it does with the patch reverted.

⚠️ **The missing control is the important one:** revert `DataPC.forge` to the backup and repeat
this exact sequence. If the character-less camera happens there too, it is normal game behaviour
and has nothing to do with the edit.


---

# ✅ RESOLVED THE SAME DAY, BY TEFA AT THE CONTROLS — THE EDIT WORKS

Everything above about "no character in frame" is **explained and superseded**. Tefa took the
controls and reported what the camera actually does:

> *"movement keys move BOTH the camera freely around, i can go up in the sky or through the walls,
> but they also move prince still, so normal gameplay is impossible right now as camera is not
> locked to Prince. the characterless camera is just you panning the camera away so far that
> prince just dissapears from view."*

`[verified-live 2026-09-07, n=1, observed by Tefa at the controls]`

`6-FREE-CAMERA-CONFIRMED-top-down-on-prince.png` is the proof: Tefa parked the camera high above
the Prince, who is visible as a small figure far below — a viewpoint no third-person camera in
this game can produce.

## What this means

**The `(309, 309, 309)` state-list edit DOES take over the camera in normal gameplay, with no
code patch at all.** That is the whole 2026-09-02 plan working, through pure data.

What we get is a **free / detached debug camera**, not a head-locked first-person one:

- the camera flies freely — into the sky, through walls
- the same keys **still drive the Prince**, so camera and character move together
- consequently **normal play is impossible on this build**

## Two of my readings were wrong, and both are corrected here

1. **"The edit did nothing"** (this morning) — taken while standing still, which is the one state
   where the free camera happens to sit in a plausible third-person position. Incomplete, not
   false, but it was recorded as a result and should not have been.
2. **"A character-less camera"** (this afternoon) — that was me flying the camera away from him.
   The frames were real; the interpretation was mine and it was wrong.

The lesson is the same both times: **a still frame cannot tell a locked camera from a free one.**
The discriminating action is to move the camera and see whether the world or the subject moves —
which is exactly what a human at the controls did in seconds.

## The control run in the OPEN block is now unnecessary

Reverting to stock to see whether the character-less camera still happens is **no longer the
question** — the camera is demonstrably free-flying, which stock data cannot do. Do not spend a
launch on it.

## What is now open, and it is a much better problem

The pipeline is proven; this is camera-rule tuning from here.

- **Which rule is actually winning?** We patched `CR_Debug_1stPerson`, whose recorded states were
  `188 CGST_DebugMode, 189 CGST_DebugModeFPSCamera, 309`. The behaviour we get is a **ghost/free
  cam**, which is what `CR_Debug_GhostCam` (`188, 309, 309`) sounds like. Either
  `CR_Debug_1stPerson`'s execution is a free camera in this build, or a different rule is winning
  now that the gate is open. `[hypothesis]`
- **Getting the camera LOCKED to the Prince's head** is the remaining step toward the North Star,
  and it is now a data question with a validated repacker rather than a code question.
- **A free camera is itself useful** for VR recon — it is a flycam through the world.
