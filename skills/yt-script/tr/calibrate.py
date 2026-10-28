#!/usr/bin/env python3
"""calibrate.py - check hookscore_tr against real Turkish video openings.

Input: a folder of yt-dlp output, one sub-folder per channel, with <id>.info.json and <id>.tr*.vtt
(yt-dlp --write-auto-subs --sub-langs "tr.*,tr" --write-info-json --skip-download).
For each video: first FIRST_SEC seconds of the auto-captions -> hook text -> score.
Views are compared WITHIN a channel (percentile rank), because a 300-view channel and a 300K-view
channel are not on one scale.

    python3 -I calibrate.py DIR [--sec 15] [--csv out.csv]

Prints: Spearman rho of verdict and of each property vs within-channel view percentile, and the mean
verdict of each channel's top third vs bottom third. This is a sanity check on a small, uneven sample,
not a fit: do not tune weights to it without a held-out set.
"""
import csv, glob, json, os, re, sys
from importlib import util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = util.spec_from_file_location("hookscore_tr", os.path.join(HERE, "hookscore_tr.py"))
hs = util.module_from_spec(spec); spec.loader.exec_module(hs)

TS = re.compile(r"(\d+):(\d+):(\d+)\.(\d+)\s+-->")
TAG = re.compile(r"<[^>]+>")

def opening(vtt, sec):
    """Text of the cues that start before `sec` seconds, rolling duplicates removed."""
    out, last, cur = [], "", None
    for line in open(vtt, encoding="utf-8", errors="ignore").read().splitlines():
        m = TS.match(line)
        if m:
            h, mi, s, ms = map(int, m.groups())
            cur = h * 3600 + mi * 60 + s + ms / 1000
            continue
        if cur is None or cur >= sec or not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        t = TAG.sub("", line).strip()
        if t and t != last:
            out.append(t); last = t
    # rolling auto-captions repeat the previous line as a prefix of the next
    text = " ".join(out)
    return re.sub(r"\s+", " ", text).strip()

def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]: j += 1
        for k in range(i, j + 1): r[order[k]] = (i + j) / 2
        i = j + 1
    return r

def spearman(a, b):
    if len(a) < 5: return float("nan")
    ra, rb = rank(a), rank(b); n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(1)
    root = a[0]; sec = 15.0; csv_out = None
    if "--sec" in a: sec = float(a[a.index("--sec") + 1])
    if "--csv" in a: csv_out = a[a.index("--csv") + 1]
    rows = []
    for ch in sorted(d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d)):
        recs = []
        for info in glob.glob(os.path.join(ch, "*.info.json")):
            vid = os.path.basename(info)[:-len(".info.json")]
            vtts = sorted(glob.glob(os.path.join(ch, vid + ".tr*.vtt")))
            if not vtts: continue
            d = json.load(open(info, encoding="utf-8"))
            views = d.get("view_count")
            txt = opening(vtts[0], sec)
            if views is None or len(txt.split()) < 6: continue
            recs.append((vid, d.get("title", ""), views, d.get("duration") or 0, txt))
        if len(recs) < 6: continue
        views = [r[2] for r in recs]; pr = rank(views)
        for r, p in zip(recs, pr):
            parts, verdict, name, _ = hs.score(r[4])
            rows.append({"channel": os.path.basename(ch), "id": r[0], "views": r[2], "pct": p / (len(recs) - 1),
                         "verdict": verdict, **{k.lower(): v for k, v in parts.items()}, "formula": name,
                         "opening": r[4], "title": r[1]})
    if not rows: print("no usable videos"); sys.exit(1)
    pct = [r["pct"] for r in rows]
    print(f"videos {len(rows)} from {len({r['channel'] for r in rows})} channels (>=6 captioned videos each), opening = first {sec:g}s\n")
    for k in ["verdict", "specificity", "address", "stakes", "curiosity", "brevity"]:
        print(f"  spearman {k:<12} vs within-channel view percentile: {spearman([r[k] for r in rows], pct):+.2f}")
    top = [r["verdict"] for r in rows if r["pct"] >= 2 / 3]; bot = [r["verdict"] for r in rows if r["pct"] <= 1 / 3]
    print(f"\n  mean verdict, top third of each channel {sum(top)/len(top):.1f} (n={len(top)})  vs bottom third {sum(bot)/len(bot):.1f} (n={len(bot)})")
    vs = sorted(r["verdict"] for r in rows)
    q = lambda p: vs[min(len(vs) - 1, int(p * len(vs)))]
    print(f"  verdict quantiles of the whole sample: p25 {q(.25)}  p50 {q(.5)}  p75 {q(.75)}  p90 {q(.9)}  max {vs[-1]}")
    if csv_out:
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        print(f"\n  wrote {csv_out}")

if __name__ == "__main__":
    main()
