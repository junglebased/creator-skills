#!/usr/bin/env bash
# rs-field-glass · build one reel from a reel JSON: fonts + plates + scene.js -> MP4 + 3 review frames.
# Usage: ./build.sh <reel.json> [out_dir]
#   out_dir defaults to the reel's "area_out". Never overwrites: an existing <slug>.mp4 gets -v2, -v3, ...
# Renders in a scratch copy of composition/, so the template (and the installed skill) stays clean.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REEL="${1:?usage: build.sh <reel.json> [out_dir]}"
REEL="$(cd "$(dirname "$REEL")" && pwd)/$(basename "$REEL")"
RS="$HOME/Desktop/2 Areas/Regenerative Stories"
FONTS="${RS_FONTS:-$RS/03 Brand & Identity/Brand Kit/RS Brandkit Fonts}"
HF="${HF:-npx --yes hyperframes@0.8.150}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/motion-rs-field-glass.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

cp -R "$HERE/composition/." "$WORK/"

# reel.json -> shell vars + scene.js (python: stdlib only). Refuses rings without a source line.
VARS="$(python3 - "$REEL" "${2:-}" "$WORK" <<'EOF'
import json, os, shlex, sys
reel, out_arg, work = sys.argv[1], sys.argv[2], sys.argv[3]
r = json.load(open(reel))
if r.get("preset", "rs-field-glass") != "rs-field-glass":
    sys.exit(f"!! preset {r.get('preset')} is not rs-field-glass")
rings = r["scene"]["rings"]
if len(rings) != 3 or len(r["plates"]) != 3:
    sys.exit("!! rs-field-glass needs exactly 3 rings and 3 plates")
for i, g in enumerate(rings, 1):
    if not g.get("source", "").strip():
        sys.exit(f"!! ring {i} has no source line. No source, no number.")
ex = lambda p: os.path.expanduser(p)
out = ex(out_arg or r.get("area_out") or os.path.join(os.path.dirname(reel), "renders"))
slug = r["slug"]; base = slug; n = 2
while os.path.exists(os.path.join(out, base + ".mp4")):
    base = f"{slug}-v{n}"; n += 1
open(os.path.join(work, "scene.js"), "w").write("window.SCENE = " + json.dumps(r["scene"], ensure_ascii=False, indent=2) + ";\n")
print(f"OUT={shlex.quote(out)}; NAME={shlex.quote(base)}; STILLS={shlex.quote(ex(r['stills_dir']))}")
print("PLATES=(" + " ".join(shlex.quote(f"ring-{i}.jpg|{p['src']}|{p['x']}") for i, p in enumerate(r["plates"], 1)) + ")")
EOF
)"
eval "$VARS"

mkdir -p "$WORK/assets/fonts" "$WORK/assets/plates" "$OUT"
for f in ClashDisplay-Medium ClashDisplay-Semibold Satoshi-Regular Satoshi-Bold Boska-Medium Boska-MediumItalic; do
  cp "$FONTS/$f.otf" "$WORK/assets/fonts/"
done
# ring-N.jpg <- 4K still, 9:16 crop (1215x2160) at x px, scaled to 1080x1920
for p in "${PLATES[@]}"; do
  IFS='|' read -r dst src x <<<"$p"
  ffmpeg -loglevel error -y -i "$STILLS/$src" -vf "crop=1215:2160:$x:0,scale=1080:1920" -q:v 3 "$WORK/assets/plates/$dst"
done

cd "$WORK"
$HF render -f 30 -q high -o "$OUT/$NAME.mp4"

# review frames: first, 8 s, last
ffmpeg -loglevel error -y -ss 0 -i "$OUT/$NAME.mp4" -frames:v 1 "$OUT/$NAME-00s.png"
ffmpeg -loglevel error -y -ss 8 -i "$OUT/$NAME.mp4" -frames:v 1 "$OUT/$NAME-08s.png"
ffmpeg -loglevel error -y -sseof -0.1 -i "$OUT/$NAME.mp4" -frames:v 1 -update 1 "$OUT/$NAME-end.png"
ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration,size -of compact "$OUT/$NAME.mp4"
echo "done: $OUT/$NAME.mp4"
