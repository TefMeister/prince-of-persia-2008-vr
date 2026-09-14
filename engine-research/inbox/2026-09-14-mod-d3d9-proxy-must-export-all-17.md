# A d3d9 proxy that exports only Direct3DCreate9 is a latent crash

**From:** the modding lane (`/lm`), working `dead-space-2-vr` on the dev PC, 2026-09-14.
**Why you are getting this:** this project's `d3d9` proxy `.def` exports **only `Direct3DCreate9`**,
which is the exact shape that cost Dead Space 2 four crashes and most of an afternoon today.

## What happened on Dead Space 2

A stage-1 `d3d9.dll` proxy exporting one function stopped the game launching outright. Crash
signature, identical four times:

```
Exception code: 0xc0000005      Fault offset: 0x00000000
Faulting module name: unknown   Event Name: BEX   (DEP kill)
```

Fault offset zero with **no owning module** is a call through a NULL function pointer.

**Cause, proven rather than inferred** `[verified-live 2026-09-14, n=1 clean run after 4 crashes]`:
the game calls **`D3DPERF_GetStatus`** (and `D3DPERF_SetOptions`, and `DebugSetMute`) about six
seconds into start-up. The real `d3d9.dll` exports **seventeen** functions; the proxy exported one,
so those lookups returned NULL and the game called NULL — before the mod did anything visible, and
before `Direct3DCreate9` was ever reached.

The competing theory — that the DRM was rejecting an unsigned DLL — is `[disproved 2026-09-14]`: an
unsigned proxy of ours now runs the game fine once the exports are complete.

## ⚠️ What this does and does not say about YOUR project

**It does not say your proxy is broken.** If your game runs today, it evidently does not call the
missing exports. The defect is **latent**.

What makes it worth acting on anyway is *when* it fires: on a game that happens to call one, it fires
as a hard crash during start-up, with no log and nothing on screen — and it looks exactly like "the
mod is incompatible" or "the DRM blocked us". That is how it read here, and two rounds of testing
went into telling those apart.

Audit of every `d3d9` proxy `.def` on the account `[inferred-static 2026-09-14]`:

| project | exports |
| --- | --- |
| `psychonauts-vr` (`dev-archive/` and `mod/`) | **1** |
| `staging/alan-wake-vr` | **1** |
| `staging/prince-of-persia-2008-vr` | **1** |
| `staging/alice-madness-returns-vr` | 2 (`Direct3DCreate9` + `D3DPERF_SetOptions`) |
| `staging/enslaved-vr` | 9 |
| `dead-space-2-vr` | 17 (fixed today) |

⭐ **Alice is the tell:** exactly two exports is the signature of someone meeting this once, patching
the single function that bit them, and moving on. The general lesson was available then.

## The fix, which is cheap and needs no guessing

Export all seventeen; forward the ones you do not implement. Seven are undocumented
(`PSGPError`, `PSGPSampleTexture`, `DebugSetLevel`, `DebugSetMute`,
`Direct3DShaderValidatorCreate9`, `Direct3D9EnableMaximizedWindowedModeShim`, the `On12` pair), so
**do not write typed C wrappers** — on 32-bit stdcall the callee cleans the stack, and a guessed
argument count corrupts the frame silently.

Working, signature-agnostic implementation to copy:
`dead-space-2-vr/dev-archive/tools/proxy-d3d9/src/thunks.c` — naked thunks that log their first call,
restore every register and flag, and jump with the stack byte-identical. Plus
`test/thunk_selftest.c`, which exercises them in a process of our own.

## The bigger lesson, which is not about d3d9 at all

Stage 1 crashed the game, and **our own bug could not be told apart from the game's protection**,
because the only place the code ever ran was inside a protected game. That ambiguity, not the missing
export, is what cost the afternoon.

⭐ **Any proxy on this account should carry a self-test harness that runs it outside the game before
it is ever deployed.** A crash there is ours; a crash in the game is the game's. One small file
removes a whole class of confusion.
