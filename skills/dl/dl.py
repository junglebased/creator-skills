#!/usr/bin/env python3
"""
dl.py — download media from a link straight into a folder. Free, no rate-capped bots.

Instagram (reel / post / carousel / story / saved collections), TikTok, YouTube, X,
Facebook, Vimeo, Pinterest and everything else yt-dlp / gallery-dl support.
Video -> yt-dlp, photos & carousels -> gallery-dl (uses your browser's login cookies).

Usage:
  dl.py DEST URL [URL ...]                 # name = platform id
  dl.py DEST CODE=URL [CODE=URL ...]       # name = CODE_01.ext, CODE_02.ext ...
  dl.py DEST --list links.txt              # lines: "CODE URL"
  dl.py DEST --browser firefox URL         # cookie source (default: chrome)
Next to every download a CODE.txt is written: source link, author, date, caption.
"""
import functools, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

print = functools.partial(print, flush=True)
HERE = Path(__file__).resolve().parent
MEDIA = {".mp4", ".mov", ".webm", ".mkv", ".jpg", ".jpeg", ".png", ".webp", ".heic", ".m4a", ".mp3"}


def tool(name):
    """Find yt-dlp / gallery-dl: PATH, then a local .venv next to the skills."""
    for c in (shutil.which(name), HERE.parent / ".venv/bin" / name, HERE / ".venv/bin" / name):
        if c and Path(c).exists():
            return str(c)
    sys.exit(f"{name} not found. Install: pip install {name}  (or brew install {name})")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def is_photo_post(url):
    return bool(re.search(r"instagram\.com/(p|stories)/|pinterest\.|/photo/", url))


def try_ytdlp(url, tmp, browser):
    base = [tool("yt-dlp"), "-q", "--no-warnings", "--no-playlist", "--write-info-json",
            "-f", "bv*+ba/b", "--merge-output-format", "mp4",
            "-o", str(tmp / "%(id)s_%(autonumber)02d.%(ext)s")]
    r = run(base + [url])
    if r.returncode != 0:
        r = run(base + ["--cookies-from-browser", browser, url])
    return r


def try_gdl(url, tmp, browser):
    return run([tool("gallery-dl"), "--cookies-from-browser", browser, "--write-metadata",
                "-D", str(tmp), "-f", "{num:>02}.{extension}", url])


def caption_from(tmp):
    for j in sorted(tmp.glob("*.json")):
        try:
            d = json.loads(j.read_text())
        except Exception:
            continue
        for k in ("description", "caption", "content", "title"):
            if isinstance(d.get(k), str) and d[k].strip():
                return d[k].strip(), d
    return "", {}


def download(url, dest, code, browser):
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        r = try_ytdlp(url, tmp, browser)
        files = [f for f in tmp.iterdir() if f.suffix.lower() in MEDIA]
        if not files or is_photo_post(url):
            before = len(files)
            g = try_gdl(url, tmp, browser)
            files = [f for f in tmp.iterdir() if f.suffix.lower() in MEDIA]
            if g.returncode != 0 and files and len(files) == before and is_photo_post(url):
                print(f"WARN {code or url}: only the video part came down — log in to the platform in {browser} for the photos")
            if not files:
                err = ((g.stderr or r.stderr).strip().splitlines() or ["?"])[-1]
                if "login" in err.lower():
                    err += f"  -> log in to this platform in {browser} and retry"
                print(f"FAIL {code or url}: {err}")
                return []
        cap, meta = caption_from(tmp)
        base = code or (meta.get("id") or meta.get("shortcode") or re.sub(r"\W+", "_", url)[-20:])
        out = []
        for i, f in enumerate(sorted(files, key=lambda p: p.name), 1):
            name = f"{base}_{i:02d}{f.suffix.lower()}" if len(files) > 1 or code else f"{base}{f.suffix.lower()}"
            target = dest / name
            shutil.move(str(f), target)
            out.append(target)
        (dest / f"{base}.txt").write_text(
            f"source: {url}\nauthor: {meta.get('uploader') or meta.get('username') or ''}\n"
            f"date: {meta.get('upload_date') or meta.get('date') or ''}\n\n{cap}\n", encoding="utf-8")
        for p in out:
            print(f"OK {p.name}  {p.stat().st_size / 1e6:.1f} MB")
        return out


def main():
    a = sys.argv[1:]
    browser = "chrome"
    if "--browser" in a:
        i = a.index("--browser"); browser = a[i + 1]; del a[i:i + 2]
    if len(a) < 2:
        sys.exit(__doc__)
    dest = Path(a[0]).expanduser()
    items = []
    if a[1] in ("--list", "--liste"):
        for line in Path(a[2]).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(\S+)\s+(https?://\S+)", line)
            if m:
                items.append((m.group(1), m.group(2)))
    else:
        for x in a[1:]:
            code, _, url = x.partition("=") if re.match(r"^[\w.-]+=https?://", x) else ("", "", x)
            items.append((code, url))
    for code, url in items:
        if code and any(dest.glob(f"{code}_*")):
            print(f"EXISTS, skipped: {code}")
            continue
        download(url, dest, code, browser)


if __name__ == "__main__":
    main()
