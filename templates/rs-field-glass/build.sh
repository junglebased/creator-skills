#!/usr/bin/env bash
# rs-field-glass · build: copy licensed fonts + crop footage plates, render MP4, export frames.
# Usage: ./build.sh [out_dir] [slug]
# Plates: edit PLATES below (source still : x-offset of the 9:16 crop inside a 3840x2160 frame).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
COMP="$HERE/composition"
RS="$HOME/Desktop/2 Areas/Regenerative Stories"
FONTS="$RS/03 Brand & Identity/Brand Kit/RS Brandkit Fonts"
STILLS="$RS/01 Films/2026 Mikro Onarım/06 Content/_Görsel Havuzu/Film Kareleri (Master 4K)"
OUT="${1:-$COMP/renders}"
SLUG="${2:-20261013-mikro-onarim-ripple-reel}"
HF="${HF:-npx --yes hyperframes@0.8.150}"

# ring-N.jpg <- still | crop x (px in 3840 wide source; crop is 1215x2160 = 9:16)
PLATES=(
  "ring-1.jpg|film_0217s_yataklar-drone-burhan.jpg|1500"
  "ring-2.jpg|film_0487s_sofra-aile.jpg|1450"
  "ring-3.jpg|film_0103s_kazdaglari-hava.jpg|1150"
)

mkdir -p "$COMP/assets/fonts" "$COMP/assets/plates" "$OUT"
for f in ClashDisplay-Medium ClashDisplay-Semibold Satoshi-Regular Satoshi-Bold Boska-Medium Boska-MediumItalic; do
  cp "$FONTS/$f.otf" "$COMP/assets/fonts/"
done
for p in "${PLATES[@]}"; do
  IFS='|' read -r dst src x <<<"$p"
  ffmpeg -loglevel error -y -i "$STILLS/$src" -vf "crop=1215:2160:$x:0,scale=1080:1920" -q:v 3 "$COMP/assets/plates/$dst"
done

cd "$COMP"
$HF render -f 30 -q high -o "$OUT/$SLUG.mp4"

# frames for review: first, 8 s, last
ffmpeg -loglevel error -y -ss 0 -i "$OUT/$SLUG.mp4" -frames:v 1 "$OUT/$SLUG-00s.png"
ffmpeg -loglevel error -y -ss 8 -i "$OUT/$SLUG.mp4" -frames:v 1 "$OUT/$SLUG-08s.png"
ffmpeg -loglevel error -y -sseof -0.1 -i "$OUT/$SLUG.mp4" -frames:v 1 -update 1 "$OUT/$SLUG-end.png"
echo "done: $OUT/$SLUG.mp4"
