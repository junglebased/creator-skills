# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""QC for a rendered deliverable (no Resolve needed): format, loudness, black frames, safe-zone frames.

Usage:
  uv run qc.py FILE --target reels|youtube [--out DIR] [--frames 4]

Checks (green/yellow/red) and writes <FILE>.qc.md next to the file (or in --out):
  - container/codec/resolution/fps/pixel format/audio rate vs target
  - integrated loudness (target -14 LUFS ±1) and true peak (<= -1 dBTP) via ffmpeg ebur128
  - black segments (>= 0.5 s) via blackdetect
  - N evenly spaced frames saved as PNG with the Reels safe zone drawn (for a visual check by Claude/Berkay)
Needs ffmpeg + ffprobe on PATH. Read-only on the input file.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TARGETS = {
    "reels": {"w": 1080, "h": 1920, "codecs": {"h264", "hevc"}, "fps": {23.976, 24.0, 25.0, 29.97, 30.0}},
    "youtube": {"w": 3840, "h": 2160, "codecs": {"h264", "hevc", "prores"},
                "fps": {23.976, 24.0, 25.0, 29.97, 30.0}},
}
LUFS, LUFS_TOL, TRUE_PEAK = -14.0, 1.0, -1.0
SAFE = {"top": 220, "bottom": 1520, "side": 64}  # Reels text zone (same as motion agent SPEC)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    if r.returncode:
        sys.exit(f"!! ffprobe failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def fps_of(stream):
    num, _, den = (stream.get("avg_frame_rate") or "0/1").partition("/")
    return round(float(num) / float(den or 1), 3) if float(den or 1) else 0.0


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-filter_complex",
             "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def black_segments(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf",
             "blackdetect=d=0.5:pix_th=0.10", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)


def frames(path, out, n, dur, draw_safe):
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        png = out / f"{path.stem}_qc_{k + 1:02d}.png"
        vf = "null"
        if draw_safe:
            s = SAFE
            vf = (f"drawbox=x={s['side']}:y={s['top']}:w=iw-{2 * s['side']}:"
                  f"h={s['bottom'] - s['top']}:color=red@0.8:t=4")
        r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-ss", f"{t:.2f}",
                 "-i", str(path), "-frames:v", "1", "-vf", vf, str(png)])
        if r.returncode == 0:
            saved.append(png)
    return saved


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--target", choices=TARGETS, required=True)
    ap.add_argument("--out")
    ap.add_argument("--frames", type=int, default=4)
    a = ap.parse_args()
    path = Path(a.file)
    out = Path(a.out) if a.out else path.parent
    t = TARGETS[a.target]
    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"].get("duration", 0))
    rows = []

    def check(name, ok, value, want, warn=False):
        rows.append((("🟢" if ok else ("🟡" if warn else "🔴")), name, value, want))

    if v is None:
        sys.exit("!! no video stream")
    check("resolution", (v["width"], v["height"]) == (t["w"], t["h"]),
          f"{v['width']}x{v['height']}", f"{t['w']}x{t['h']}")
    check("codec", v["codec_name"] in t["codecs"], v["codec_name"], "/".join(sorted(t["codecs"])))
    f = fps_of(v)
    near = min(abs(f - x) for x in t["fps"])
    check("fps", near < 0.01, f"{f}" + (" (VFR?)" if 0.01 <= near < 0.1 else ""),
          "/".join(map(str, sorted(t["fps"]))), warn=near < 0.1)
    check("pixel format", v.get("pix_fmt", "").startswith("yuv420"), v.get("pix_fmt"), "yuv420p",
          warn=a.target == "youtube")
    check("audio", bool(au) and au.get("sample_rate") == "48000",
          f"{au.get('codec_name')} {au.get('sample_rate')}" if au else "none", "48 kHz")
    i, tp = loudness(path) if au else (None, None)
    check("loudness", i is not None and abs(i - LUFS) <= LUFS_TOL, f"{i} LUFS", f"{LUFS}±{LUFS_TOL}")
    check("true peak", tp is not None and tp <= TRUE_PEAK, f"{tp} dBTP", f"<= {TRUE_PEAK}")
    blacks = black_segments(path)
    edge = [b for b in blacks if float(b[0]) > 0.1 and float(b[1]) < dur - 0.1]
    check("black frames", not edge, f"{len(edge)} mid-segments", "0", warn=True)
    pngs = frames(path, out, a.frames, dur, a.target == "reels")

    md = [f"# QC · {path.name}", "", f"Target: {a.target} · duration {dur:.1f}s", "",
          "| | check | value | want |", "|---|---|---|---|"]
    md += [f"| {s} | {n} | {val} | {w} |" for s, n, val, w in rows]
    md += ["", "Frames (red box = Reels text safe zone; text must stay inside):"]
    md += [f"- {p.name}" for p in pngs]
    verdict = "🔴" if any(r[0] == "🔴" for r in rows) else ("🟡" if any(r[0] == "🟡" for r in rows) else "🟢")
    md.insert(2, f"**Verdict: {verdict}**")
    report = out / f"{path.stem}.qc.md"
    report.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\n-> {report}")


if __name__ == "__main__":
    main()
