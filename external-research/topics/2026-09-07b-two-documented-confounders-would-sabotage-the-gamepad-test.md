# Two documented Steam confounders would sabotage the `[USER]` gamepad test — and one community report supports the hypothesis it is testing

**Status:** 🆕 new · **Priority:** high for its cost — it is aimed squarely at the one row that
**needs the user**, and it could turn a wasted ask into a conclusive one.

## Why this was looked up

The board's `[USER]` row:

> ⭐ **TRY A GAMEPAD AT THE TITLE SCREEN — the cheapest test of the leading input hypothesis, and only
> you can plug one in.** The exe imports `XInputGetState`/`SetState`/`GetCapabilities` and reads **no**
> key state from the Windows message queue at all; the title screen ignores every injected keyboard
> route and does not poll DirectInput. A console port of this vintage waiting on a pad fits
> everything seen.

Before the user is asked to do anything, it is worth knowing what the public record says about a
gamepad and this exact game on this exact platform. This install is **Steam, app 19980**, and the
project already knows Steam runs `Launcher\Launcher.exe -uplay_steam_mode` rather than the game's own
launcher — so Steam-specific behaviour is in scope, not incidental.

## ✅ 1. Support for the hypothesis

A community report describes being able to **use the A button to advance from the splash screen**,
while being unable to navigate menus or play without keyboard and mouse `[reported 2026-09-07]`. That
is a direct, if second-hand, instance of the thing the row predicts: **a pad gets past the screen that
keyboard cannot.**

It is one report and it is not from us, so `[reported]` — but it means the row is testing a live
hypothesis rather than a guess.

## 🚨 2. The confounder that matters most: Steam Input can stop the game launching at all

Two documented behaviours, both about **having a controller connected**:

- **"The game will fail to launch while the Steam Controller is connected"** — the Steam Controller
  specifically is reported incompatible.
- More generally, **Steam Input is reported to make this game crash on launch when controllers are
  connected**. The documented workaround is to set the game's **"Steam Input Per Game Setting" to
  `Forced Off`** in its Steam properties (right-click → Properties), rather than unplugging pads.

`[reported 2026-09-07]`

**Why this is the important one:** the `[USER]` row's instruction is *plug a pad in and see if it
advances the title screen.* If Steam Input is not forced off first, a plausible outcome is **the game
failing to launch or crashing** — which is not "the pad didn't help", but which is exactly what it
would look like. That is a false negative on the estate's **leading input hypothesis**, produced by an
unrelated platform setting, in the one row that costs the user's time rather than a session's.

**So the row should carry a prerequisite:** set *Steam Input Per Game Setting* → **Forced Off** before
plugging anything in, and prefer a plain XInput pad over a Steam Controller.

## ⚠️ 3. A second confounder for any input test on this game

**Opening the Steam overlay is reported to make the game ignore all input — keyboard or controller —
until it is restarted** `[reported 2026-09-07]`. This project already records that the game does not
play nicely with the overlay (the developers reportedly disabled it in-game to make things work).

That matters beyond the pad row: **any** input experiment here is invalidated if the overlay has been
opened during the session, and the failure is silent and total. Worth being on the board's hazards
rather than discovered once.

## ⚖️ 4. An alternative explanation for the title screen — weaker than it first looks, but free

PCGamingWiki-adjacent reporting says: **with V-Sync enabled, the "Press any button" prompt may not
display**, preventing progress past the first screen `[reported 2026-09-07]`.

**I do not think this explains our symptom, and the distinction is the useful part.** That report is
about *the prompt not being drawn*. Our measured symptom is different and stronger: the title screen
**ignores injected keyboard input and does not poll DirectInput at all** `[verified-live 2026-09-07]`
— which is a statement about what the game *reads*, not about what it *draws*. A missing prompt on a
screen that still accepts input would not produce our result.

So: **not a competing explanation**, but a free config toggle that costs nothing to eliminate, and the
two could co-occur on a machine. Worth one line, not a redirection of effort.

⚠️ Our own first-party measurement outranks all four of these community reports. Nothing here should
displace it.

## 5. What this does *not* answer

The board's `[PD]` row — *why does the `xinput1_3` virtual-pad proxy never fire, when `applied_pad`
stayed 0 and the game was never observed calling `XInputGetState`?* — is untouched by any of this. No
public source describes this game's XInput polling cadence, and the row's own plan (log on **every**
`XInputGetState` entry, to separate *never called* from *called but our apply declined*) remains the
right and cheapest discriminator. That is static work, not a research question.

⚠️ One caution if a **virtual** pad is ever substituted for the physical one as a cheaper test: a
sibling project found this machine has a **broken ViGEm bus instance** (`ROOT\SYSTEM\0004` in an Error
state, pre-existing) `[measured 2026-09-07]`. A ViGEm-based virtual pad would therefore be an
unreliable stand-in *on this machine* — and the resulting failure would again look like a fact about
the game. The project's own `xinput1_3` DLL proxy is a different mechanism and is unaffected by that
fault.

## The concrete next steps

1. **Before the `[USER]` test:** set *Steam Input Per Game Setting* → **Forced Off**, and use a plain
   XInput pad rather than a Steam Controller. Free, and it removes the most likely false negative.
2. **Do not open the Steam overlay** during any input session on this game; if it has been opened,
   restart before drawing conclusions.
3. **Optionally** toggle V-Sync off while there — free, and it eliminates the prompt-rendering report
   even though it probably does not describe our symptom.
4. The virtual-pad `[PD]` row is unchanged and stays the right next static job.

## Sources and credit

All read online; nothing installed or downloaded.

- **PCGamingWiki contributors** — the Prince of Persia (2008) page (V-Sync/prompt, overlay and
  controller notes). <https://www.pcgamingwiki.com/wiki/Prince_of_Persia_(2008)>
- **Steam Community discussion and guide authors** for app 19980 — the Steam Input `Forced Off`
  workaround, the Steam Controller launch failure, and the splash-screen A-button report.
- **GOG forum contributors** — corroborating controller-behaviour reports.
- **StrategyWiki contributors** — the game's control reference.
- **Ubisoft Support**, as quoted in those threads (reset keyboard/mouse to default; disable Steam
  controller override).

## Honest limits

Every item in §1–4 is **`[reported]`** — community and wiki reporting about this game generally, not
about our build or our machine, and none of it is first-party. Our own measurements (the import
table, the message-queue read, the DirectInput polling) are stronger and stand unchanged. What this
topic changes is **the conditions under which the `[USER]` test should be run**, not what the test
means.


---

## 👀 Outcome — reviewed, not yet exercised (2026-09-08)

Folded in by `/gr` on 2026-09-08 from `external-research/inbox/`.

Both confounders are **folded into the project's `ENGINE-DOSSIER.md` and cited** in the note
covering the XInput proxy work. **No gamepad test has been run**, so neither has been observed
first-hand on this game: both stay `[reported]`, and the project's own measurements would outrank
them if the two ever disagreed.

⚠️ **The `[USER]` gamepad row this topic was written to protect no longer exists.** It was
deleted on 2026-09-07 under the standing "every install stays a dev build" rule. That does not
retire the topic — the Steam Input "Forced Off" prerequisite and the Steam-overlay-kills-input
hazard apply to *any* future pad test on this title, and the cost of learning them the hard way is
the same as it ever was. It does mean **nothing is currently blocked on this**, so it is reference
material rather than a pending action.
