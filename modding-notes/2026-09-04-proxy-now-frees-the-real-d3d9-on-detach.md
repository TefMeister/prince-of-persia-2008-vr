# The proxy now frees the real `d3d9.dll` on detach

`/pd`, no launch. Closes an `/sr` estate-wide inbox drop:
`engine-research/inbox/2026-09-04-sr-proxy-never-frees-the-real-dll.md`.

## The finding, read directly in this project's source

`staging/prince-of-persia-2008-vr/proxy-d3d9/src/proxy.c` loaded the real system `d3d9.dll` by full
path (`LoadLibraryA(sysdir)`, `load_real_dll()`) but `DllMain`'s `DLL_PROCESS_DETACH` branch only
closed the log file — it never called `FreeLibrary` on the handle. `[verified-live 2026-09-04, read
directly]`. The `/sr` sweep that found this checked all ten proxies across the estate that load the
real module by path and found only one that releases it.

## Why it matters

If this game ever `FreeLibrary`s our proxy — a startup capability probe, a renderer restart, an
options change — Windows' `LoadLibraryA` (no path given) matches the still-resident system copy by
base name first, and the game's next `LoadLibrary("d3d9.dll")` succeeds against **that**, never
searching the application directory again. The mod would stop loading with no error and no log
entry after the reload, and the symptom (a clean load/unload inside ~100ms, then nothing, while the
game visibly reaches gameplay) reads as a crash or an API mismatch — not what it actually is.
ReShade shipped this exact defect against Alan Wake until commit `74347b91d` (2019-12-19, "Fix
hooking in Alan Wake").

**Honest scope: this is latent, not observed.** Nothing in this project's own live testing (one
clean launch, 2026-08-25) has hit a reload. It was worth fixing anyway because it is a one-line
change and, when it does bite, it costs a whole session to diagnose from the wrong end.

## The fix

`DLL_PROCESS_DETACH` now calls `FreeLibrary(real_d3d9)` before closing the log, matching the ReShade
fix. `[compile-verified 2026-09-04]` — built with the project's own toolchain
(`i686-w64-mingw32-clang`, matching `build.sh`'s flags; that script's hardcoded toolchain path is
dev-PC-specific, so this session invoked the compiler directly with the same arguments), export
table checked afterward (`Direct3DCreate9` still the sole export, ordinal 1).

## Deployment

This machine's install (`C:\Steam\steamapps\common\Prince of Persia\`) is a clean reinstall dated
2026-08-29 — postdating the 2026-08-25 live-verify recorded in the dossier — and had **no**
`d3d9.dll` present at all. So the fixed build was copied in directly; there was nothing to back up
and no existing proxy to overwrite. `pop2008_vr_proxy_log.txt` will appear in the install root on
first launch, same as before.

## What is NOT established

Whether this game ever actually triggers a probe-and-reload is unknown and was not tested (no
launch). The fix removes the whole failure class regardless, at zero behavioral cost on a game that
never reloads.

## Evidence / source

- `staging/prince-of-persia-2008-vr/proxy-d3d9/src/proxy.c` (the fix)
- `engine-research/inbox/2026-09-04-sr-proxy-never-frees-the-real-dll.md` (drained, this session)
- ReShade fix: https://github.com/crosire/reshade/commit/74347b91d7729a6da93040298c6587bb3b786da4
