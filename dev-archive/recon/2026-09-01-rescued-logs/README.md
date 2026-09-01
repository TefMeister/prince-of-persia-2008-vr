# Rescued proxy log — Prince of Persia (2008)

`pop2008_vr_proxy_log.txt` was written by **our own** `d3d9.dll` proxy during the 2026-08-25 live
test and existed **only** in the game install folder, which is not backed up and which Steam may
overwrite. Copied into git on 2026-09-01 by a `/pd` session.

This is a log our tooling generated. It is not game content.

It records: proxy load, the real system `d3d9.dll` resolving, `Direct3DCreate9` called once with
`SDKVersion=0x20` returning a valid interface pointer, and a clean unload. Its value now is as the
primary evidence that this game creates a **plain D3D9** device rather than D3D9Ex — which
constrains any future VR compositor submission path.
