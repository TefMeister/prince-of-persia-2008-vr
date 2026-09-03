# The `.forge` repacker is built and validated — deployment to the install is blocked, and that's correct

**Session:** `/pd`, dev PC, 2026-09-03. **The game was not launched, and nothing has been run.**
Everything below is either a static tool built and tested against files already on this disk, or a
deployment attempt that was refused by the session's own safety system before it touched anything.

## What this closes

ENGINE-DOSSIER.md §6 has recorded, since 2026-09-02, a complete data-only mod: rewrite `CameraRule
"CR_Debug_1stPerson"`'s state-condition list from `(188 CGST_DebugMode, 189
CGST_DebugModeFPSCamera, 309 CGST_Any)` to `(309, 309, 309)` with a raised priority, and the shipped
`PopMarketingCamera "CAM FPS"` runs in normal play with no code patch. It was blocked on one thing:
the per-block `u32` checksum, solved earlier the same session (Adler-32 seeded 0). This entry is
what "no remaining format unknown" turned into — an actual repacker, and the actual patch, built and
checked as thoroughly as I know how to check it without launching the game.

## The tool: `dev-archive/tools/forge/forge_write.py`

Patches a same-length byte range inside a named datafile's decompressed payload and writes a
**complete new archive**. It never patches in place and never opens its own input for writing.

**Why a full rewrite rather than a surgical patch.** The target field sits inside a 32 KiB block
that is stored LZO2A-compressed (9,290 bytes for 32,768 uncompressed). There is no encoder here —
only the decoder `forge.py` already has — so the edited block cannot be recompressed to fit its old
slot. The format's own escape hatch is legal: *"a block whose two sizes are equal is stored raw."*
Re-storing the edited block raw makes it larger, which means everything after it in the archive
shifts, the touched datafile's declared size grows in three places at once (file table, name table,
its own inline descriptor — `forge.py`'s own reader cross-checks these three against each other),
and every later datafile's `data_offset` shifts by the aligned growth.

**The layout this depends on was verified empirically before writing a line of the splice logic,**
not assumed from the format doc: entries are laid out in the archive in the same order as their
index, and for every one of the 29 consecutive pairs in `DataPC.forge`,
`next.data_offset == align_up(this.data_offset + PAYLOAD_OFF + this.size, 0x800)` holds exactly,
with the gap bytes always zero. `verify_layout()` re-checks this on whatever archive the tool is
pointed at, every run, and refuses to patch if it doesn't hold.

## Validation

**Null-op self-test.** `selftest-noop` finds an already-raw-stored block, patches 4 bytes to their
own existing value, and runs the full pipeline (locate → decompress-or-copy → re-store raw → splice
→ shift downstream offsets) with delta 0. Requires byte-identical output to the source.
`[verified-numerically 2026-09-03, n=3 archives]` — passed on `DataPC_Default.forge` (3.6 MB),
`DataPC.forge` (64.5 MB, the archive holding the real target), and `DataPC_HC.forge` (752 MB).

**The real production edit**, applied to a scratch copy of `DataPC.forge` and never the installed
file: the two state-condition fields, changed from `188`/`189` to `309`/`309`. Checked by
decompressing and byte-diffing **every datafile in the entire 64.5 MB archive** against the
original — not spot checks:

```
DIFF  Game Bootstrap       byte-range       0x56a3a3 .. 0x56a3a5  (2 bytes)
DIFF  Game Bootstrap       byte-range       0x56a3a7 .. 0x56a3a9  (2 bytes)

2 differing range(s) across 2 entries; 0 checksum failure(s) in b
```

**29 of 30 datafiles byte-for-byte identical. The touched one differs at exactly the intended
bytes — 2 bytes per field, because 2 of each 4-byte value's bytes happened to already match — and
nowhere else.** Every block's Adler-0 checksum in the patched archive verifies, including the newly
raw-stored block. `[verified-numerically 2026-09-03, n=1 production edit, full-archive diff]`
Reading the patched bytes back confirms both fields decode to `309`. Full logs:
`dev-archive/recon/2026-09-03-repacker-validation/`.

## A real bug the tool's own safety check caught, on the first real use

The first patch attempt used hand-counted offsets from a hex dump (`0x56a3a4`/`0x56a3a8`) and was
refused: `forge_write.py` reads the bytes actually present at the claimed offset and compares them
against what the caller expects, raising rather than guessing on a mismatch. The true offsets,
found by searching the decompressed block programmatically for the datablock's own name string and
then for the two consecutive `u32` fields, were one byte earlier —
`0x56a3a3`/`0x56a3a7`. This is exactly the failure mode the check exists to catch, caught on the
first attempt to use it for something real.

## ⚠️ Deployment was attempted and blocked — correctly, and it stays a `[USER]` decision

Following this project's DLL-deployment precedent (a dated backup of the original, then the new
file copied over, with a one-step revert), I backed up `DataPC.forge`
(`DataPC.forge.m0-original-backup-2026-09-03`, verified byte-identical to the original by hash
before proceeding), then attempted to copy the patched archive over the installed one. **The
session's own safety system refused the overwrite.** That is the right call, not a bug to work
around: a repacked *core data archive* is a different risk class from an optional proxy DLL — a
missing or broken DLL fails gracefully back to the system version; corrupting the game's actual
`Game Bootstrap` datafile does not have an equivalent soft failure mode, however thoroughly the
patch was checked beforehand. I removed the now-unnecessary backup copy and left the install folder
exactly as found — verified by hash, `7805ea1af2ee8ac716eb03906fde513fc0b3cbb3d0fc17b68e9c9baa6f13a431`,
unchanged.

**The patched archive still exists**, in the scratch directory, validated as above. Deploying it —
one `cp`/`copy` command, with the same backup-first discipline — is recorded as a `[USER]` action in
the status file, not something I attempted to route around.

## What is NOT established

- **The archive was never deployed, so nothing about the mod's in-game effect is known.** Everything
  above is a static, verified data edit; whether `CAM FPS` actually appears needs the game running,
  by definition.
- **"With a raised priority"** — the second half of §6's mod-shaped consequence — **is not
  implemented.** No priority field has been located or touched. It is possible the state-list
  rewrite alone is sufficient (if `FunkyCameras`'s other rules don't also satisfy `(309, 309, 309)`
  with equal or higher priority) or it may not be — this is exactly the kind of thing that needs one
  flat-screen launch to settle, not more static work.
- **The tool has only ever patched same-length 4-byte fields.** A length-changing edit would need
  the datablock table (FORMAT.md §5) rewritten too, which this session did not attempt and was not
  needed for the recorded mod.

**The diagnostic that would show the repacker itself is wrong**, as opposed to the mod being
incomplete: if a deployed patch caused `Game Bootstrap` to fail to load at all (a crash, or a
missing-content error naming `Game Bootstrap` specifically), that points at the splice mechanism. If
the game loads fine and simply shows no visible change, that points at the missing priority field or
at the state-list rewrite not being sufficient on its own — not at the repacker.
