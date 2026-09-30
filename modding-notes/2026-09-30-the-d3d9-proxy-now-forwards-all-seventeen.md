# 2026-09-30 — the d3d9 proxy now forwards all seventeen

`/pd`, dev PC. **The game was not launched, and nothing here has been run in the game.**

## What changed

Our `d3d9.dll` exported only `Direct3DCreate9`. Windows' own `d3d9.dll` exports seventeen functions.
On Dead Space 2 a game asking for one of the other sixteen got NULL and crashed at start
`[verified-live 2026-09-14, n=1, dead-space-2-vr]`. Prince of Persia runs today, so here the defect was
latent.

- Dead Space 2's pass-through stubs (`src/thunks.c`) are ported unchanged. Each one saves every
  register, logs its first call, restores everything and jumps to the real function, so it is correct
  for any argument list, documented or not.
- Exports now match `SysWOW64\d3d9.dll` exactly: **17 of 17** `[compile-verified 2026-09-30]`.
- `test/thunk_selftest.c` (also from Dead Space 2) loads our DLL in a plain 32-bit program and calls
  three of the stubs: all return, the stack is balanced, and all 16 resolved against the real DLL
  `[verified-numerically 2026-09-30]`. It now runs from `build-tests.sh`.
- Before changing anything, the installed file was checked against a rebuild of the old source: same
  source, differing only in 8 timestamp bytes `[verified-numerically 2026-09-30]`.

## Installed

Dev PC: `d3d9.dll` `c89fb8a93d98` (63,488 B); the previous one is in
`Prince of Persia\_backup-2026-09-30-pd\`. Recorded in `deployed/DESKTOP-V8GTSIR/`. The home PC still has
the one-export build; a reminder is raised in `owed/HOME/`.

## What is NOT established

- Whether this game ever calls any of the sixteen. The log now answers that: any `THUNK:` line in
  `pop2008_vr_proxy_log.txt` after a launch names the function it asked for.
- That nothing else about the start-up changed. The stubs only run if the game asks for them, but a
  launch is the proof.

## Next launch

Nothing extra to do: read `pop2008_vr_proxy_log.txt` after any launch. `forwarding table built: 16 of
16 resolved` means the stubs are ready; a `THUNK:` line means the game used one; a start-up crash that
was not there before means stop and restore the backup.
