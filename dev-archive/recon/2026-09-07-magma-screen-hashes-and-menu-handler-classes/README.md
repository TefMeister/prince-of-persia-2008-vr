# 2026-09-07 — Magma screen names are CRC32, and the menu-handler classes are decoded

`/pd`, dev PC, **no launch**. Evidence for
`modding-notes/2026-09-07-screen-names-are-crc32-and-the-state-hash-channel-does-not-exist.md`.

| file | what it is |
| --- | --- |
| `screen-name-hash-sweep.txt` | the load-bearing result: screen names live in the `.MGB` UI files as **CRC32 little-endian**, with 3 positive and 3 negative controls, per-file attribution, and per-section counts |
| `menu-handler-classes-and-hash-channel.txt` | the class-descriptor layout, the four menu-handler classes' descriptors / factories / constructors / vtables, and the state-hash sweep with positive controls |
| `dump_mgb.py` | extracts the `MagmaMgbFile` datablock bodies out of `DataPC.forge → Game Bootstrap` |
| `resolve.py` | builds a CRC32 dictionary from the unpacked exe's identifier strings and resolves constants |
| `scan_handlers.py` | walks named vtable methods and resolves every 32-bit immediate against that dictionary |

## Not committed, deliberately

The `.MGB` bodies and the Steamless-unpacked executable are **game content**. Only counts,
offsets, hashes and layouts are here — interface metadata. Both regenerate:

```
python dump_mgb.py <outdir>                       # needs the game installed
Steamless.CLI.exe <copy of PrinceOfPersia_Launcher.exe>   # v3.1.0.5, atom0s
```

The unpack was verified against the 2026-09-03 record before anything was read from it:
entry point `0x00B076BD`, `.text` entropy 8.00 → 6.61, `CC` padding runs 0 → 32,491. Same
three numbers, different machine, different session.
