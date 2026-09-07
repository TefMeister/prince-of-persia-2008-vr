# 2026-09-07 — windowed mode works; input automation does not

`/lm`, dev PC. The game **was** launched and driven this session, with explicit permission.

| file | what it is |
| --- | --- |
| `windowed-1280x720-titlescreen.png` | the result: a titled, centred 1280x720 window, rendering correctly |
| `proxy-log-windowed-success.txt` | the load-bearing log — game requests 1920x1080 fullscreen@60, gets 1280x720 windowed, `CreateDevice -> 0x00000000` |
| `proxy-log-direct-exe-launch-fails.txt` | launching `PrinceOfPersia_Launcher.exe` directly: the proxy loads and reads its config, then the process exits in 0.6 s without ever calling `Direct3DCreate9`. **The game must be started through Steam**, which runs `Launcher\Launcher.exe -uplay_steam_mode` first |
| `capture.ps1` | BitBlt screen capture (NOT `PrintWindow` — see UNIVERSAL.md) |
| `sendkey.ps1` | `SendInput` scancode route — **no observed effect on this game** |
| `postkey.ps1` | posted-message route — **also no observed effect** once the attract timer was controlled for |

## The launcher IS drivable, even though the game is not

`Launcher\Launcher.exe` is an ordinary Win32 dialog. Its three buttons enumerate cleanly and
`BM_CLICK` on the first one starts the game — no pixel work, no synthetic input:

```
class=Button text='Launch the game!'
class=Button text='Settings'
class=Button text='Quit'
```

## The correction this folder exists to record

An early reading — "SendInput does nothing, PostMessage works" — was **wrong and is withdrawn**.
The screen advanced because the title screen is an **attract/demo reel on an idle timer**, which a
60-second no-input control demonstrated directly. Neither input route is demonstrated to work.
Two cheap explanations are eliminated: focus is genuinely held by the game (checked from its own
thread under `AttachThreadInput`), and UIPI is not blocking (both processes Medium integrity).

## Later the same session — the camera test finally ran

Tefa played through the opening cutscene by hand and handed back a live gameplay state.

`gameplay-camera-still-third-person.png` — ordinary player-controlled gameplay (the
"PRESS [SPACE] TO JUMP ON TO THE WALL" tutorial prompt is on screen), Prince standing still.
**The camera is steady behind-the-shoulder third person.** Three captures a second apart show no
flicker and no fighting between camera rules.

The archive on disk was re-checked at the same moment and is **still patched** —
`CR_Debug_1stPerson states = (309, 309, 309)` read back from the live install — so this is not
Steam having silently restored the stock file.

**So the state-list edit alone does NOT produce a first-person camera.** `[verified-live
2026-09-07, n=1]`

### A defect in `capture.ps1`, found by using it

The first three "flicker" captures had **our own console window composited into the frame**:
`BitBlt` reads the screen, so anything overlapping the game is captured, and PowerShell stole
foreground as it ran. `capture.ps1` now verifies `GetForegroundWindow` really is the game before
grabbing, retries up to 12 times, refuses rather than returning a contaminated image, and
re-checks focus afterwards. The clean re-capture confirms the third-person reading, so no
conclusion here rests on a contaminated frame.
