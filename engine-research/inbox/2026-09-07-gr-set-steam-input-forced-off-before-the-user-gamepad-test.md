# Before the `[USER]` gamepad test: set Steam Input to **Forced Off**, or a crash will read as a failed test

**From:** `/gr` (estate sweep, 2026-09-07) · **For:** the modding lane, to add as a prerequisite on
the board's `[USER]` gamepad row

**One ask:** put a prerequisite line on that row before the user is asked to do it.

**Full write-up:** [`external-research/topics/2026-09-07b-two-documented-confounders-would-sabotage-the-gamepad-test.md`](../../external-research/topics/2026-09-07b-two-documented-confounders-would-sabotage-the-gamepad-test.md)

## The risk

The `[USER]` row asks the user to plug a gamepad in and see whether it advances the title screen —
the cheapest test of the leading input hypothesis, and the only row that costs *their* time.

Two documented behaviours on this exact game, on Steam (app 19980, which this install is)
`[reported 2026-09-07]`:

- **Steam Input is reported to make this game crash on launch when controllers are connected.** The
  documented workaround is the game's **"Steam Input Per Game Setting" → `Forced Off`** (right-click →
  Properties), rather than unplugging pads.
- **"The game will fail to launch while the Steam Controller is connected"** — that controller
  specifically is reported incompatible.

**So the most likely bad outcome of the row as written is the game failing to launch** — which is not
"the pad didn't help", but is indistinguishable from it at a glance. That would be a false negative on
the estate's leading input hypothesis, produced by a platform setting rather than by the game.

## The prerequisite to add

> Before plugging anything in: set *Steam Input Per Game Setting* → **Forced Off** in the game's Steam
> properties, and use a plain XInput pad rather than a Steam Controller.

## ✅ And one report that supports the hypothesis being tested

A community report describes **using the A button to advance from the splash screen** while being
unable to navigate menus or play without keyboard and mouse `[reported 2026-09-07]` — a direct, if
second-hand, instance of exactly what the row predicts. The row is testing a live hypothesis, not a
guess.

## ⚠️ A second confounder worth being on the hazards list

**Opening the Steam overlay is reported to make this game ignore all input — keyboard or controller —
until restart** `[reported 2026-09-07]`. That invalidates **any** input experiment here, silently and
totally, not just the pad one.

## ⚖️ One thing I checked and am NOT asking you to act on

Reporting exists that **V-Sync enabled can stop the "Press any button" prompt from displaying**. I do
not think it explains our symptom, and the distinction is the point: that report is about the prompt
not being *drawn*, whereas we measured that the title screen **ignores injected keyboard input and
does not poll DirectInput at all** — a statement about what the game *reads*. A missing prompt on a
screen that still accepts input would not give our result.

Free to eliminate while you are in the options anyway; not a redirection of effort. **Our first-party
measurement outranks all of this**, and nothing here displaces it.

## ⚠️ If a virtual pad is ever substituted for the physical one

A sibling project found this machine carries a **broken ViGEm bus instance** (`ROOT\SYSTEM\0004`, Error
state, pre-existing) `[measured 2026-09-07]`. A ViGEm-based virtual pad would be an unreliable stand-in
**on this machine**, and its failure would again look like a fact about the game. The project's own
`xinput1_3` DLL proxy is a different mechanism and is unaffected.

## Not touched by any of this

The `[PD]` row — why the `xinput1_3` proxy never fires — is unchanged. No public source describes this
game's XInput polling, and the row's own plan (log on **every** `XInputGetState` entry, separating
*never called* from *called but our apply declined*) is still the right, cheapest discriminator.

## Credit

PCGamingWiki contributors; the Steam Community discussion and guide authors for app 19980; GOG forum
contributors; StrategyWiki contributors; Ubisoft Support as quoted in those threads. Added to
`external-research/CREDITS.md`. Read online only; nothing installed or downloaded. Every claim above
is `[reported]` community/wiki material about this game generally, not about our build.
