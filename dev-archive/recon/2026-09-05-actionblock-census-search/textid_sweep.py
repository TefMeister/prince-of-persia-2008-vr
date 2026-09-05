"""Second sweep: the Magma UI files store datablock ids as ASCII text
("0x081b804f"), so a purely binary needle would miss a text-form reference.
Sweeps every datafile of every archive for the text form of the three debug
menu ids, with two known-present controls."""
import os, re, sys, time
sys.path.insert(0, r"C:\Users\TD3KX\github-backups-pd\prince-of-persia-2008-vr\dev-archive\tools\forge")
import forge

GAME = r"C:\Steam\steamapps\common\Prince of Persia"
names = forge.TypeNames(os.path.join(GAME, "PrinceOfPersia_Launcher.exe"))
OUT = sys.argv[1]

IDS = {
    0x81358011: "TARGET StartMenuDebug_m",
    0x96e48045: "TARGET DebugMenuHandler_m",
    0x96e48049: "TARGET CheatMenuMagma_m",
    0x96e48031: "control MainPauseMenuHandler_m",
    0x081b8052: "control MagmaCommon_MGB (text form known to be used)",
    0x081b804f: "control MagmaFonts_MGB (text form seen at MagmaCommon_MGB+0x2b19)",
}
needles = []
for v, n in IDS.items():
    for s in ("0x%08x" % v, "0x%08X" % v, "%08x" % v, "%08X" % v):
        needles.append((s.encode(), "%s  as %r" % (n, s)))

counts = {}
out = open(os.path.join(OUT, "text-id-sweep.txt"), "w", encoding="utf-8")
t0 = time.time()
for fn in sorted(f for f in os.listdir(GAME) if f.lower().endswith(".forge")):
    a = forge.Forge(os.path.join(GAME, fn))
    for e in a.entries:
        payload = a.read(e)
        dec = forge.decompress_payload(payload) if forge.is_chunked(payload) else payload
        blocks = None
        if forge.is_chunked(payload):
            try:
                blocks = forge.split_datablocks(dec)
            except Exception:
                blocks = None
        for needle, label in needles:
            start = 0
            while True:
                k = dec.find(needle, start)
                if k < 0:
                    break
                counts[label] = counts.get(label, 0) + 1
                where = "-"
                if blocks:
                    for b in blocks:
                        if b["offset"] <= k < b["offset"] + b["size"]:
                            where = "block %d %s %r (+0x%x)" % (
                                b["index"], names(b["type_hash"]), b["name"], k - b["offset"])
                            break
                if counts[label] <= 12:
                    out.write("%-56s %s [%d] %s @0x%x in %s\n"
                              % (label, fn, e.index, e.name, k, where))
                start = k + 1
    out.flush()
    print("done %s (%.0fs)" % (fn, time.time() - t0), flush=True)
out.write("\n-- totals --\n")
for needle, label in needles:
    out.write("%-56s %d\n" % (label, counts.get(label, 0)))
    print("%-56s %d" % (label, counts.get(label, 0)), flush=True)
out.close()
