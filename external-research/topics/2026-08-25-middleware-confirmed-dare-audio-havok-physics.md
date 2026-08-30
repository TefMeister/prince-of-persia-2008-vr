# Middleware identified: "Dare" is Ubisoft's own audio system (not engine-specific); physics is Havok

**Status:** 🆕 new · **Priority:** medium — directly fills two open blanks in `ENGINE-DOSSIER.md`
§2 (the `Dare`/`DARE.INI` string was flagged as an unconfirmed internal subsystem, and physics
middleware was marked "not yet investigated").

## What was found

- **`Dare` = Ubisoft's own internal "Dare Audio" system** — confirmed as a genuine, named Ubisoft
  audio technology, **not specific to the Scimitar/Anvil engine family**: it was also used (per
  public sources) in Splinter Cell's separate "Third Echelon Engine," used there instead of OpenAL.
  Ubisoft is reported to maintain an internal "Dare" team functioning as a cross-project technical
  audio group. This resolves the dossier's open question about what `Dare`/`DARE.INI` refers to —
  it's a shared, Ubisoft-wide audio middleware/team, not an Anvil-specific or Prince-of-Persia-
  specific system, and not something with public technical documentation of its internal format
  beyond this identification.
- **Havok physics confirmed** for Prince of Persia (2008) specifically, per technical/specs
  aggregation (MobyGames' tech listing draws on official/press-sourced platform and middleware
  data). This matches the same physics middleware already confirmed on the Mad Max front of this
  portfolio (companion project, different engine) — Havok was extremely common across this console
  generation, so the coincidence isn't itself meaningful, but it's now a confirmed fact rather than
  an open blank.

## Why this matters

Neither finding is directly camera/projection-relevant, but both close out real open items in §2
without requiring live investigation, and Havok's confirmation means any physics-driven camera
behavior (e.g. camera reacting to ragdoll/impact physics, if this game does that) has a known,
identifiable middleware behind it rather than an unknown custom system — worth remembering if such
behavior comes up during live investigation.

## Concrete next step

Record both directly in `ENGINE-DOSSIER.md` §2. No further action needed — neither warrants deeper
investigation on its own.

## Sources

- https://en.namu.wiki/w/%EC%9C%A0%EB%B9%84%EC%86%8C%ED%94%84%ED%8A%B8%20%EA%B2%8C%EC%9E%84%20%EC%97%94%EC%A7%84
- https://www.mobygames.com/game/38110/prince-of-persia/
