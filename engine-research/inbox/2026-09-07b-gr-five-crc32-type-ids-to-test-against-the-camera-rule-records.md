# ⭐ Five CRC-32 type IDs to test against our own records — and what to expect `CameraHolder` to be

**From:** `/gr` (estate sweep, 2026-09-07, second POP drop) · **For:** the modding lane, for the ⭐⭐
`[PD]` camera-rule row

**One ask:** run the CRC-32 type-ID test in §1 before decoding `CameraExecution`/`CameraHolder` by
hand. It is minutes, needs no launch, and a single match makes the rest ground truth.

**Full write-up:** [`external-research/topics/2026-09-07c-nobody-documents-anvil-camera-datablocks-but-crc32-type-ids-and-a-structural-prior-are-testable.md`](../../external-research/topics/2026-09-07c-nobody-documents-anvil-camera-datablocks-but-crc32-type-ids-and-a-structural-prior-are-testable.md)

## First, the honest headline: no public schema exists

**Nobody has documented Scimitar/Anvil camera datablock internals** — not for this game, not for any
Anvil game. No `CameraRule` field list, no `CameraExecution`/`CameraHolder` description, no `CGST_`
enum `[reported 2026-09-07]`. The negative is evidenced, not assumed: AnvilToolkit's wiki (the only
public datablock-internals reference) loaded fine and simply has no camera page; and GitHub code
search returns **0** for `TemporalCameraTransition`, `CGST_DebugMode`, `CGST_DebugModeFPSCamera` and
`CR_Debug_1stPerson` against a **capability control of `"CGST_"` returning 38,784 hits**
`[verified-numerically 2026-09-07]`.

**So our decode cannot be shortened by copying a spec** — and our `CR_Debug_1stPerson` edit looks like
the **first public data-driven camera change in this game**. Every other public PoP camera solution is
memory patching.

## ⭐⭐ 1. The test worth running first

Anvil type IDs are documented as **CRC-32 (zlib, poly `0xEDB88320`) of the ASCII type name** — from
decompiled AnvilToolkit internals, verified empirically on Ghost Recon Breakpoint
(`crc32("BuildTable") = 585940579`, `crc32("Mesh") = 1096652136`) and cross-corroborated by a type ID
`95741049` = `CRC32("Bone")` appearing in both a 2014 and a 2019 title `[reported / inferred-static]`.

If this game uses the same scheme, our type IDs are — `[verified-numerically]` as CRC-32 values,
`[hypothesis]` that the scheme applies here:

| type | decimal | hex |
| --- | --- | --- |
| `CameraRule` | 1785313731 | `0x6A69B9C3` |
| `TemporalCameraTransition` | 4030866271 | `0xF042235F` |
| `GraphRuleBook` | 1249365758 | `0x4A77CEFE` |
| `CameraExecution` | 446306511 | `0x1A9A18CF` |
| `CameraHolder` | 1022213160 | `0x3CEDBC28` |

**One match converts the scheme into ground truth**, and then the same trick **brute-forces field
names** inside `CameraRule` from a wordlist — because Anvil stores field names only as **32-bit
hashes** (its reflection member records carry a `memberNameHash` and a `typeNameHash`; field order is
schema order). That is why AnvilToolkit shows unresolved names as `x73B5D0A0`.

## ⭐ 2. What to expect when the bytes are read

From reverse-engineered AC Unity class layouts — seven years downstream, so `[hypothesis]` throughout:

- **Follow-vs-free is not a boolean.** What a camera tracks is an **object reference** (a target
  tracker inside the camera data), and non-following cameras live under a **structurally separate
  root** — a different node *class*, not a flag. **Expect `CameraHolder` to hold a reference/handle,
  not a follow-mode enum.**
- ⭐ **`*Holder` is an Anvil naming idiom for "container of a list"**, not "thing that holds the camera
  in space" — the same codebase has `TransitionInfoHolder`, `HumanStatesHolder`, `RenderValuesHolder`,
  `DebugCommandsHolder` `[inferred-static]`.
- **Arbitration is a tree walk with a boolean condition per node, and order within the parent's child
  array IS the priority** — no separate priority integer. That speaks directly to the row's either/or:
  check whether `CR_Debug_1stPerson` and `CR_Debug_GhostCam` differ in **child order** rather than in
  a priority field.
- **Transitions attach to the node**, which is the natural analogue of our 968
  `TemporalCameraTransition` records.

## ⭐ 3. `GraphRuleBook` has a shipped precedent on this engine family

An **AC4 data-only camera mod** edits `GraphRuleBook` datablocks and nothing else — two files out of
`Game Bootstrap Settings.data`: `7398_-_Fight Book.GraphRuleBook` (combat camera distance, prevents
auto zoom-out) and `9390_-_Run_Sprint Book.GraphRuleBook` (removes camera shake, over-the-shoulder
sprint camera) `[reported 2026-09-07]`. Unpack → drop in → repack: our own workflow.

So a `GraphRuleBook` is a **named per-context rule book**, consistent with our 2,631 records being
per-context books referencing `CameraRule`s `[hypothesis]`. It also ties back to this lane's earlier
"Game Bootstrap is a named editable block" finding — that mod's files come out of exactly that block.

## 4. `CGST_` and state `309` — the answer is internal

Nothing public names any `CGST_` constant or what `309` is; **our archive is likely the only public
artefact carrying those names.** The route needs no research: `309` sits beside `188 CGST_DebugMode`
and `189 CGST_DebugModeFPSCamera` in our own list, and **the 876 `CameraRule` state lists are a
frequency corpus** from which the common/default state falls out numerically.

## 5. One route that could halve the work, with its caveat

**AnvilToolkit ships a generic schema-based exporter for AC1–Syndicate** — and **AC1 is our engine
generation**. If it is generic over the class registry, it could dump AC1 camera datablocks to XML
with resolved or `x<HEX>` field names, giving a field list to align our bytes against.
⚠️ **AnvilToolkit does not support Prince of Persia**, so this is a route to a *schema*, not a tool for
our archive. ⚠️ And the evidence is weak in a specific way: its changelog was **summarised by an
automated fetcher rather than reproduced**, so "no camera exporter is mentioned" is **not** a strong
negative. Re-check before relying on it either way.

## ⚠️ The distance involved

Our target is **2008, LZO2A**. The reflection headers are **AC Unity 2014**; the CRC-32 documentation
is **Ghost Recon Breakpoint 2019, Oodle, forge v27**; the `GraphRuleBook` mod is **AC4 2013**. Every
cross-generation claim is `[hypothesis]` for that reason — and each is cheap to test numerically
against an archive we already parse in full, which is the only reason they are worth having.

## Credit

Kamzik123 (AnvilToolkit + Resources/wiki); NameTaken3125 (`ACUFixes` / `ACU-RE` headers); dataterminals
(GRB knowledgebase, the CRC-32 type-ID documentation); gentlegiantJGC and Ads20000 (ACExplorer);
KhoiPete and whitek3note (the AC4 `GraphRuleBook` camera mod); one3rd and mul0 (PoP cheat tables);
Frans Bouma / Otis_Inf (IGCS, checked and confirmed not to cover this game); PCGamingWiki; ZenHAX;
Hidden Palace / Prototype Preservation. Added to `external-research/CREDITS.md`. Read online only;
nothing cloned, downloaded or installed.

⚠️ **Archival gaps, not negatives:** `wiki.tbotr.net` is dead and the XeNTaX forum is gone, and
ACExplorer's own wiki *defers to TBotR* for format depth — so the era-appropriate reference for this
exact question is **lost rather than absent**; an Internet Archive attempt is the obvious follow-up.
AC1's 1.0 MB / 3.3 MB name lists were not examined (too large for code search, out of scope for a
no-download pass) and are a good untested lead.
