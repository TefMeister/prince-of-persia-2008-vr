# Your proxy never frees the real `d3d9.dll` — a game that unloads and reloads it walks straight past you

Filed by: `/sr`, 2026-09-04 (cross-engine sweep; Windows loader behaviour, not engine-specific).
Library write-up:
[techniques → a proxy must free the real DLL on detach](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md#and-it-must-free-the-real-dll-on-detach-or-a-reload-walks-straight-past-it)

## The finding, checked directly in this project's source

`proxy-d3d9/src/proxy.c` loads the real module from the system directory by full path
(`LoadLibraryA(sysdir)`, around line 71) and **contains no `FreeLibrary` call anywhere**
`[inferred-static 2026-09-04, read directly]`. The estate-wide audit that found this read all ten
proxies: **of the eight that load the real system module by path, exactly one releases it.**

## Why that can silently remove your mod

Microsoft's `LoadLibraryA` remarks: *"When no path is specified, the function searches for loaded
modules whose base name matches the base name of the module to be loaded. If the name matches, the load
succeeds. Otherwise, the function searches for the file."*
(<https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya>)

If the game ever `FreeLibrary`s **your** proxy — a startup capability probe, a renderer restart, an
options change — the system copy stays resident under the base name `d3d9.dll`. The game's next
`LoadLibrary("d3d9.dll")` matches **it** by name and succeeds at once. The application directory is never
searched, **your proxy never loads again, and the game runs perfectly without you.**

## The diagnostic signature, which is the part worth remembering

Per launch, the proxy log holds a load, one or two export calls, and an unload within about 100 ms —
and then nothing, while the game visibly reaches gameplay. That reads as "the game crashed my mod" or
"this game must use a different graphics API". It means neither: **you were reloaded past.**

## Prior art, and the fix

ReShade carried this exact defect against one game until commit `74347b91d` (2019-12-19, shipped in
4.5.2), titled *"Fix hooking in Alan Wake"*; the diff's own comment records that freeing the module
reference taken for export hooks *"is necessary for Alan Wake to work"*.
<https://github.com/crosire/reshade/commit/74347b91d7729a6da93040298c6587bb3b786da4>

**Fix: `FreeLibrary` the real module in `DLL_PROCESS_DETACH`.** One line. (The alternative structural
fix is to load a *renamed* original instead of the system one, which is why `XIII2003-vr`'s proxy is
immune — no resident module ever shares its base name.)

**This is latent, not live.** It only bites on a game that probes-and-reloads — so far that is Alan
Wake. It is worth closing anyway, because when it does bite it costs a whole session to
diagnose from scratch, and the symptom points away from the cause.
