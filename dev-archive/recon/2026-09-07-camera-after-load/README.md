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
