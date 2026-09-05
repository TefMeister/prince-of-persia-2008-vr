#!/usr/bin/env python3
"""Estate-wide ActionBlock census + id/string reference search (read-only).

[PD] question: does any of the 2,464 ActionBlock datablocks reference
StartMenuDebug_m (0x81358011) or DebugMenuHandler_m (0x96e48045)?

Design notes:
 * The needle set includes EVERY menu-handler datablock id from
   DataPC.forge -> Game Bootstrap, not only the two debug ones, so a negative
   on the debug ids is measured against how ordinary menus behave.
 * Positive control A: the same byte scan reports, for every ActionBlock, how
   many ids of OTHER datablocks in the same datafile it contains.
 * Positive control B: the two MagmaMgbFile ids the menu handlers point at.
 * String needles catch a name-driven (rather than id-driven) reference.

Read-only; the game is never launched.
"""
import os
import re
import struct
import sys
import time
import zlib

sys.path.insert(0, r"C:\Users\TD3KX\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import forge  # noqa: E402

GAME = r"C:\Steam\steamapps\common\Prince of Persia"
EXE = os.path.join(GAME, "PrinceOfPersia_Launcher.exe")
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# ---- needles -----------------------------------------------------------
TARGET_IDS = {
    0x81358011: "StartMenuDebug_m/P_MainMenuDebug",
    0x96e48045: "DebugMenuHandler_m/P_PauseMenuDebug",
    0x96e48049: "CheatMenuMagma_m/P_CheatMenuDebug",
}
CONTROL_IDS = {
    0x96e48031: "MainPauseMenuHandler_m/P_PauseMenu",
    0x96e4804d: "PauseMenuHandler_m",
    0x96e4802d: "OptionsMenuHandler_m/P_PauseOptions",
    0x96e48035: "SaveGameMenuHandler_m/P_PauseSave",
    0x96e48039: "DisplayOptionsMenuHandler_m",
    0x96e4804e: "SoundOptionsMenuHandler_m",
    0x96e4803d: "ControlsMenuHandler_m",
    0x96e48041: "CombosListMenuHandler_m",
    0x3ccac026: "PreGameMainMenuHandler_m/P_MainMenu",
    0x3ccac022: "StartMenuE3Handler_m/P_SplashPage",
    0x3ccac02a: "PreGameMenuHandler_m",
    0x149f4000: "TutorialMenuHandler_m/P_Tutorial",
    0x81358015: "HudMenuHandler_m/P_HUD",
    0xca3a0004: "MapMenuHandler_m/P_Map",
    0xa106c000: "TCRMenuHandler_m/P_AlertTCR",
    0x2c2e4005: "DownloadableContentMenuHandler_m",
    0x081b8052: "MagmaMgbFile MagmaCommon_MGB (the debug menus' UI file)",
    0x082ac02a: "MagmaMgbFile MagmaInGame_MGB (the normal pause menu's UI file)",
    0x00000808: "InterfaceManager 'Interface Manager'",
}
ALL_IDS = dict(TARGET_IDS)
ALL_IDS.update(CONTROL_IDS)

STRINGS = ["P_MainMenuDebug", "P_PauseMenuDebug", "P_CheatMenuDebug",
           "P_PauseMenu", "P_MainMenu", "MenuDebug", "DebugMenu"]

needles = []   # (bytes, label, kind)
for v, n in ALL_IDS.items():
    kind = "TARGET-ID" if v in TARGET_IDS else "control-id"
    needles.append((struct.pack("<I", v), "0x%08x %s" % (v, n), kind))
    needles.append((struct.pack(">I", v), "0x%08x %s [BE]" % (v, n), kind))
for s in STRINGS:
    kind = "TARGET-STR" if "Debug" in s else "control-str"
    needles.append((s.encode("ascii"), "str %r" % s, kind))
    needles.append((s.encode("utf-16-le"), "str %r [utf16]" % s, kind))

names = forge.TypeNames(EXE)
AB_HASH = zlib.crc32(b"ActionBlock") & 0xFFFFFFFF

archives = sorted(f for f in os.listdir(GAME) if f.lower().endswith(".forge"))
if len(sys.argv) > 2:
    archives = [f for f in archives if re.search(sys.argv[2], f, re.I)]

census = open(os.path.join(OUT, "actionblock-census.tsv"), "w", encoding="utf-8")
census.write("archive\tdatafile_index\tdatafile\tblock_index\tblock_id\tsize\tname\tn_ids_referenced\n")
log = open(os.path.join(OUT, "search-log.txt"), "w", encoding="utf-8")
hitf = open(os.path.join(OUT, "needle-hits.txt"), "w", encoding="utf-8")


def say(s):
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


say("estate-wide ActionBlock census + reference search  (read-only, game not launched)")
say("archives scanned: %d" % len(archives))
say("needles: %d id values (%d target, %d control) x 2 byte orders, %d strings x 2 encodings"
    % (len(ALL_IDS), len(TARGET_IDS), len(CONTROL_IDS), len(STRINGS)))
say("ActionBlock type hash = 0x%08x = crc32('ActionBlock')" % AB_HASH)
say("")

tot_files = tot_bytes = tot_ab = tot_ab_bytes = ab_with_refs = 0
split_fail = decomp_fail = notchunked = 0
hit_counts = {}
hit_in_ab = {}
ab_ref_hist = {}
ab_ref_examples = []
t0 = time.time()

for fn in archives:
    a = forge.Forge(os.path.join(GAME, fn))
    n_ab = n_files = 0
    for e in a.entries:
        payload = a.read(e)
        n_files += 1
        tot_files += 1
        blocks = None
        if not forge.is_chunked(payload):
            notchunked += 1
            dec = payload
        else:
            try:
                dec = forge.decompress_payload(payload)
            except Exception as exc:
                decomp_fail += 1
                say("  !! decompress %s [%d] %s: %s" % (fn, e.index, e.name, exc))
                continue
            try:
                blocks = forge.split_datablocks(dec)
            except Exception as exc:
                split_fail += 1
                say("  !! split %s [%d] %s: %s" % (fn, e.index, e.name, exc))
        tot_bytes += len(dec)

        for needle, label, kind in needles:
            start = 0
            while True:
                k = dec.find(needle, start)
                if k < 0:
                    break
                hit_counts[label] = hit_counts.get(label, 0) + 1
                where = "(datablock layout unavailable)"
                inab = False
                if blocks:
                    for b in blocks:
                        if b["offset"] <= k < b["offset"] + b["size"]:
                            where = "block %d %s %r (+0x%x)" % (
                                b["index"], names(b["type_hash"]), b["name"],
                                k - b["offset"])
                            inab = (b["type_hash"] == AB_HASH)
                            break
                if inab:
                    hit_in_ab[label] = hit_in_ab.get(label, 0) + 1
                # log every target hit, and control hits outside the archive we
                # already know about, capped so the file stays readable
                if kind.startswith("TARGET") or inab or hit_counts[label] <= 6:
                    hitf.write("%-11s %-56s %s [%d] %s @0x%x in %s%s\n" % (
                        kind, label, fn, e.index, e.name, k, where,
                        "   <<< INSIDE AN ActionBlock" if inab else ""))
                start = k + 1
        hitf.flush()

        if not blocks:
            continue
        ids = {}
        for b in blocks:
            ids.setdefault(b["id"], b)
        for b in blocks:
            if b["type_hash"] != AB_HASH:
                continue
            n_ab += 1
            tot_ab += 1
            tot_ab_bytes += b["size"]
            raw = b["raw"]
            refs = set()
            for off in range(0, len(raw) - 3):
                v = struct.unpack_from("<I", raw, off)[0]
                if v and v != b["id"] and v in ids:
                    refs.add(v)
            nb = len(refs)
            ab_ref_hist[nb] = ab_ref_hist.get(nb, 0) + 1
            if nb:
                ab_with_refs += 1
                if len(ab_ref_examples) < 12:
                    ab_ref_examples.append("%s [%d] %s block %d %r -> %d ids, e.g. %s" % (
                        fn, e.index, e.name, b["index"], b["name"], nb,
                        ", ".join("%08x:%s" % (t, names(ids[t]["type_hash"]))
                                  for t in sorted(refs)[:4])))
            census.write("%s\t%d\t%s\t%d\t%08x\t%d\t%s\t%d\n" % (
                fn, e.index, e.name, b["index"], b["id"], b["size"],
                b["name"] or "", nb))
    say("== %-34s datafiles=%5d ActionBlocks=%5d  (%5.0fs, %.2f GB decompressed)"
        % (fn, n_files, n_ab, time.time() - t0, tot_bytes / 1e9))
    census.flush()

census.close()
hitf.close()

say("")
say("TOTALS: archives=%d datafiles=%d decompressed=%d bytes (%.2f GB) in %.0fs"
    % (len(archives), tot_files, tot_bytes, tot_bytes / 1e9, time.time() - t0))
say("ActionBlocks enumerated: %d  (%d bytes)" % (tot_ab, tot_ab_bytes))
say("datafiles not chunked: %d ; decompress failures: %d ; datablock-split failures: %d"
    % (notchunked, decomp_fail, split_fail))
say("")
say("-- CONTROL A: how many datablock ids each ActionBlock's bytes contain")
say("   ActionBlocks referencing >=1 other datablock id: %d of %d (%.1f%%)"
    % (ab_with_refs, tot_ab, 100.0 * ab_with_refs / max(tot_ab, 1)))
for k in sorted(ab_ref_hist)[:15]:
    say("   %3d ids: %5d ActionBlocks" % (k, ab_ref_hist[k]))
say("   examples:")
for s in ab_ref_examples:
    say("     " + s)
say("")
say("-- NEEDLE RESULTS (hits anywhere / of those, hits inside an ActionBlock)")
for needle, label, kind in needles:
    c = hit_counts.get(label, 0)
    ia = hit_in_ab.get(label, 0)
    say("   %-11s %-56s %6d hits, %4d in ActionBlocks" % (kind, label, c, ia))
log.close()
