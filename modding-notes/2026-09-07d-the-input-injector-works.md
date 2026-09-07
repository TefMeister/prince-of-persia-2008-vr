# 2026-09-07d — The input injector works: this game can now be driven

`/lm`, dev PC. Launched and driven with explicit permission.

**Automation capability 1 and 2 are achieved on this game.** Menus can be navigated and keys
held, entirely from outside the process, with no hardware and no reliance on Windows input.

---

## 1. Why an injector was needed at all

Neither Windows route reaches this game:

- **`SendInput`** — verifiably not seen. Game foreground, keyboard acquired **NONEXCLUSIVE**,
  polled ~200 Hz, a key held **22 seconds** across four logged samples, `keys currently down: 0`
  throughout. `[verified-live 2026-09-07]`
- **Posted messages** — cannot work by construction: the exe imports `DirectInput8Create` and
  XInput, and **none** of `GetAsyncKeyState`/`GetKeyboardState`/`GetKeyState`/raw input/
  `GetMessageA`/`ToAscii`. Only `PeekMessageA`, the pump itself. `[verified-numerically 2026-09-07]`

So rather than fight the input stack, write into the buffer the game asks for.

## 2. What it does

`IDirectInputDevice8::GetDeviceState` is already hooked. After the real call, before the game
sees the buffer, the proxy ORs in a shared-memory state block the harness writes from outside.

**OR, never assignment** — a key the human is physically holding must never be cleared by us.

Covered: the 256-byte keyboard array, `DIMOUSESTATE` (16 bytes) and `DIMOUSESTATE2` (20), with
relative mouse motion applied **exactly once** per write, because a delta left in place would be
re-added 200 times a second and spin the camera forever.

## 3. It works — three independent readings

| reading | result |
| --- | --- |
| `applied kb` counter | **355** in six seconds of one held key |
| the game's OWN log | every sample `keys currently down: 0` under `SendInput`, then **`1`** under injection |
| by eye | two injected `DOWN` taps moved the main-menu highlight **exactly two rows**, New Game to Options |
| frame difference under injected movement | **24.08**, against **0.00–0.23** measured on the same scene with no input |

`[verified-live 2026-09-07, n=1 session]` Evidence:
`dev-archive/recon/2026-09-07-input-injector/`.

The second row is the one that matters: it is the game reporting its own view of the keyboard,
from the buffer after injection, and it is the same log line that read 0 for every earlier attempt.

## 4. The harness

`staging/prince-of-persia-2008-vr/proxy-dinput8/tools/pop_input.py`

```
python pop_input.py on
python pop_input.py tap DOWN --ms 120
python pop_input.py down W          /  python pop_input.py up W
python pop_input.py mouse 40 -15
python pop_input.py status
python pop_input.py release-all
```

Injection defaults **OFF**, so deploying the DLL changes nothing until something enables it.

## 5. Two defects found by using the tools, both fixed

- **The dinput proxy hooked only the FIRST device.** This game creates the mouse first, so the
  keyboard — the whole point — was never instrumented and the log looked empty of activity. Now
  every device is registered, with originals stored per vtable.
- **`capture.ps1` composited our own console into frames**, because `BitBlt` reads the screen and
  PowerShell stole foreground. It now verifies the game is frontmost before grabbing and refuses
  rather than returning a contaminated image.

Both were caught before any conclusion rested on them.

## 6. Verification that is not "it seemed to work"

36 host-side checks, 0 failures, with no game and no device: OR semantics, bit-for-bit no-ops when
disabled or on bad magic, one-shot mouse deltas, both mouse state sizes, refusal on an
unrecognised size, and NULL inputs.

**And the offsets are checked against the compiler, not against a human reading the header.** The
harness writes raw bytes at hard-coded offsets into shared memory; a mismatch would not crash, it
would silently press the wrong keys — exactly the sort of bug that gets blamed on the game.
`tools/check_offsets.py` diffs the Python constants against `offsetof` output from a compiled
dump. All agree.

## 7. ⛔️ What is NOT established

- **The XInput virtual pad has never fired.** `proxy-xinput/` loads, maps the shared block and is
  unit-tested, but `applied_pad` stayed **0** — the game was never observed calling
  `XInputGetState`. So **"we can get past the title screen unattended" is NOT proven.** Only the
  DirectInput keyboard path is proven live. Why the game did not poll XInput while watched is
  open; the pad demonstrably matters, since plugging one in is what advanced the title screen.
- **Mouse injection is untested live.** The code path is covered by host tests and shares the hook
  that is proven for the keyboard, but no camera motion has been driven yet.
- **Capability 3 (character + camera) and 4 (graceful self-close) are not demonstrated.** Menus
  respond; nothing has been driven in gameplay yet, and no in-game quit route is mapped.
