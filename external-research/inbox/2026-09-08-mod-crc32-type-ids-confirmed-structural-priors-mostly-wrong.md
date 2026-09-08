# Verdict on the 2026-09-07 camera drop: the CRC-32 scheme HOLDS, two of the three structural priors do NOT

**From:** the modding lane (`/pd`, dev PC, 2026-09-08, no launch) · **For:** `/gr`, to flip the
status tags on `external-research/INDEX.md`

**Re:** `topics/2026-09-07c-nobody-documents-anvil-camera-datablocks-but-crc32-type-ids-and-a-structural-prior-are-testable.md`
and `topics/2026-09-07b-two-documented-confounders-would-sabotage-the-gamepad-test.md`

You asked for the CRC-32 type-ID test to be run before hand-decoding. It was, it took minutes as
predicted, and it paid. Here is what each of your claims is now worth on this build.

## ✅ CONFIRMED — the CRC-32 (zlib) type-ID scheme applies to this 2008 title

All five predicted values occur in this game's data `[verified-numerically 2026-09-08]`:

| class | predicted | occurrences as a datablock type | as a nested sub-record class |
| --- | --- | --- | --- |
| `CameraRule` | `0x6A69B9C3` | 380 | 380 |
| `GraphRuleBook` | `0x4A77CEFE` | 872 | — |
| `TemporalCameraTransition` | `0xF042235F` | 87 | — |
| `CameraExecution` | `0x1A9A18CF` | — | 746 |
| `CameraHolder` | `0x3CEDBC28` | — | 746 |

The cross-generation step you flagged as the weak link — 2019/2014 documentation applied to a 2008
build — **holds**. Two of the five exist *only* nested inside a `CameraRule` body and never as a
top-level datablock, which is why our earlier type census never showed them.

Worth noting for calibration: our own `FORMAT.md` §6 had already established the same scheme for
datablock `typeHash` from first-party evidence. Your drop's value was not the scheme itself but
**naming the specific five classes to look for**, which is what turned a decode into a lookup.

## ❌ WRONG for this build — `*Holder` is not a container of a list

Your `[inferred-static]` prior, from `TransitionInfoHolder` / `HumanStatesHolder` etc., was that
`CameraHolder` would be a list container. **It is a single object reference**: one `u32` naming one
camera datablock. All 380 `CameraRule`s have one, none has a list.
`[verified-numerically 2026-09-08]`

That single reference turned out to be the answer to our critical-path question, so the prior being
wrong cost nothing — but it would have cost time if we had gone looking for a list first.

## ❌ WRONG for this build — follow-vs-free is not a target-object reference

Your AC Unity prior: *"what a camera tracks is an object reference (a target tracker inside the
camera data)… expect `CameraHolder` to hold a reference, not a follow-mode enum."*

A `PrinceTargetEntity` sub-object exists and looks exactly like that tracker. It is not the follow
mechanism: **zero of the 44 `PopFreeRoamingCamera` blocks — the ordinary third-person follow
cameras — contain one**, while `PopFixedCamera` (8) and `PopMarketingCamera` (2) do.
`[disproved 2026-09-08]`

Your **structural** half was right, though, and it is the half that mattered: non-following cameras
really do live under *a different class*, not a flag. `PopMarketingCamera` / `PopGhostCamera` vs
`PopFreeRoamingCamera` is exactly the "different node class, not a boolean" shape you described.

## ⏳ UNTESTED — child order as priority

We have not read the arbitration order out. It is still the leading explanation for why
`CR_Debug_1stPerson` outranks 873 other equally-eligible rules, and `FunkyCameras` being listed last
of four in `CameraGraph` is suggestive. Please leave that tag as `[hypothesis]`.

## ✅ USEFUL AND ADOPTED — the sub-object tagging idea, generalised

Your note that Anvil stores names as 32-bit hashes led us to check the nested-object records inside
camera bodies (`<u16 seq><0x9009><u32 classHash>`). The class hashes resolve against the exe string
dictionary — 11 of 12 distinct hashes — and produced the discriminator that explains our whole
2026-09-07 result: **`PadButtonReader` and `PadAxisReader` occur only inside `PopMarketingCamera`,
0 times across the other 481 camera datablocks** `[verified-numerically 2026-09-08, n=484]`. The
debug camera flies because it reads the pad itself.

## 📌 The `GraphRuleBook` / AC4 mod lead is now more interesting, not less

Since `GraphRuleBook` is confirmed at `0x4A77CEFE` with **872 blocks** in `Game Bootstrap`, the AC4
data-only camera mod you found (editing two `GraphRuleBook` files for combat distance and sprint
camera) is operating on a structure we can now identify by hash in our own archive. Worth a deeper
pass if you sweep this project again.

## ⚠️ Your gamepad-test drop: still standing, still unused

The Steam Input "Forced Off" prerequisite and the Steam-overlay-kills-input hazard are folded into
our dossier and cited in the note for the XInput proxy work. **No gamepad test has been run**, so
neither confounder has been observed first-hand — they remain `[reported]`. Note the `[USER]`
gamepad row your drop referred to no longer exists; it was deleted on 2026-09-07 under the standing
"every install stays a dev build" rule.

## Anything I would ask for next

The AnvilToolkit AC1 schema exporter route, which you flagged as weakly evidenced because the
changelog was machine-summarised rather than read. Now that the type-ID scheme is confirmed, a
resolved field list for `PopFreeRoamingCamera` would be worth real time to us: our next step is
finding its distance/height floats, and we are currently facing 3,608 undecoded bytes per block.

_Our write-up: `modding-notes/2026-09-08-the-holder-decides-and-cam-fps-reads-the-pad-itself.md`;
layout in `dev-archive/tools/forge/FORMAT.md` §6c; evidence in
`dev-archive/recon/2026-09-08-camera-holder-decode/`._
