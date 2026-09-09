# The forge patch replays onto a fresh install, byte for byte

**2026-09-09, home PC (`RTX`), no launch.**

## What happened

The home PC re-downloaded Prince of Persia to `D:\SteamLibrary`, which left a **stock**
`DataPC.forge` (64,552,960 B) where the dev PC has the patched one (64,575,488 B). The question
was whether the mod could be reproduced there from what is in git, or whether the patched archive
would have to be copied between machines.

It reproduces. All four recorded edits were replayed onto the home machine's own stock archive in
a single `forge_write.py patch` run:

```
--edit 0x56a3a3:bc000000=35010000   # state list -> 309   (2026-09-07b)
--edit 0x56a3a7:bd000000=35010000   # state list -> 309   (2026-09-07b)
--edit 0x56a3d2:3380f7c0=05412a84   # CameraHolder target (2026-09-08)
--edit 0x56a3eb:3380f7c0=05412a84   # TransitionSpec back-reference (2026-09-08)
```

Output sha256 `52a27251cc0a30b1362f467c7874e465bebcab2594ca6f834339854377f401bc`, 64,575,488 B —
**exactly the dev PC's recorded hash.** `[verified-numerically 2026-09-09]`

## Why that is worth writing down

Two separate things fall out of it, and only one of them was being asked.

1. **The patch is portable.** Nothing about it depends on the machine, the install path, or the
   order the two edit rounds were applied in — the 2026-09-08 repoint was originally applied on
   top of an already-patched archive and here it went on in the same pass as the state list, to
   the same bytes.
2. **Both machines hold the same game build.** A hash equality on a 64 MB repacked archive is not
   something two different game versions produce. That was not the goal and it is the more
   durable fact: it means any future byte offset recorded on one machine is valid on the other.
   `[verified-numerically 2026-09-09, n=1 archive]`

## Checked the same four ways as the original deployment

- `verify-layout` PASS on the home stock archive before touching it (30 entries, layout formula
  exact, padding all zero);
- full-archive `diff`: **exactly the 4 intended byte-ranges across 4 entries, 0 checksum failures**;
- read back from the **installed** file after deploying, through `camera_rules.py` — an
  independent code path rather than a re-print of the patch buffer: `CR_Debug_1stPerson ->
  Parent Ground Cam`, 380 `CameraRule` blocks, all 380 holding a `CameraHolder`;
- backup `DataPC.forge.bak-2026-09-09-stock` written and `cmp`-verified before the overwrite.

⚠️ Steam's file verification will silently replace the patched archive, on this machine as on the
other. The stock backup beside it is the one-copy revert.

## The proxies, and why their hashes deliberately do NOT match

`d3d9.dll`, `dinput8.dll` and `xinput1_3.dll` were rebuilt from `origin/main` and deployed, and
their hashes are **not** the dev PC's. That is the fix, not the problem: all three `build.sh`
lacked `-Wl,--no-insert-timestamp`, so two back-to-back builds of identical source differed in 2
bytes and the "rebuild and compare the hash" check could not work here at all. The flag is added;
two builds now differ in **0** bytes. `[verified-numerically 2026-09-09]` The dev PC should rebuild
and redeploy, after which both machines match outright.

⚠️ `pop_vr.ini` was left **absent** on the home PC. The dev PC's copy is not in git and could not
be fetched; `pop_windowed_load_cfg()` documents missing-file ⇒ defaults (enabled, 1280x720), so
absent is functionally the dev PC's configuration — and 1280x720 is what `MACHINES.md` wants
pinned on that 21:9 monitor anyway.

## Nothing here was run

Both `[FLAT]` camera rows are now runnable on the home PC as well as the dev PC. Neither has been
run. The four distinguishable outcomes are unchanged and live in
`2026-09-08-the-holder-decides-and-cam-fps-reads-the-pad-itself.md`.
