# 2026-10-16 (`/lm`, dev PC): the repointed rule gives a following camera, and a control test shows the swap is honoured

Three launches, all recorded (game window only), in `MEGA transfer\Videos\prince-of-persia-2008-vr\`:
`followcam-walk-turn_2026-10-16_18-51-24.mp4`, `ghostcam-check_2026-10-16_19-06-52.mp4`,
`marketingcam-check_2026-10-16_19-12-28.mp4`.

## 1. The deployed build (`CR_Debug_1stPerson` → `Parent Ground Cam`): a normal following camera

Tefa played it: loaded the Canyon save, walked and turned. Their words: *"prince moves normally"*, and asked whether
the camera stays behind the Prince and whether the mouse swings it around him: *"yes to both"*
`[verified-live 2026-10-16, n=1, observed by Tefa]`. So the build is playable again with the rule still eligible
everywhere, which is the 2026-09-08 prediction for success.

## 2. Is that camera ours, or the game ignoring us? Two control swaps

A following camera looks the same whether our rule installs `Parent Ground Cam` or the game falls back to its own
rule. So the holder was swapped twice more (the same two `u32` fields, `0x56a3d2` and `0x56a3eb` of
`Game Bootstrap`; each build `verify-layout` PASS and a full diff of exactly the 2 intended 4-byte ranges, 0
checksum failures), and driven by me:

| Holder installed by `CR_Debug_1stPerson` | Walk (W/S) | Mouse turn | Reading |
| --- | --- | --- | --- |
| `Parent Ground Cam` (`842a4105`, PopFreeRoamingCamera) | follows | orbits the Prince, he stays centred | normal follow camera (Tefa) |
| `CAM Ghost POP` (`c0f7800b`, PopGhostCamera) | follows (backing into a wall put the camera inside the rock once) | orbits, the Prince stays centred | looks like a follow camera |
| `CAM Marketing POP` (`c0f78001`, marketing camera class) | **camera stays, the Prince walks away from it** | **turns on the spot, the Prince slides off the screen edge** | free camera, like `CAM FPS` on 2026-09-07 |

`[verified-live 2026-10-16, n=1 each]`, screenshots read by me at each step.

**What it settles:** the game honours a swapped holder. `CAM Marketing POP` is a different object from `CAM FPS`, and
it produced the free camera, so the rule is still winning and the holder field is what decides the behaviour.

**What it does not fully settle** `[hypothesis]`: `CAM Ghost POP` and `CAM Marketing POP` sit in the same id range as
`CAM FPS` (`c0f780xx`); `Parent Ground Cam` comes from another range (`842a41xx`). The two readings for the
follow-camera result:

1. the game installs `Parent Ground Cam` from our rule (most likely: the ghost camera, from the proven range, also
   came out as an orbit camera, so "orbit-looking" is no sign of fallback);
2. a holder from another range does not resolve, and the game falls back to its own rule.

The observation that separates them: change something visible in **our** camera only (for example point the rule at
a different `PopFreeRoamingCamera` with an obviously different framing, or edit a copy of `Parent Ground Cam`). If
the view changes, reading 1 holds. This is also the first step towards first person, so it is not wasted work.

## 3. Driving: the title screen is no longer a wall

With the game window truly in front (an Alt tap, then `SetForegroundWindow`; checked `GetForegroundWindow` equals
the game), `keybd_event` with **hardware scancodes** (SPACE then RETURN, each held 300 ms) passed "PRESS ANY KEY"
`[verified-live 2026-10-16, n=2]`. Not the idle timer: the timer leads to a demo reel, and this went straight to the
main menu. From there the injector route works as before (DOWN, SPACE held 700 ms, SPACE held 700 ms) to the
loaded save. So **launch to gameplay is now fully automatic**, which the 2026-09-07 profile said it was not.

## 4. Other readings

- **XInput:** `applied pad` stayed **0** through menus and gameplay with no pad connected `[measured 2026-10-16]`.
  No `VERDICT:` line was written because each run ended by closing the process, which skips the proxy's exit
  path. A graceful quit is still not automated.
- `pop2008_vr_proxy_log.txt` shows `THUNK: the game called DebugSetMute`, which this proxy build forwards by thunk.
- **Music is not muted yet.** Its setting is not in the registry (`Engine`, `Game`, `Launcher` keys hold no volume),
  so it most likely sits in the profile blob or the save. Set it in Options once, then find what changed.

## Installed now (dev PC)

Unchanged from the record: `DataPC.forge` with the `Parent Ground Cam` repoint (`deployed.sh check`: all 5 files
match). The two control builds were never kept in the game folder.
