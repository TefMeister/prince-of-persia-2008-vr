# The XInput proxy now counts entries, not just applies — so a zero can be read

`/pd`, dev PC, 2026-09-08. **The game was not launched. Nothing here has been run.**

## The problem this fixes

The board's `⭐` row: `proxy-xinput/` loads, maps the shared block and passes its
host checks, but `applied_pad` stayed **0** across every launch — and *nobody could
say what that meant*. A zero there has two completely different causes:

1. **the game never called `XInputGetState`** — a fact about the game, and the one
   the 2026-09-07e session recorded ("the game **never** calls `XInputGetState`,
   even with a controller connected"); or
2. **it called and our apply declined** — a fact about our DLL.

Only the first is evidence about the game. The old build could not tell them apart,
because the only counter incremented on the *apply* path. That is the same defect
class as the 2026-09-07h `applied_mouse` bug: **a counter that cannot distinguish
its own failure modes is not evidence.**

## What changed

`proxy-xinput/src/proxy.c` now counts **entries** into all three exports, with
interlocked counters (XInput is polled from whichever thread renders):

- `XInputGetState` entries, and separately those with `idx == 0`;
- `XInputSetState` and `XInputGetCapabilities` first entries — a game that probes
  capabilities, gets nothing, and therefore never polls state would otherwise be
  invisible.

Logging is bounded on purpose: the **first** entry into each export is logged
immediately, then a heartbeat every 600 `GetState` entries (~10 s at 60 Hz). Logging
every entry would write megabytes and slow the game; logging only the first would
hide a poll that starts late, which is precisely what a title screen ignoring input
might do.

It also logs, **once**, why the first pad-0 entry declined — `state` NULL, block not
mapped, `enabled`, `pad_force`, and the real `hr` — so "declined" is never just a
category.

On unload it prints a verdict:

```
=== unloading; XInputGetState entries=N (idx0=M) SetState=.. GetCaps=.. applied_pad=K ===
=== VERDICT: <one of four> ===
```

## The verdict is a pure function, and it is tested

Following the module's own idiom (*"the apply functions are PURE and take plain
buffers, so they are tested on the host with no game, no device and no launch"*),
the decision logic lives in `proxy-dinput8/src/input_inject.c` as
`pop_pad_verdict(calls, calls_idx0, applied)` returning one of:

| verdict | meaning |
| --- | --- |
| `POP_PAD_NEVER_CALLED` | no entry at all — **the game does not poll XInput on this path** |
| `POP_PAD_CALLED_OTHER_PAD` | polled, but never index 0 |
| `POP_PAD_DECLINED` | polled pad 0, applied nothing — our side |
| `POP_PAD_INJECTED` | the pad path works |

`input_inject_test.c` gained **20 checks** covering every row, both "a zero apply
must never read as success" cases, negative/impossible counter values, and that the
four verdict names exist and are distinct. **58 checks, 0 failures** (was 38).
`[verified-numerically 2026-09-08]`

## Builds and deployment

- `xinput1_3.dll` — PE32 i386, clean under `-Wall -Wextra`, export table still
  pinning ordinals **2/3/4 by ordinal** (the exe imports by ordinal; a name-only
  table would not resolve and the game would not start). `[compile-verified 2026-09-08]`
- `dinput8.dll` rebuilt too, because it links the same `input_inject.c`. **This
  incidentally closes a stale deploy**: the installed `dinput8.dll` was still the
  pre-2026-09-07h build, i.e. it still had the `applied_mouse` counter that rose on
  every poll whether or not anything landed. The 2026-09-07h note said the fix
  "takes effect on the next launch" — it would not have, because the fixed binary
  was never deployed.
- Both deployed with dated backups (`*.bak-2026-09-08`), `cmp`-verified against the
  fresh builds, and `deployed.sh record` re-run.

## Reading the next launch

Look at `pop2008_xinput_log.txt` beside the exe.

| log says | conclusion |
| --- | --- |
| no `ENTERED` line at all, `VERDICT: NEVER CALLED` | **confirms 2026-09-07e**: the game genuinely does not poll XInput. The virtual pad is then a dead end and unattended launch needs a different route — the `dinput8` path or the launcher-side `BM_CLICK`. |
| `XInputGetCapabilities ENTERED` but no `GetState` | the game probes for a pad, is told there is none, and gives up. `pad_force=1` should then be enough — and that is a one-flag retest. |
| `GetState ENTERED`, `VERDICT: DECLINED` | our bug, not the game's. The decline line names which precondition failed. |
| `VERDICT: INJECTED` | the pad path works and unattended launch-to-gameplay is unblocked. |

⚠️ **Prerequisite before any pad test, from `/gr`'s 2026-09-07 drop:** set Steam
Input Per Game Setting to **Forced Off** and do not use a Steam Controller — this
game is reported to crash on launch with Steam Input and controllers connected, and
a crash is indistinguishable from a failed test at a glance. Also: opening the Steam
overlay is reported to make the game ignore all input until restart, which would
invalidate any input experiment silently.

## What is NOT established

Nothing here says whether the game polls XInput. It says that **after the next
launch the log will answer that question unambiguously**, which it previously could
not. `[compile-verified 2026-09-08]`
