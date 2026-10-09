#!/usr/bin/env python3
"""
formula.py — turn reference content into a "viral formula" dataset.

  fetch  <LINK> <WORKDIR> [--limit N]   account / saved collection / single post / link list
  build  <WORKDIR> [--no-transcribe] [--no-enrich] [--baseline]
                                        posts.jsonl + contact sheets + frames + colors + transcripts
  table  <WORKDIR> [--top N]            ranked compact table (for Claude to read)
  synth  <WORKDIR>                      analysis/*.json -> elements.csv (lift) + hook_bank.csv

WORKDIR layout:
  media/        downloaded files (+ gallery-dl .json metadata)
  sheets/       <post>.jpg  — carousel contact sheet / video frame strip
  transcripts/  <post>.timed.txt — timecoded transcript (video)
  analysis/     <post>.json — per-post analysis (written by Claude, see codebook.md)
  posts.jsonl   one line per post: metrics, caption, colors, outlier score
"""
import argparse, glob, json, os, re, shutil, statistics, subprocess, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent


def _tool(name):
    for c in (shutil.which(name), SKILLS / ".venv/bin" / name, HERE / ".venv/bin" / name):
        if c and Path(c).exists():
            return str(c)
    return name


GDL = _tool("gallery-dl")
YTDLP = _tool("yt-dlp")
INDIR = str(SKILLS / "dl/dl.py")
TRANSCRIBE = str(SKILLS / "transcribe/transcribe.py")
BROWSER = os.environ.get("FORMULA_BROWSER", "chrome")
FMT = "{date:%Y%m%d}_{username}_{post_shortcode}_{num:>02}.{extension}"
VID = {".mp4", ".mov", ".webm", ".mkv"}
IMG = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- fetch
def fetch(link, work, limit):
    media = Path(work) / "media"
    media.mkdir(parents=True, exist_ok=True)
    arch = str(Path(work) / ".archive.sqlite3")
    base = [GDL, "--cookies-from-browser", BROWSER, "--download-archive", arch,
            "--sleep-request", "2-5", "--write-metadata", "-D", str(media), "-f", FMT]
    if Path(link).is_file():  # "KOD URL" listesi
        r = sh(["python3", INDIR, str(media), "--list", link]); log(r.stdout[-2000:]); return
    if re.search(r"instagram\.com/(p|reel|reels|tv)/", link):
        r = sh(base + [link])
        if r.returncode != 0 or not any(media.iterdir()):
            r = sh(["python3", INDIR, str(media), link])
        log(r.stdout[-1500:], r.stderr[-800:]); return
    if "instagram.com" in link:
        m = re.match(r"https?://(www\.)?instagram\.com/([\w.]+)/?(saved/.*)?$", link.split("?")[0])
        if m and not m.group(3):  # hesap: postlar + reels
            for sub in ("posts", "reels"):
                url = f"https://www.instagram.com/{m.group(2)}/{sub}/"
                r = sh(base + ["--range", f"1-{limit}", url]); log(sub, (r.stderr or "")[-400:])
            return
        r = sh(base + [link]); log((r.stderr or "")[-800:]); return
    # other platforms: single video or channel/profile
    r = sh([YTDLP, "-q", "--no-warnings", "--write-info-json", "--playlist-end", str(limit),
            "-o", str(media / "%(upload_date)s_%(uploader_id)s_%(id)s_01.%(ext)s"), link])
    if r.returncode != 0:
        r = sh(base + [link])
    log((r.stderr or "")[-800:])


# ---------------------------------------------------------------- build
def load_posts(media):
    posts = defaultdict(lambda: {"files": [], "meta": {}})
    for f in sorted(media.iterdir()):
        if f.suffix.lower() not in VID | IMG:
            continue
        meta = {}
        for jp in (Path(str(f) + ".json"), f.with_suffix(".info.json"), f.with_suffix(".json")):
            if jp.exists():
                try: meta = json.loads(jp.read_text()); break
                except Exception: pass
        m = re.match(r"(\d{8})_(.+)_([\w-]{11})_(\d{2})$", f.stem)
        key = meta.get("post_shortcode") or meta.get("id") or (m.group(3) if m else f.stem.rsplit("_", 1)[0])
        p = posts[key]
        p["files"].append(f)
        if meta and not p["meta"]:
            p["meta"] = meta
        if m and "date" not in p:
            p["date"], p["user"] = m.group(1), m.group(2)
    return posts


def enrich(url):
    """views/comments/duration via yt-dlp (only filled for video posts)."""
    r = sh([YTDLP, "--skip-download", "--dump-json", "--no-warnings", "--cookies-from-browser", BROWSER, url], timeout=90)
    if r.returncode != 0:
        return {}
    try: d = json.loads(r.stdout.splitlines()[0])
    except Exception: return {}
    return {k: d.get(k) for k in ("view_count", "like_count", "comment_count", "duration") if d.get(k) is not None}


def account_median(user, cache):
    """Median likes of the account's last 12 posts (for the outlier score)."""
    if user in cache:
        return cache[user]
    r = sh([GDL, "--cookies-from-browser", BROWSER, "--sleep-request", "2-4", "--range", "1-12",
            "--simulate", "--dump-json", f"https://www.instagram.com/{user}/posts/"], timeout=180)
    likes = []
    try:
        for item in json.loads(r.stdout or "[]"):
            if isinstance(item, list) and len(item) > 1 and isinstance(item[-1], dict) and item[-1].get("num", 1) == 1:
                if item[-1].get("likes") is not None:
                    likes.append(int(item[-1]["likes"]))
    except Exception:
        pass
    cache[user] = statistics.median(likes) if likes else None
    return cache[user]


def contact_sheet(files, out):
    imgs = [str(f) for f in files if f.suffix.lower() in IMG][:10]
    vids = [f for f in files if f.suffix.lower() in VID]
    frames = []
    tmp = out.parent / ".frames"; tmp.mkdir(exist_ok=True)
    for v in vids[:2]:
        dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)]).stdout.strip() or 0)
        for i, t in enumerate([0, 1.5, 3, dur * .25, dur * .5, dur * .75, max(dur - 1.5, 0)]):
            fp = tmp / f"{out.stem}_{v.stem[-2:]}_{i}.jpg"
            sh(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(v), "-frames:v", "1", str(fp)])
            if fp.exists(): frames.append(str(fp))
    srcs = (imgs + frames)[:12]
    if not srcs:
        return
    n, cols = len(srcs), min(len(srcs), 6)
    args, lay = [], []
    for k, s in enumerate(srcs):
        args += ["-i", s]; lay.append(f"{(k % cols) * 320}_{(k // cols) * 400}")
    scale = ";".join(f"[{k}:v]scale=320:400:force_original_aspect_ratio=decrease,pad=320:400:(ow-iw)/2:(oh-ih)/2[v{k}]" for k in range(n))
    stack = "".join(f"[v{k}]" for k in range(n))
    fc = scale + (f";{stack}xstack=inputs={n}:layout={'|'.join(lay)}:fill=white" if n > 1 else "")
    cmd = ["ffmpeg", "-loglevel", "error", "-y", *args, "-filter_complex", fc]
    if n == 1: cmd += ["-map", "[v0]"]
    sh(cmd + [str(out)])


def palette(files, k=5):
    """Dominant colors (hex) from the first image or first video frame."""
    src = next((f for f in files if f.suffix.lower() in IMG), None) or next((f for f in files if f.suffix.lower() in VID), None)
    if not src:
        return []
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(src), "-frames:v", "1",
                        "-vf", f"scale=64:80,palettegen=max_colors={k}:reserve_transparent=0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    px = r.stdout
    cols = ["#%02x%02x%02x" % tuple(px[i:i + 3]) for i in range(0, min(len(px), 256 * 3), 3)]
    seen = []
    for c in cols:
        if c not in seen and c != "#000000": seen.append(c)
    return seen[:k]


def build(work, transcribe=True, do_enrich=True, baseline=False, transcribe_top=0):
    work = Path(work); media = work / "media"
    sheets = work / "sheets"; trans = work / "transcripts"
    sheets.mkdir(exist_ok=True); trans.mkdir(exist_ok=True)
    posts = load_posts(media)
    log(f"{len(posts)} posts found")
    old = {}
    pj = work / "posts.jsonl"
    if pj.exists():
        for line in filter(None, pj.read_text().split("\n")):
            d = json.loads(line); old[d["id"]] = d
    cache, rows, to_tx = {}, [], []
    for key, p in posts.items():
        m = p["meta"]; files = p["files"]
        user = m.get("username") or m.get("uploader_id") or p.get("user", "")
        url = m.get("post_url") or m.get("webpage_url") or (f"https://www.instagram.com/p/{key}/" if re.match(r"^[\w-]{9,12}$", key) else "")
        vids = [f for f in files if f.suffix.lower() in VID]
        row = old.get(key, {})
        row.update({
            "id": key, "url": url, "user": user, "date": p.get("date") or (m.get("upload_date") or "")[:8],
            "type": "video" if vids and len(files) == len(vids) else ("carousel" if len(files) > 1 else "image"),
            "slides": len(files), "likes": int(m["likes"]) if str(m.get("likes", "")).isdigit() else m.get("like_count"),
            "caption": (m.get("description") or m.get("caption") or "").strip(),
            "hashtags": m.get("tags") or [], "collection": m.get("collection_name"),
            "files": [f.name for f in files],
        })
        if do_enrich and vids and "view_count" not in row and url:
            row.update(enrich(url))
        if baseline and user and "acct_median_likes" not in row:
            row["acct_median_likes"] = account_median(user, cache)
        if row.get("likes") and row.get("acct_median_likes"):
            row["outlier"] = round(row["likes"] / row["acct_median_likes"], 2)
        sp = sheets / f"{key}.jpg"
        if not sp.exists():
            contact_sheet(files, sp)
        if "colors" not in row:
            row["colors"] = palette(files)
        if vids and transcribe and not list(trans.glob(f"{key}*")):
            to_tx.append((key, vids[0], row.get("likes") or 0))
        rows.append(row)
        log(f"  {key} {row['type']} likes={row.get('likes')} views={row.get('view_count')}")
    if transcribe_top:  # pareto: only the best-performing videos get transcribed
        to_tx = sorted(to_tx, key=lambda t: -t[2])[:transcribe_top]
    to_tx = [(k, v) for k, v, _ in to_tx]
    if to_tx:
        log(f"transcribing {len(to_tx)} videos…")
        # one call = model loads once
        r = sh([shutil.which("uv") or "uv", "run", "--python", "3.12", TRANSCRIBE, *[str(v) for _, v in to_tx],
                "--mode", "timed", "--out", str(trans)], timeout=7200)
        if r.returncode:  # one silent/broken video can sink the whole batch → retry one by one
            log("  batch transcription failed, retrying per file")
            for _, v in to_tx:
                if not any(f.name.startswith(v.stem) for f in trans.iterdir()):
                    rr = sh([shutil.which("uv") or "uv", "run", "--python", "3.12", TRANSCRIBE, str(v),
                             "--mode", "timed", "--out", str(trans)], timeout=1800)
                    if rr.returncode: log("  skip (no speech/audio?):", v.name)
        for key, v in to_tx:
            for f in list(trans.iterdir()):
                if f.name.startswith(v.stem) and f.name.endswith(".txt"):
                    f.rename(trans / f"{key}.timed.txt")
    for row in rows:
        t = next(iter(trans.glob(f"{row['id']}*.txt")), None)
        if t:
            txt = t.read_text()
            row["transcript_file"] = t.name
            spoken = " ".join(l.split("] ", 1)[-1] for l in txt.splitlines()[:3])[:300]
            words = re.findall(r"\w+", txt)
            # Whisper hallucinates on music/silent video: drop very short or repetitive text
            if len(words) < 8 or len(set(w.lower() for w in words)) < 0.3 * len(words) or \
               spoken.strip().lower() in {"thank you.", "thanks for watching!", "you"}:
                spoken, row["transcript_note"] = "", "no speech / music (hallucination filtered)"
            row["spoken_hook"] = spoken
    # relative score inside the set (when no outlier): likes / that user's median in the set
    by_user = defaultdict(list)
    for r in rows:
        if r.get("likes"): by_user[r["user"]].append(r["likes"])
    for r in rows:
        u = by_user.get(r["user"], [])
        if r.get("likes") and len(u) >= 5:
            r["rel_in_set"] = round(r["likes"] / statistics.median(u), 2)
    rows.sort(key=lambda r: (r.get("outlier") or 0, r.get("likes") or 0, r.get("view_count") or 0), reverse=True)  # rel_in_set is shown, not ranked on
    pj.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
    shutil.rmtree(work / "sheets" / ".frames", ignore_errors=True)
    log(f"wrote: {pj}  ({len(rows)} posts)")


def table(work, top):
    rows = [json.loads(l) for l in filter(None, (Path(work) / "posts.jsonl").read_text().split("\n"))]
    log("rank|id|user|date|type|slides|likes|views|comments|dur|outlier|rel|colors|caption[:90]|spoken_hook[:90]")
    for i, r in enumerate(rows[:top], 1):
        log("|".join(str(x) for x in [i, r["id"], r["user"], r["date"], r["type"], r["slides"], r.get("likes"), r.get("view_count"),
                                       r.get("comment_count"), r.get("duration"), r.get("outlier"), r.get("rel_in_set"),
                                       ",".join(r.get("colors", [])), r["caption"][:90].replace("\n", " "),
                                       (r.get("spoken_hook") or "")[:90]]))


def synth(work):
    """analysis/*.json + posts.jsonl → elements.csv (lift), hook_bank.csv, counts.json"""
    import csv
    work = Path(work)
    rows = {json.loads(l)["id"]: json.loads(l) for l in filter(None, (work / "posts.jsonl").read_text().split("\n"))}
    an = []
    for f in sorted((work / "analysis").glob("*.json")):
        try: a = json.loads(f.read_text())
        except Exception as e: log("broken json", f.name, e); continue
        a["_m"] = rows.get(a.get("id"), {}); an.append(a)
    score = lambda a: (a["_m"].get("outlier") or 0, a["_m"].get("likes") or 0)
    an.sort(key=score, reverse=True)
    n = len(an); k = max(3, round(n * .3))
    top, low = an[:k], an[-k:]
    def feats(a):
        v = a.get("visual", {}); c = a.get("copy", {})
        fs = {f"el:{e}" for e in a.get("viral_elements", [])}
        fs |= {f"hook:{a.get('hook', {}).get('type', '')}", f"emotion:{a.get('emotion', '')}",
               f"first_frame:{v.get('first_frame', '')}", f"typography:{v.get('typography', '')}",
               f"text_pos:{v.get('text_position', '')}", f"density:{v.get('density', '')}",
               f"palette:{v.get('palette_mood', '')}", f"cta:{(c.get('cta') or {}).get('type', '')}",
               f"type:{a['_m'].get('type', '')}"}
        return {x for x in fs if not x.endswith(":")}
    allf = sorted({x for a in an for x in feats(a)})
    pct = lambda grp, x: round(100 * sum(x in feats(a) for a in grp) / max(len(grp), 1))
    out = []
    for x in allf:
        t, l, al = pct(top, x), pct(low, x), pct(an, x)
        out.append({"feature": x, "all%": al, "top%": t, "low%": l, "lift": round((t + 5) / (l + 5), 2)})
    out.sort(key=lambda r: (-r["lift"], -r["top%"]))
    with open(work / "elements.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ["feature"]); w.writeheader(); w.writerows(out)
    with open(work / "hook_bank.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["rank", "id", "user", "likes", "hook_type", "hook_text", "spoken", "mechanism", "cta_type", "cta_text", "url"])
        for i, a in enumerate(an, 1):
            h = a.get("hook", {}); c = (a.get("copy") or {}).get("cta") or {}
            w.writerow([i, a["id"], a["_m"].get("user"), a["_m"].get("likes"), h.get("type"), h.get("text"), h.get("spoken"),
                        h.get("mechanism"), c.get("type"), c.get("text"), a["_m"].get("url")])
    log(f"{n} analyses | top={k} low={k}")
    log("feature|all%|top%|low%|lift")
    for r in out[:25]:
        log(f"{r['feature']}|{r['all%']}|{r['top%']}|{r['low%']}|{r['lift']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("fetch"); a.add_argument("link"); a.add_argument("work"); a.add_argument("--limit", type=int, default=60)
    b = sp.add_parser("build"); b.add_argument("work"); b.add_argument("--no-transcribe", action="store_true")
    b.add_argument("--no-enrich", action="store_true"); b.add_argument("--baseline", action="store_true")
    b.add_argument("--transcribe-top", type=int, default=0, help="only transcribe the N most-liked videos")
    c = sp.add_parser("table"); c.add_argument("work"); c.add_argument("--top", type=int, default=40)
    d = sp.add_parser("synth"); d.add_argument("work")
    x = ap.parse_args()
    if x.cmd == "synth": synth(x.work); sys.exit()
    if x.cmd == "fetch": fetch(x.link, x.work, x.limit)
    elif x.cmd == "build": build(x.work, not x.no_transcribe, not x.no_enrich, x.baseline, x.transcribe_top)
    else: table(x.work, x.top)
