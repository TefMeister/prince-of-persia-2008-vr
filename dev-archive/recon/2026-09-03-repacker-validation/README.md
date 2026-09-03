# `forge_write.py` validation record — 2026-09-03

`/pd`, dev PC. **The game was not launched.** Everything here is evidence produced by running the
repacker (`dev-archive/tools/forge/forge_write.py`) against the shipped `.forge` archives, read-only
on the archives themselves — every write went to a scratch directory outside the game install.

**No game content is stored here.** These are tool logs — byte counts, offsets, diff summaries,
checksums — the same category as an export-name dump. The archives and the patched artifact stay
outside git.

## Files

| file | what it holds |
| --- | --- |
| `selftest-log.txt` | the null-op acceptance test (`selftest-noop`) on three archives, up to 752 MB — patches an already-raw block to its own value and requires byte-identical output |
| `production-edit-diff-log.txt` | the actual recorded mod applied to a scratch copy of `DataPC.forge`, then a full-archive decompression diff against the original — every OTHER datafile byte-identical, the touched one differing at exactly the intended 4 bytes, zero checksum failures |

## Headline results

- **Null-op self-test: byte-identical output on all three archives tested** (3.6 MB, 64.5 MB,
  752 MB), exercising the full pipeline (locate block → decompress-or-copy → re-store raw → splice
  → shift downstream offsets) with a genuine no-op edit.
- **The real production edit** — `CameraRule "CR_Debug_1stPerson"`'s state-condition list, rewritten
  from `(188, 189, 309)` to `(309, 309, 309)` — applied to a scratch copy of `DataPC.forge` (64.5 MB,
  30 entries). Full-archive diff against the original: **29 of 30 entries byte-for-byte identical**;
  the touched entry (`Game Bootstrap`) differs at **exactly the two byte ranges the edit touched**
  (2 bytes each, since 2 of each 4-byte field's bytes happened to already match); **zero checksum
  failures** across every block of the entire patched archive.
- The patched archive's own layout re-verifies cleanly (`verify-layout`), and reading the patched
  bytes back confirms both fields now decode to `309`.

## Method note: a real off-by-one caught by the tool's own safety check

The first patch attempt used hand-counted hex offsets (`0x56a3a4`/`0x56a3a8`) and was refused:
`forge_write.py` compares the bytes actually present against the `old_bytes` the caller expects, and
refuses to guess on a mismatch. The true offsets, found programmatically by searching the
decompressed block for the datablock's own name string and then for the two consecutive `u32`
fields, are `0x56a3a3`/`0x56a3a7` — one byte earlier. Recorded because it is exactly the failure mode
the check exists to catch, and it caught it on the first real use.

## What is NOT established

- **The archive was never deployed to the actual game install.** Deployment was attempted following
  this project's DLL-deployment precedent (dated backup, one-step revert) and was **blocked by the
  session's own safety system** — appropriately: a repacked core data archive is a different risk
  class from an optional proxy DLL. The patched artifact and the exact deploy command are recorded
  in `status/prince-of-persia-2008-vr.md` as a `[USER]` action.
- **The "raised priority" half of the recorded mod is not implemented.** ENGINE-DOSSIER.md's
  mod-shaped consequence bullet names two changes — the state-list rewrite (done, validated) and "a
  raised priority" (not located, not touched). Whether the state-list rewrite alone is sufficient for
  `CAM FPS` to actually win over sibling rules in `FunkyCameras` is untested and needs the game
  running either way.
- **This tool has not been used to edit anything but same-length 4-byte fields.** A length-changing
  edit (e.g. adding a datablock) would need the datablock table (FORMAT.md §5) rewritten too — out of
  scope, not needed for the recorded mod, and not attempted.
