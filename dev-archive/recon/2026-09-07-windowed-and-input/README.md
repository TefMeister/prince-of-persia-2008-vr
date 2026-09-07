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
