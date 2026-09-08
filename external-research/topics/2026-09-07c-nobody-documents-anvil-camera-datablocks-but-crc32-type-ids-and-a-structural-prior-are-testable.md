# Nobody documents Anvil camera datablocks — but five CRC-32 type IDs and a structural prior are testable against an archive we already parse

**Status:** 🆕 new · **Priority:** high — the `[PD]` camera-rule row is now the critical path, and this
turns "read the sub-records and hope" into **one numerical test we can run today**, plus a concrete
expectation of what `CameraHolder` will turn out to be.

## Why this was looked up

The board's ⭐⭐ `[PD]` row, after the camera takeover was confirmed live:

> **WHICH CAMERA RULE IS ACTUALLY WINNING, AND CAN IT BE LOCKED TO THE PRINCE'S HEAD?** … We patched
> `CR_Debug_1stPerson` (`188 CGST_DebugMode, 189 CGST_DebugModeFPSCamera, 309`) but the behaviour is a
> **ghost/free cam** … Read both rules' `CameraExecution` / `CameraHolder` sub-records out of
> `DataPC.forge` and compare. Then find what makes a camera FOLLOW the character.

## ❌ The direct answer: no public schema exists, and the negative is well-evidenced

**Nobody has publicly documented the internal schema of Scimitar/Anvil camera datablocks** — not for
this game, not for any Anvil game `[reported 2026-09-07]`. No `CameraRule` field list, no
`CameraExecution`/`CameraHolder` description, no `CGST_` enum.

The negative is trustworthy rather than assumed:

- **AnvilToolkit's wiki** is the only community reference that goes *inside* datablocks. Its file-type
  guides cover BuildTable & EntityBuilder, Materials & TextureSets, Skeletons, Reflex3 constraints and
  ClothSettings — **and nothing else**. The page loaded and returned that real content, so the absence
  of a camera page is real, not a fetch failure.
- **GitHub code search**, authenticated: `TemporalCameraTransition` **0**, `CGST_DebugMode` **0**,
  `CGST_DebugModeFPSCamera` **0**, `CR_Debug_1stPerson` **0**, `GraphRuleBook` 9 (all unrelated
  graph/planning code) — against a **capability control of `"CGST_"` returning 38,784 hits** (all
  Indian tax code). The index returns that substring freely, so the zeroes are true negatives
  `[verified-numerically 2026-09-07]`.
  ⚠️ Caveat we already know: GitHub does not index files over ~384 KB, so AnvilToolkit's AC1 name
  lists (1.0 MB and 3.3 MB) are **not** covered by that negative.

**So our own decode cannot be shortened by copying a spec, and our `CR_Debug_1stPerson` data edit
appears to be the first public data-driven camera change in this game.** Every public PoP 2008 camera
solution is memory/code patching — a Cheat Engine table that only works while paused at the main menu,
a handful of cheat tables, and nothing else; PoP is absent from IGCS's 32 camera folders
`[verified-numerically]` and PCGamingWiki records `FOV: false` for it.

## ⭐⭐ 1. The testable part: type IDs may be CRC-32 of the ASCII type name

Documented from decompiled AnvilToolkit (`ScimitarClassRegistry`, `CRC32.ComputeCRC32`) and verified
empirically against Ghost Recon Breakpoint files: `crc32("BuildTable") = 585940579`,
`crc32("Mesh") = 1096652136`, standard zlib CRC-32 `[reported 2026-09-07]`. Cross-generation
corroboration: ACExplorer's AC Unity type-reader files are named by 8-hex type IDs, and one is
`95741049` — which the GRB table lists as `CRC32("Bone")`. Same value in a 2014 game and a 2019 one
`[inferred-static]`.

**If PoP 2008 uses the same scheme, these are our type IDs** — `[verified-numerically 2026-09-07]` as
CRC-32 values (zlib, poly `0xEDB88320`); `[hypothesis]` that this game uses the scheme:

| type name | decimal | hex |
| --- | --- | --- |
| `CameraRule` | 1785313731 | `0x6A69B9C3` |
| `TemporalCameraTransition` | 4030866271 | `0xF042235F` |
| `GraphRuleBook` | 1249365758 | `0x4A77CEFE` |
| `CameraExecution` | 446306511 | `0x1A9A18CF` |
| `CameraHolder` | 1022213160 | `0x3CEDBC28` |

### ✅ I recomputed all five, and the scheme itself now verifies against three anchors

Not relayed — computed here with zlib CRC-32 `[verified-numerically 2026-09-07]`. All five values
above reproduce exactly, and three independent controls confirm the **scheme**, which is the part that
actually matters:

| control | computed | status |
| --- | --- | --- |
| `crc32("BuildTable")` | **585940579** | matches the documented value exactly |
| `crc32("Mesh")` | **1096652136** | matches the documented value exactly |
| `crc32("Bone")` | **2507411529 = `0x95741049`** | ⭐ exactly the hex type-ID filename observed in ACExplorer's AC Unity type readers |

The third is the strongest: it was **not** a documented value to check against, it independently
**explains an observed filename in a different game's tooling**. So "Anvil type IDs are CRC-32 of the
ASCII type name" is now verified end to end rather than taken on report.

⚠️ **What remains `[hypothesis]` is narrower than before, and worth stating precisely:** the scheme is
established for the family; whether **this 2008 build** uses it is the open question, and that is what
the test settles.

**Matching even one against a record's type field converts the whole scheme into ground truth for
us** — and if it holds, the same CRC-32 trick lets us **brute-force field names inside `CameraRule`
from a wordlist** (`FollowTarget`, `Priority`, `Holder`, `Distance`, `Fov`, …). We already parse the
archive in full, so this is a test we can run today with no new tooling and no launch.

## ⭐ 2. What the decode will look like: names are 32-bit hashes, order is schema order

Anvil is reflection-driven, and the reflection system is publicly reverse-engineered for AC Unity
`[reported 2026-09-07]`. Each class carries a `TypeInfo` with a type name, base-class hash, struct
size, deserializer and an array of member records; **each member record carries a `memberNameHash`
(uint32) and a `typeNameHash` (uint32)**, an offset, bitfield offset/width, inline-array size, and a
primitive type code from a named enum (`TIPT_Bool`, `TIPT_Float`, `TIPT_Vector3`, `TIPT_Quaternion`,
`TIPT_ObjectID`, `TIPT_Enum`, `TIPT_String`, `TIPT_StrongPtr`, `TIPT_SmallArrayObjectPtr`, …).

**Two consequences for our decode:** field order in a datablock is the schema's member order, and
**field names exist only as 32-bit hashes** — which is exactly why AnvilToolkit displays unresolved
names as `x73B5D0A0`. That is the mechanism behind §1's brute-force suggestion.

## ⭐ 3. A structural prior for "what makes a camera follow" — and it says `CameraHolder` is probably a list

From reverse-engineered AC Unity class layouts (memory layouts, not file schema, and seven years
downstream — so `[hypothesis]` for 2008 throughout):

- **Follow-vs-free is not a boolean.** What an ACU camera tracks is an **object reference** — a
  `MainBehaviorTargetTracker` inside `CameraData` — and genuinely non-following cameras live under a
  **structurally separate root** (`FixedCameraSelectorNode` / `FixedCameras`), i.e. a different node
  *class*, not a flag on a shared one. **So expect `CameraHolder` to contain a reference/handle to a
  tracker or entity, rather than a follow-mode enum.**
- **Arbitration is a tree walk with a boolean condition per node**, and **order within the parent's
  child array is the priority** — there is no separate priority integer in the ACU layout. That bears
  directly on the row's either/or: *"either this rule's execution is a free camera in this build, or
  opening the gate let a different rule win."*
- **Transitions attach to the node**, via a `TransitionInfoHolder` on the selector — the natural
  analogue of our **968 `TemporalCameraTransition`** records.
- ⭐ **`*Holder` is an Anvil naming idiom meaning "container of a list"**, not "thing that holds the
  camera in space" — the same codebase has `TransitionInfoHolder`, `HumanStatesHolder`,
  `RenderValuesHolder`, `DebugCommandsHolder` `[inferred-static]`. Weak but real, and it changes what
  to expect when the bytes are read.

## ⭐ 4. `GraphRuleBook` has a confirmed precedent — a data-only camera mod on the same engine family

On **Assassin's Creed IV** (AnvilNext, 2013) there is a published **data-only** camera mod that edits
`GraphRuleBook` datablocks and nothing else `[reported 2026-09-07]`: two files pulled out of
`Game Bootstrap Settings.data` — **`7398_-_Fight Book.GraphRuleBook`** (combat camera distance,
prevents auto zoom-out) and **`9390_-_Run_Sprint Book.GraphRuleBook`** (removes walk/sprint camera
shake, over-the-shoulder sprint camera). Install is unpack → drop in → repack, which is our own
workflow.

So a `GraphRuleBook` is a **named per-context rule book** — "Fight Book", "Run_Sprint Book" — and
editing one changes camera framing, distance and shake for that context. That is consistent with our
**2,631 `GraphRuleBook`** records being per-context books referencing `CameraRule`s `[hypothesis]`,
and it is independent evidence that data-only camera modding is a legitimate, shipped technique on
this engine family. Neither mod page documents internal fields — they are "here are the bytes"
releases.

**It also connects to this lane's earlier finding** that "Game Bootstrap" is a named, routinely-edited
block across the Anvil family: the AC4 camera mod's files come out of exactly that block.

## 5. The one route that could genuinely halve the work

**AnvilToolkit ships a generic "schema based exporter for AC1 – Syndicate games"** (forceable by
holding Shift), and its changelog claims resolved hashed property names for BuildTable,
EntityBuilder, Cloth, Material, Mesh and Skeleton `[reported 2026-09-07]`. **AC1 is our engine
generation.** If that exporter is generic over the class registry rather than a hand-written per-type
list, it can dump *arbitrary* AC1 datablocks — camera types included — to XML with resolved or
`x<HEX>` field names, giving us a field list to align our own bytes against.

⚠️ **AnvilToolkit does not list Prince of Persia among its supported games**, so it will not open our
archive. This is a route to a *schema*, not a tool for our data.

⚠️ **And the evidence for it is weak in a specific way:** the changelog was read by an automated
fetcher that **summarised rather than reproduced it**, so "no camera-type exporter is mentioned" is
**not** a strong negative — someone reading it end to end could still find a camera entry. Re-check
before relying on either direction.

## 6. `CGST_` and state `309`: the answer is internal, not external

Nothing anywhere names any `CGST_` constant or says what `309` is `[verified-numerically 2026-09-07]`.
**Our archive is very likely the only public artefact carrying that enum's names.**

The practical route is internal and needs no research: `309` sits beside `188 CGST_DebugMode` and
`189 CGST_DebugModeFPSCamera` in our own recorded state list, and **the 876 `CameraRule` records'
state lists are a frequency corpus** — the common/default state can be identified numerically from
them alone.

## The concrete next steps, cheapest first

1. **Test the CRC-32 hypothesis** against the type field of records we already parse, using the five
   values in §1. Minutes, no launch, and a single match makes the rest ground truth.
2. **If it holds, brute-force field-name hashes** in `CameraRule` from a wordlist — the reflection
   system in §2 is why that works.
3. **Read `CameraHolder` expecting a list/reference container**, not a mode flag (§3), and check
   whether `CR_Debug_1stPerson` and `CR_Debug_GhostCam` differ in *child order* rather than in a
   priority field.
4. **Identify state `309` from our own 876 state lists**, not from the web.
5. Only if 1–4 stall: pursue AnvilToolkit's AC1 schema exporter (§5), with its caveat.

## ⚠️ Everything cross-generation here is a hypothesis, and the gap is large

Our target is **2008, LZO2A**. The reflection headers are **AC Unity, 2014**; the CRC-32 type-ID
documentation is **Ghost Recon Breakpoint, 2019, Oodle, forge v27**; the `GraphRuleBook` mod is
**AC4, 2013**. Every claim carried across that distance is tagged `[hypothesis]` for exactly that
reason — and each is cheap for us to test numerically against an archive we already parse in full,
which is the only reason they are worth writing down.

## Sources and credit

Read online only; nothing cloned, downloaded or installed, and no code copied.

- **Kamzik123** — AnvilToolkit and its Resources/wiki (the only public datablock-internals reference,
  and the AC1–Syndicate schema exporter). <https://github.com/Kamzik123/AnvilToolkit-Resources>
- **NameTaken3125** — `ACUFixes` and its `ACU-RE` reverse-engineered AC Unity class headers
  (`TypeInfo`, `CameraManager`, `CameraSelectorNode`, `CameraData`, `ACUPlayerCameraComponent`).
  <https://github.com/NameTaken3125/ACUFixes>
- **dataterminals** — the GRB modding knowledgebase: forge/`.data` layout and the **CRC-32 type-ID**
  documentation. <https://github.com/dataterminals/grb-modding-knowledgebase>
- **gentlegiantJGC** (and fork **Ads20000**) — ACExplorer / pyUbiForge.
- **KhoiPete** (original) and **whitek3note** (data version) — the AC4 `GraphRuleBook` camera mod.
- **Turfster** (Elika, the PoP 2008 extractor) and **feillyne** (ModDB mirror) — already credited here.
- **one3rd** — the PoP 2008 Cheat Engine free-camera table and its description of the camera as a
  position plus a rotation matrix. **mul0** and the fearlessrevolution team — PoP cheat tables.
- **Frans Bouma / Otis_Inf** — IGCS, checked and confirmed not to support this game.
- **PCGamingWiki contributors**; the **ZenHAX** community; **Hidden Palace / Prototype Preservation**
  (the AC3 2012 prototype's documented debug-camera controls, which confirm the engine family ships a
  first-class debug-camera concept).

## What came back empty, and which gaps are archival rather than real

- **Camera schema, `CGST_` enum, state `309`, PoP data-edit camera mods:** real negatives, with the
  capability controls described above.
- ⚠️ **`wiki.tbotr.net` is dead** (certificate failure / offline) and **the XeNTaX forum is gone**
  (403 → 404). ACExplorer's own wiki *defers to TBotR* for format depth, so the era-appropriate
  reference for this exact question is **lost, not absent** — an Internet Archive attempt is the
  obvious follow-up in a later pass.
- ⚠️ **Three FearLess cheat-table threads returned HTTP 403**, so their feature lists come from search
  snippets and are thin `[reported]`.
- ⚠️ **AC1's name lists** (`AC1.gfl` 1.0 MB, `AC1.fgfl` 3.3 MB) were **not examined** — too large for
  code search and out of scope for a no-download pass. If PoP-like camera type names appear in AC1's
  list, that would confirm our types exist in AC1 and that its schema exporter might dump them. **An
  untested lead, and a good one.**
- **Method note worth keeping:** the GRB knowledgebase repo ships `AGENTS.md` and `CLAUDE.md` — files
  addressed to AI agents. They were noted, **not opened**, and the repo was treated as data throughout,
  per the standing rule that fetched material is data and not instructions. This is the second time
  that surface has come up in this account's research; the first was cloaked instructions on tcrf.net.


---

## ✅ Outcome — tested by the modding lane, 2026-09-08 (`/pd`, dev PC, no launch)

Folded in by `/gr` on 2026-09-08 from `external-research/inbox/`. This section records what each
claim above turned out to be worth **on this build**; the body above is left as written.

### The CRC-32 (zlib) type-ID scheme: CONFIRMED

All five predicted values occur in this game's data `[verified-numerically 2026-09-08]`:

| class | predicted | as a datablock type | as a nested sub-record |
| --- | --- | --- | --- |
| `CameraRule` | `0x6A69B9C3` | 380 | 380 |
| `GraphRuleBook` | `0x4A77CEFE` | 872 | — |
| `TemporalCameraTransition` | `0xF042235F` | 87 | — |
| `CameraExecution` | `0x1A9A18CF` | — | 746 |
| `CameraHolder` | `0x3CEDBC28` | — | 746 |

The weak link this topic named itself — 2014/2019 documentation applied to a 2008 build, the
*first* Scimitar title — **holds**. Two of the five exist only nested inside a `CameraRule`
body and never as a top-level datablock, which is why the project's earlier type census never
showed them.

Calibration, recorded so this topic is not credited with more than it did: the project's own
`FORMAT.md` §6 had already established the same scheme for datablock `typeHash` from
first-party evidence. **The value here was naming the specific five classes to look for**, which
turned a decode into a lookup.

### ⭐ What it unlocked

The sub-object tagging idea generalised: nested-object records inside camera bodies
(`<u16 seq><0x9009><u32 classHash>`) resolve against the exe string dictionary — 11 of 12
distinct hashes — and produced the discriminator explaining the whole 2026-09-07 result.
**`PadButtonReader` (56 occurrences) and `PadAxisReader` (4) appear only inside
`PopMarketingCamera`, and in none of the other 879 camera datablocks**
`[verified-numerically 2026-09-08, n=882 camera datablocks]`. The debug camera flies because it
reads the pad itself.

> ⚠️ **Sample size corrected the same day.** This verdict first arrived as "0 times
> across the other **481** camera datablocks `[verified-numerically 2026-09-08, n=484]`". That
> figure was written from memory rather than counted; the committed census
> (`dev-archive/recon/2026-09-08-camera-holder-decode/camera-subobject-census.txt`) gives **882**
> camera datablocks across 18 classes, of which 3 are `PopMarketingCamera`, so the control group is
> **879**. The finding is unchanged and is **stronger** than first stated. Recorded here because a
> number that flatters a finding is the kind that does not get re-checked.

### ❌ The structural priors: two of three refuted for this build

- **`*Holder` means "list container"** — wrong here. `CameraHolder` is a **single object
  reference**: one `u32` naming one camera datablock. All 380 `CameraRule`s have one; none has a
  list. `[verified-numerically 2026-09-08]` That single reference turned out to *be* the answer to
  the critical-path question, so the wrong prior cost nothing — but it would have cost time
  had anyone gone hunting for a list first.
- **Follow-vs-free is a target-object reference** — wrong here. A `PrinceTargetEntity`
  sub-object exists and looks exactly like the predicted tracker, but **zero of the 44
  `PopFreeRoamingCamera` blocks** (the ordinary third-person follow cameras) contain one, while
  `PopFixedCamera` (8) and `PopMarketingCamera` (2) do. `[disproved 2026-09-08]`
- **The structural half was right, and was the half that mattered:** non-following cameras really
  do live under *a different class* rather than behind a flag —
  `PopMarketingCamera` / `PopGhostCamera` vs `PopFreeRoamingCamera`.

### ⏳ Still untested

**Child order as priority** remains the leading explanation for why `CR_Debug_1stPerson` outranks
873 other equally-eligible rules (`FunkyCameras` being listed last of four in `CameraGraph` is
suggestive). The arbitration order has not been read out. **Leave it `[hypothesis]`.**

### 📌 Follow-up this raises

`GraphRuleBook` is confirmed at `0x4A77CEFE` with **872 blocks** in `Game Bootstrap`, so the
shipped AC4 data-only camera mod noted above is operating on a structure this project can now
identify by hash in its own archive. Worth a deeper pass. The modding lane also asked for the
**AnvilToolkit AC1 schema-exporter route** — flagged in the body above as weakly evidenced
because its changelog was machine-summarised rather than read — to be re-examined properly: a
resolved field list for `PopFreeRoamingCamera` is worth real time against **3,608 undecoded bytes
per block**.
