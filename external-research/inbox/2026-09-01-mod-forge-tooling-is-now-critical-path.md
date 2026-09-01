# The `.forge` extraction lead is now on the critical path, not a nice-to-have

**From:** the modding side (`/pd` pass), 2026-09-01
**For:** `/gr prince-of-persia-2008-vr`

## The topic

`topics/2026-08-25-elika-forge-asset-extraction-tools.md` — currently 👀 **reviewed**, filed as
generally useful tooling. **Please re-rank it: it is now the single thing blocking a concrete
question**, and worth a deeper pass on which extractor actually works for this specific 2008 build.

## Why it changed

Static work today decoded the game's character-state registry: a 313-record table at `0x00E521E8`
of `{const char *name; int32 ordinal; uint32 nameHash}`, in which **`CGST_DebugModeFPSCamera` is
ordinal 189** (hash `0xA80488AB`) and `CGST_DebugMode` is 188.

Then the useful negative: **nothing in the executable references either state.** Not the hashes
(one occurrence each, inside their own record), not the name strings, not the individual records —
only the table *start*, from a descriptor. There is no switch, no dispatch and no gate on these
states anywhere in `.text`.

The conclusion is not "the state was stripped". It is that **this engine's character state machine
is data-driven** — states are graph nodes authored as data and resolved through the registry, so the
executable has nothing to inspect. **The answer lives in the `.forge` archives**, and a single
search of the character graph for state 189 settles the debug-camera question outright.

## A second question for the same pass

The 152 `Camera*` class names found earlier are also a registry, and the vocabulary is
graph-authoring — `CameraGraph`, `CameraTemplate`, `CameraRule`, `CameraRuleGraphClip`,
`CameraTransitionSpecification`. It is a fair expectation that **camera behaviour is authored as
data too.**

If that holds, the route to owning this game's camera runs through `.forge` rather than through
patching code — a materially different plan from the D3D9 shader-constant work the dossier currently
proposes, and plausibly a better one for a first-person conversion. **`[hypothesis]` on our side.**

**What would help most:** whether the community's Scimitar/`.forge` work has ever touched the
*camera graph* or *character graph* specifically (as opposed to meshes and textures), and whether
Assassin's Creed 1 tooling — same engine lineage, far more attention — transfers to this build.
