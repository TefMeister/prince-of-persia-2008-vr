# 2026-09-01 (b) — `CGST_DebugModeFPSCamera` is ordinal 189, and nothing in the code dispatches it

**Date:** 2026-09-01, dev machine, `/pd` pass. **The game was never launched.** Static analysis of
the shipped executable; nothing modified, nothing run.

This closes out the static half of the debug-camera lead from earlier today. The result is not the
one I hoped for, but it is a clean one: **the question cannot be answered from the executable,
because the state machine is not driven from the executable.**

---

## 1. The enum registry, fully decoded

There is a table at **VA `0x00E521E8`** in `.data`: **313 records, 12 bytes each**, of the form

```c
struct CGStateName {
    const char *name;    // -> the "CGST_…" string blob at 0x00D4C8CC..0x00D4E580
    int32_t     ordinal; // equals the row index; CGST_INVALID is -1
    uint32_t    nameHash;// 32-bit name hash
};
```

followed immediately at **`0x00E53094`** by a descriptor that points back at the table start — the
usual shape of a generic reflection registry.

`[inferred-static 2026-09-01]` — the field roles are read off the data itself: column 2 is exactly
the row index for 312 of 313 rows and `-1` for `CGST_INVALID`, which is what an ordinal does and
what nothing else would.

| Ordinal | Name |
|---|---|
| 0 | `CGST_Ground` |
| 1 | `CGST_Idle` |
| … | |
| **188** | **`CGST_DebugMode`** |
| **189** | **`CGST_DebugModeFPSCamera`** |
| … | |
| 310 | `CGST_Root` |
| 311 | `CGST_COUNT` |
| −1 | `CGST_INVALID` |

Hashes: `CGST_DebugMode` = `0x861D663F`, `CGST_DebugModeFPSCamera` = `0xA80488AB`.

## 2. The decisive negative: no code touches either state

Three searches, all across the whole image:

* **The name hashes** `0x861D663F` and `0xA80488AB` — **one occurrence each, and both are inside
  their own table record.** Nothing in `.text` references them.
* **The name strings** (`0x00D4D67C`, `0x00D4D664`) — referenced only from their own records.
* **Individual records** (e.g. `0x00E52AC4`) — **no references at all.** Only the table *start* is
  referenced, from the descriptor.

So there is **no hardcoded switch, no dispatch, no gate** on these states anywhere in the
executable — and that is not specific to the debug states: the registry as a whole is consumed
generically, through the descriptor, the way a reflection table is.

## 3. What that actually means (and what it does not)

**It does not mean the state is unimplemented.** That was the hypothesis I set out to test — "if the
dispatch has a real case for that ordinal, the state is implemented; if it falls through, the name
outlived the code" — and **the test was invalid, because there is no dispatch to inspect.** This
engine's character state machine is **data-driven**: states are nodes in a graph authored as data,
referenced by name or hash, and the executable only provides the registry that resolves them.

Recording that plainly, because the failure mode here is to read "no code references it" as "it was
stripped". It means neither. `[disproved 2026-09-01]` for the *method*, not for the lead.

**Where the answer actually is:** the character-graph data in the `.forge` archives. If a graph
there contains a node for state 189, the state is live and reachable; if not, only the enum
survived.

## 4. This promotes an existing research lead onto the critical path

`external-research/topics/2026-08-25-elika-forge-asset-extraction-tools.md` (currently 👀 reviewed)
documents `.forge` extraction tooling. That was filed as generally useful. **It is now the specific
thing standing between us and an answer** — the debug-camera question, and any other question about
this engine's state machine or camera graph, lives inside those archives.

Same for the camera side: the 152 `Camera*` class names found earlier are also a **registry**, and
`CameraGraph` / `CameraTemplate` / `CameraRule` are graph-authoring vocabulary. It is a fair
expectation that the camera behaviour is authored as data too — which would mean **the route to
owning this game's camera runs through `.forge`, not through patching code.** That is a materially
different plan from the D3D9 shader-constant work the dossier currently proposes, and probably a
better one for a first-person conversion.

`[hypothesis]` — the camera system being data-driven is inferred from the state machine being so and
from the naming, not demonstrated.

## 5. Next

**No launch needed:** get a `.forge` extractor working against `DataPC*.forge`, then look for the
character graph and search it for state 189 / hash `0xA80488AB`. That single search answers the
debug-camera question outright.

If `.forge` proves impractical, the shader-constant route in the dossier is unaffected and remains
available — nothing here closes it off.

🤖 Static analysis of the shipped executable only. The game was not launched, nothing was modified,
and no game content was copied here — only identifier names and table layout, which are interface
metadata.
