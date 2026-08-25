# M0 static recon — 2026-08-25

Pure file-based static analysis of `PrinceOfPersia_Launcher.exe` (the actual game binary, per
the install's registry key — no process was launched or attached to). Tools: `file`,
`objdump`/`strings` (llvm-mingw, i686 target — 32-bit).

## PE header
```
file format coff-i386
PE32 executable for MS Windows 4.00 (GUI), Intel i386, 9 sections
```
12.7 MB on disk.

## Section table — standard MSVC layout, nothing unusual
```
Idx Name          Size     VMA      Type
  0 .text         00923ddc 00401000 TEXT
  1 .rdata        000d948a 00d25000 DATA
  2 .data         0010f800 00dff000 DATA
  3 .tls          00000089 00fa8000 DATA
  4 _RDATA        00001d18 00fa9000 DATA
  5 .data1        00000540 00fab000 DATA
  6 .rsrc         00153768 00fac000 DATA
  7 .extra        00001288 01100000
  8 .bind         00053800 01102000 DATA
```
No giant opaque blob, no renamed/obfuscated sections — a clean contrast with Burnout
Paradise's Denuvo `.trace` blob and Mad Max's `.xpdata` blob.

## Import table (full DLL list)
```
KERNEL32.dll, USER32.dll, GDI32.dll, ole32.dll, OLEAUT32.dll, WS2_32.dll, COMCTL32.dll,
d3d9.dll, d3dx9_39.dll, DINPUT8.dll, XINPUT1_3.dll, binkw32.dll, WININET.dll, iphlpapi.dll,
ADVAPI32.dll, SHELL32.dll, EAX.DLL, DSOUND.dll, WINMM.dll
```

## Renderer strings
```
Direct3DCreate9   <- present
Direct3DCreate9Ex <- NOT present (plain D3D9 only, not D3D9Ex)
```

## Engine identification strings
```
AnvilScript
CustomAnvilBrush
startanvil
Dare
```
Confirms **Anvil engine** (Ubisoft's proprietary engine, later famous via Assassin's Creed).

## DRM / anti-tamper search — all negative
```
denuvo / securom / starforce / uplay / ubisoft connect / ubi launcher / link2 / activation
  -> no DRM-related hits. The many "*Activation*" string hits are all gameplay logic
     (ActivationPlate, TrapActivation, ZoneActivationType, PoisonActivationEvent, etc.) --
     unrelated to licensing/DRM.
```

## Console / debug menu strings
```
"- unable to open console device"
GetConsoleCP / GetConsoleMode / GetConsoleOutputCP / WriteConsoleA / WriteConsoleW
consoleout
DebugMenu
DebugMenuHandler_m
```

## Embedded default command line (one literal string in the exe)
```
/world:POP0WORLD /fast /shadows:on /lightmode:normal /fardist:1500 /noconsole /bink:on
/mission:pop0_root /startupmenu:on /localbigfile
```

## What this means for the project

Cleanest DRM/injection situation in this portfolio so far — no Denuvo, no anti-cheat, no
third-party launcher requirement (unlike Burnout Paradise's EA App wall). D3D9 (non-Ex)
renderer confirmed, Anvil engine confirmed, a real debug menu and console system both appear
present in the binary. Full synthesis in `ENGINE-DOSSIER.md`.

## Gap noted, not a finding
No `/game-research` external-research sweep has run for this project yet (unlike Mad Max and
Burnout Paradise, which both had rich parallel research land during their M0 sessions). Community
prior art for this game is currently unknown.
