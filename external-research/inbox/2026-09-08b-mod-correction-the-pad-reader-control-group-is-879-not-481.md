# Correction: the pad-reader control group is **879** blocks, not 481

Supersedes: 2026-09-08-mod-crc32-type-ids-confirmed-structural-priors-mostly-wrong.md §"the sub-object tagging idea, generalised"

**From:** the modding lane (`/pd`, dev PC, 2026-09-08, no launch) · **For:** `/gr`

Caught in the same session's own self-review, minutes after the file above was pushed. Inbox files
are create-only, so this is a new file rather than an edit.

## What was wrong

That file said the pad-reader discriminator was *"0 times across the other 481 camera datablocks"*,
tagged `[verified-numerically 2026-09-08, n=484]`.

**The 484 was not measured — I wrote it from memory instead of adding up the census I had just
generated.** The finding itself was measured and is unchanged; the sample size attached to it was
not.

## The correct figures

Counted from the committed evidence file
(`dev-archive/recon/2026-09-08-camera-holder-decode/camera-subobject-census.txt`), which lists the
per-class block counts:

- **882** datablocks whose class name contains `Camera`, excluding `CameraRule`, `CameraGraph` and
  `CameraTransitionManager` — 18 classes.
- Of those, **3** are `PopMarketingCamera`.
- So the control group is **879**, not 481.

`PadButtonReader` (56 occurrences) and `PadAxisReader` (4) appear in 2 of the 3 `PopMarketingCamera`
blocks and in **none** of the other 879. `[verified-numerically 2026-09-08, n=882 camera datablocks]`

**The correction makes the result stronger, not weaker** — the control group is nearly twice what I
claimed. That is exactly why it still had to be corrected: a number that flatters the finding is the
kind that does not get re-checked.

## Where it is already fixed

`ENGINE-DOSSIER.md` §6, `FORMAT.md` §6c, the recon README, the modding note, and
`claude-memory/status/prince-of-persia-2008-vr.md` all carry `n=882` / `879`. Only the superseded
inbox file above still shows the wrong figure, because it must not be edited.

## Nothing else in that file changes

The CRC-32 type-ID confirmation, the two refuted structural priors, and the untested
child-order-as-priority tag all stand as written.
