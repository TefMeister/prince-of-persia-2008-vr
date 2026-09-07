# 2026-09-07b — The repacked `DataPC.forge` is DEPLOYED (user-approved)

`/pd`, dev PC. **The game was still not launched.** This entry covers a file deployment only.

The `[USER]` row opened on 2026-09-03 — "deploy the validated repacked `DataPC.forge`, or say
no" — was answered **yes** by Tefa on 2026-09-07. Deployed the same session.

## What was deployed

`CR_Debug_1stPerson`'s state-condition list, in `DataPC.forge → Game Bootstrap`:

```
(188 CGST_DebugMode, 189 CGST_DebugModeFPSCamera, 309 CGST_Any)  ->  (309, 309, 309)
```

309 is `CGST_Any`, the don't-care sentinel, so the rule's state gate becomes unconditional.

## It was regenerated, not lifted out of a temp folder

The 2026-09-03 staged file was four days old and sitting in `%TEMP%`. Rather than trust it, the
patch was **regenerated from the currently-installed archive** and then checked four ways:

1. `verify-layout` on the installed archive — `PASS: 30 entries, layout formula holds exactly,
   padding is all zero`.
2. **Full-archive diff**, original vs freshly patched — decompressing and byte-comparing every
   datafile, not spot checks:
   ```
   DIFF  Game Bootstrap  byte-range  0x56a3a3 .. 0x56a3a5  (2 bytes)
   DIFF  Game Bootstrap  byte-range  0x56a3a7 .. 0x56a3a9  (2 bytes)
   2 differing range(s) across 2 entries; 0 checksum failure(s) in b
   ```
   Identical to the 2026-09-03 result.
3. The freshly generated file is **byte-identical to the 2026-09-03 staged file** — an independent
   reproduction of that output, four days and one session apart.
4. Read-back from the **live install after deployment**: `CR_Debug_1stPerson states = (309, 309,
   309)`, and the datafile still splits into **9,684 datablocks**, the same count as before the
   edit. `verify-layout` passes on the deployed file.

`[verified-numerically 2026-09-07, n=1 production edit, full-archive diff + post-deploy read-back]`

## Reverting — one file copy

```
copy "DataPC.forge.bak-2026-09-07-pre-debugcam" "DataPC.forge"
```

The backup sits beside the archive in the game folder, was written before the overwrite, and was
`cmp`-verified byte-identical to the original at the time it was taken. **Nothing else in the
install was touched.**

⚠️ **Steam's "verify integrity of game files" will replace the patched archive**, silently and
without warning, because it no longer matches Steam's manifest. If the debug camera stops working
for no apparent reason, check that first — and note this also means the deployment is trivially
undoable by anyone, including by accident.

## ⚠️ What this does NOT establish, and what to actually watch for

**Only the state-list half of the recorded mod is done.** The 2026-09-02 plan was "rewrite the
state list **and raise its priority**". The priority half has never been located and was not
touched. So the honest position is that this edit makes `CR_Debug_1stPerson` *eligible* in every
state; it does not make it *win*. `[hypothesis]`

The next launch decides it, and the outcomes are distinguishable:

| what you see | what it means |
| --- | --- |
| first-person camera in normal play, `CAM FPS` behaviour | the state list was the only gate — the mod works with no code patch at all |
| camera unchanged, game otherwise normal | the rule is eligible but **losing to a higher-priority rule**; the priority field is the next target, and it is a static hunt, not a live one |
| camera flickers or fights between first and third person | two rules now both satisfy their conditions — that is the priority problem showing itself directly, and it is *informative*, not a failure |
| crash or hang on load | the archive edit is not being read as intended; revert with the one copy above and say so, because the full-archive diff says this should not happen |

**A crash would be the surprising outcome**, given every block's checksum verifies and the layout
formula holds on the deployed file. Say which of the four happened — the middle two are the
interesting ones and they are easy to confuse.

## Status of the debug-menu line

Unchanged and unaffected. This route was always independent of it; 2026-09-07's earlier entry
closed the hash channel and left item enumeration open, and none of that matters if the camera
simply appears.
