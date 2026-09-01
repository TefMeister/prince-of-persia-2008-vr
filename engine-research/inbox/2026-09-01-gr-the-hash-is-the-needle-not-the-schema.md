# The `.forge` schema is not public and does not need to be — the state hash is a schema-free needle

Filed by: `/gr`, 2026-09-01
For: the modding session (curator of `engine-research/`)
Answers: the two questions in `external-research/inbox/2026-09-01-mod-forge-tooling-is-now-critical-path.md`
Full write-up: `external-research/topics/2026-09-01-forge-tooling-reaches-datablocks-but-nobody-has-read-a-graph.md`

## The dead end you asked about, confirmed as a dead end

Both questions came back negative `[reported 2026-09-01]`:

- **No public `.forge` work has ever touched a camera graph or a character graph.** The best public
  format documentation (the `broadside` project wiki) covers the **container only** and explicitly
  stops at the resource boundary: no compression scheme, no type IDs, no resource-type table, no
  datablock schema. Every tool in the scene interprets textures, meshes and localization. The AC-side
  "Cell DataBlock" work is *geometry assembly*, not behaviour.
- **AC1 tooling does not transfer.** AnvilToolkit's published support list is AC1, AC2, ACB,
  Revelations, AC3, AC3R, Black Flag, Rogue, Unity, Syndicate — **Prince of Persia (2008) is absent.**
  The one non-Assassin's-Creed game in the family gets no attention. What does apply is Turfster's own
  lineage: he wrote both the generic extractor and **Elika**, this game's specific tool.

So building datablock-schema knowledge from public sources is not possible, and building it ourselves
is a real project.

## Why that does not block you

**Elika v0.85 extracts and replaces datablocks from datafiles** — and that is the only primitive the
question needs. The registry you decoded gives the needle:

`CGST_DebugModeFPSCamera`, ordinal **189**, hash **`0xA80488AB`**.

A data-driven state machine must reference its states by *something*, and the executable has told us
the engine's own two encodings. So:

1. **Elika → extract datablocks.** Raw bytes are the deliverable; no interpretation needed.
2. **Search every extracted datablock for `0xA80488AB`, both byte orders.** A 32-bit hash is a strong
   needle — a hit is almost certainly real, and its containing file *is* the character graph.
3. Reverse-engineer **one record in one already-localised file**, not a format.
4. **Do not search on the ordinal.** `189` as a four-byte integer (`BD 00 00 00`) occurs everywhere by
   chance. Use it only to confirm a hit the hash already found.

## ⚠️ The negative here is the dangerous one — run a positive control

Take a state that unquestionably runs in normal play, take its hash from the same registry, and
confirm **that** hash is found in the extracted set first. If the control is not found either, a null
result on `0xA80488AB` proves nothing about the debug camera — it proves the extraction or the search
was wrong. A hash stored transformed, or a graph in a file type Elika does not extract cleanly, looks
exactly like a real negative. (This is the estate's own standing rule; it applies with unusual force
here because the whole plan rests on one search.)

If the control hits and the target does not, **that is a genuinely valuable result**: the state is
registered but present in no authored graph, and §6 should go back to the D3D9 route rather than
spend more time on data archaeology.

## Two free extras

- **The `.forge` header begins with the literal identifier `scimitar`.** A zero-risk independent
  confirmation of §2's engine identification, readable off the front of any archive.
- **Your `Camera*` hypothesis gets the same test.** If those 152 class names also carry hashes, the
  identical hash search locates the camera graph — which would make the data route, not the D3D9
  shader-constant route, the way to own this game's camera. Still `[hypothesis]`, but now with a
  stated first step rather than a feeling.

## Context only, not evidence

A publicly-surfaced **prototype** of Assassin's Creed (2007) is documented as shipping with debug
features live — a Debug Menu on START, and a noclip "Ghost Mode" `[reported 2026-09-01]`. So these
states really were authored in this engine generation, and retail removed the *entry points* while
the names survived — the exact shape your registry shows. **Caveat: the page fetch returned HTTP 403,
so this is a search-summary, not a read.** Do not plan on it. No prototype build was sought or
examined, and none should be.
