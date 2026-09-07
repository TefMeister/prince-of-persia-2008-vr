# 2026-09-07c — Forced windowed mode, through the d3d9 proxy (the game has no switch for it)

`/lm`, dev PC. **The game WAS launched and driven** — Tefa gave explicit permission mid-session
(*"feel free to launch/close the game yourself as many times as you need"*), which is a departure
from the standing only-the-user-launches rule and is recorded here as the reason.

Asked for: *"if it is not running windowed, please do your best to get it to run windowed."*
**Done, and confirmed live.** The game now runs in a titled 1280x720 window.

---

## 1. The game cannot be asked for a window — there is no switch and no setting

Checked before building anything, because "add a `-window` flag" would have been the cheap answer
if one existed:

- **The command-line switch table has no windowed switch.** The whole pool was read out of a
  Steamless-unpacked copy: **97 switch-shaped names** in one contiguous `.rdata` run around file
  offset `0x929640`. Nothing display-related beyond `testvideo`, `msaa`, `shadows`, `postfx`,
  `fixedfov`, `fardist`, `neardist`. `[verified-numerically 2026-09-07, n=97]`
- **A whole-file case-insensitive search for `window`** returns only Win32 import names
  (`CreateWindowExA`, `ShowWindow`, …), the literal `Windows`, and one non-switch `window`.
  No `windowed`, no `fullscreen`, no `borderless`. `[verified-numerically 2026-09-07]`
- **The registry has no fullscreen flag.** `HKCU\Software\Ubisoft\Prince of Persia\1.0\Engine`
  carries `ScreenResolutionWidth` 1920, `ScreenResolutionHeight` 1080, `VerticalSync`,
  `Antialiasing`, `AspectRatioOverride`, `Shadows`, `PostEffects` — and nothing about windowing.
  `[measured 2026-09-07]`
- **No config file anywhere else.** Nothing under `Documents\My Games`, `AppData\Local` or
  `AppData\Roaming`. `DARE.INI` in the game folder is audio only. `[measured 2026-09-07]`

**So the present parameters are the only lever — and we already sit in front of them.**

## 2. What was built

The project's existing `d3d9.dll` proxy was a pure pass-through: it forwarded `Direct3DCreate9`
and logged. It now patches two vtable slots:

| interface | slot | why |
| --- | --- | --- |
| `IDirect3D9::CreateDevice` | 16 | where the fullscreen device is asked for |
| `IDirect3DDevice9::Reset` | 16 | a device lost/restored re-reads the parameters; without this the game snaps back to fullscreen at the first alt-tab |

Three of the four edits are **D3D9 validity rules, not preferences** — get any wrong and
`CreateDevice` returns `D3DERR_INVALIDCALL` rather than misbehaving visibly:

```
Windowed                     = TRUE
FullScreen_RefreshRateInHz   = 0                 /* MUST be 0 when windowed */
BackBufferFormat             = D3DFMT_UNKNOWN    /* adopt the desktop format */
BackBufferWidth/Height       = 1280x720          /* configurable; 0,0 keeps the game's own */
```

Then the window itself is reframed: `WS_POPUP` cleared, `WS_OVERLAPPEDWINDOW` set, client area
sized to exactly the backbuffer via `AdjustWindowRect`, centred on the work area, and
`WS_THICKFRAME`/`WS_MAXIMIZEBOX` removed — a user-dragged resize would not resize the backbuffer
and would just stretch the image, which reads as a rendering bug.

**Why 1280×720 and not the game's 1920×1080:** the desktop here is 1920×1080, so the game's own
resolution cannot fit in a window once a title bar and borders exist.

## 3. How well it is known — IT RAN, AND IT WORKS

**`[verified-live 2026-09-07, n=1 launch]`.** Tefa gave permission to launch mid-session, so this is no
longer a compile-time claim. The proxy log and an independent measurement of the window agree:

```
config ...\pop_vr.ini: Windowed=1 WindowWidth=1280 WindowHeight=720
Direct3DCreate9 called: SDKVersion=0x20
  hooked IDirect3D9::CreateDevice (slot 16), real=73C84DD0; windowed override ENABLED, 1280x720
IDirect3D9::CreateDevice adapter=0 type=1 hFocusWindow=006907AA flags=0x46
  requested: 1920x1080 fmt=22 windowed=0 refresh=60 swap=1
  CreateDevice: forced windowed (windowed=1 refresh=1 format=1 size=1) -> 1280x720
  applied  : 1280x720 fmt=0 windowed=1 refresh=0 swap=1
  CreateDevice -> 0x00000000 device=0CF7CC00
  window reframed: hwnd=006907AA ok=1 client=1280x720
  hooked IDirect3DDevice9::Reset (slot 16), real=73FE6500
```

**The game asked for exactly what the registry said** — 1920x1080, fullscreen, refresh 60 — which
is an independent confirmation that the registry read was right. `CreateDevice` returned
`D3D_OK`. Measured from outside the process afterwards: window rect 1286x749, **client area exactly
1280x720**, `WS_POPUP` clear, `WS_CAPTION` set, `WS_THICKFRAME` clear. Screenshot in
`dev-archive/recon/2026-09-07-windowed-and-input/`: a titled, centred, correctly-rendering window.

The earlier compile-time evidence still stands behind it:

- The parameter munging is a **pure function** over `D3DPRESENT_PARAMETERS`, tested on the host
  with no device, no game and no launch: **18 checks, 0 failures**
  (`src/windowed_test.c`). The tests cover the three validity rules, `0,0` meaning
  "keep the game's own size", **bit-for-bit no-op when disabled**, **idempotency**, correcting an
  already-windowed-but-invalid parameter block, and NULL inputs.
- The DLL builds clean as **PE32/i386** with its export table intact (`Direct3DCreate9` at ordinal 1).

What is **still** not established: behaviour across an alt-tab (`Reset` is hooked but no `Reset`
has been observed), and anything about how the game looks in gameplay, because gameplay was never
reached (section 7).

## 4. Turning it off, and reverting

Two levels, neither needing a rebuild:

| want | do |
| --- | --- |
| keep the proxy, drop the windowing | `Windowed=0` in `pop_vr.ini` beside the exe |
| a different size | `WindowWidth` / `WindowHeight` in the same file; `0`/`0` keeps the game's own |
| the previous proxy back | `copy d3d9.dll.bak-2026-09-07-pre-windowed d3d9.dll` |
| no proxy at all | delete `d3d9.dll` — the game then loads the system one and is entirely stock |

The proxy log is `pop2008_vr_proxy_log.txt` beside the exe. On a failure it says so in words and
names the ini switch to flip, rather than leaving a silent black screen to diagnose.

## 5. Reading the log next time

The healthy sequence is in section 3. The failure signatures, kept because they are what makes the
log worth reading:

```
config …\pop_vr.ini: Windowed=1 WindowWidth=1280 WindowHeight=720
hooked IDirect3D9::CreateDevice (slot 16), real=…; windowed override ENABLED, 1280x720
IDirect3D9::CreateDevice adapter=0 type=1 hFocusWindow=… flags=…
  requested: 1920x1080 fmt=22 windowed=0 refresh=60 …
  CreateDevice: forced windowed (windowed=1 refresh=1 format=1 size=1) -> 1280x720
  applied  : 1280x720 fmt=0 windowed=1 refresh=0 …
  CreateDevice -> 0x00000000 device=…
  window reframed: hwnd=… ok=1 client=1280x720
  hooked IDirect3DDevice9::Reset (slot 16), real=…
```

- **No `config` line at all** ⇒ the proxy is not loading; the game found the system `d3d9.dll` first.
- **`hooked … CreateDevice` missing** ⇒ the vtable patch failed; the game runs fullscreen as before.
- **`CreateDevice -> 0x8876086C`** (`D3DERR_INVALIDCALL`) ⇒ the game rejects a windowed device on
  those parameters. That is the interesting failure and the log's next line names the ini switch.
- **`window reframed: ok=0`** ⇒ device made windowed but the window handle was not ours to restyle;
  expect a borderless 1280×720 in the corner rather than a titled centred one.

## 6. ⛔️ INPUT AUTOMATION IS NOT SOLVED — and one of my own readings had to be withdrawn

Windowed mode was the ask and it is done. Driving the game is a separate problem and it is **open**.

**What happened, honestly.** From the attract screen I sent `SendInput` scancodes (the route that
works on Enslaved) and nothing moved. I then posted `WM_KEYDOWN`/`WM_CHAR`/`WM_KEYUP` to the
window, the screen advanced into the intro seconds later, and **I recorded that as "SendInput does
nothing, PostMessage works".** That was wrong. A later burst of the same posted messages did
nothing, so I ran the control I should have run first — **60 seconds with no input at all** — and
the game advanced into the intro by itself. It is an **attract/demo reel on an idle timer**. The
one apparent success was the timer, not my input.

`[disproved 2026-09-07]` — "PostMessage drives this game". Neither route is demonstrated.

**What IS established, and it narrows the next attempt:**

| checked | result |
| --- | --- |
| the window is foreground | yes — `GetForegroundWindow` returns the game |
| the game's own thread agrees it is focused and active | yes — `GetFocus` == `GetActiveWindow` == the game window, read under `AttachThreadInput` |
| UIPI blocking injected input | **no** — game and injector are both `S-1-16-8192` (Medium), neither elevated |
| `SendInput` keyboard scancodes | no observed effect |
| posted `WM_KEYDOWN`/`WM_CHAR`/`WM_KEYUP` | no observed effect once controlled for the attract timer |

So the two cheapest explanations — wrong focus, and integrity-level blocking — are both eliminated.

**What remains, and the observation that separates them:**

- **The game reads a gamepad only on this screen.** A console port of this vintage plausibly polls
  XInput/DirectInput for "press any key". *Separating observation:* plug in or emulate a pad and
  see whether the attract screen advances on a button press.
- **The game uses DirectInput8 with an exclusively-acquired keyboard device.** *Separating
  observation:* hook `DirectInput8Create`/`IDirectInputDevice8::GetDeviceState` in the proxy and
  see whether it is called at all, and with what.
- **The game is deliberately ignoring input during the attract sequence** and only accepts it in a
  narrow window. *Separating observation:* post keys continuously at ~10 Hz for a full attract
  cycle and see whether the transition ever happens off-schedule.

The second is the most informative and costs one proxy rebuild, since we already own `d3d9.dll`
and could add a `dinput8.dll` proxy beside it.

## 7. Not established

- **Whether the first-person camera edit did anything.** Gameplay was never reached, because of
  section 6. The deployed `(309,309,309)` state list is still completely untested. The frames
  captured during the attract reel are **cinematic cameras**, which tell us nothing about
  `CR_Debug_1stPerson`.
- Behaviour across an alt-tab: `Reset` is hooked but no `Reset` was observed in this run.
- Whether the mouse is captured differently in a window than in exclusive fullscreen.
- Any of the 97 switches. **A switch name in a binary is a lead, not a live feature** — this estate
  has already been burned by exactly that on Enslaved. None has been run.
