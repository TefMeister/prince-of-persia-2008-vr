# 2026-09-07 — the input injector, working

`/lm`, dev PC. The game was launched and driven with explicit permission.

This game cannot be driven by any Windows input API: `SendInput` is verifiably not seen
(game foreground, key held 22 s across four logged samples, `keys down` 0 throughout), and
posted messages cannot work because the exe imports no message-queue key reading at all.
So the proxy writes into the state buffer the game asks for, inside `GetDeviceState`.

| file | what it shows |
| --- | --- |
| `dinput-log-injection-working.txt` | the game's own view. Every sample reads `keys currently down: 0` while `SendInput` was held, then **`1`** once the injector was used |
| `menu-highlight-on-new-game.png` | main menu, highlight on **New Game** |
| `menu-highlight-moved-two-rows-by-injection.png` | after two injected `DOWN` taps, highlight on **Options** — exactly two rows, no hardware involved |

## The numbers

- `applied kb` rose to **355** over six seconds of one held key — the injector runs on every
  poll, at the game's own ~200 Hz.
- Frame difference while a movement key was injected: **24.08**, against **0.00–0.23** measured
  on the same scene with no input. Not a marginal signal.

## What is NOT proven

The **XInput virtual pad** (`proxy-xinput/`) loads and maps the shared block, but `applied_pad`
stayed **0** — the game never called `XInputGetState` while it was watched. So the pad path is
built and unit-tested but **has never actually fired**, and the claim "we can get past the title
screen unattended" is NOT established. Only the DirectInput keyboard path is proven live.
