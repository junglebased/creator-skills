#!/usr/bin/env bash
# Install creator-skills into ~/.claude/skills (keeps your existing brand kits).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/skills"
DST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DST"

for s in dl formula transcribe yt-script yt-package yt-edit yt-comment yt-plan yt-viral yt-retention yt-shorts yt-seo yt-chapters yt-audit; do
  mkdir -p "$DST/$s"
  # copy everything except brand kits the user already has
  rsync -a --exclude 'brands/*.md' "$SRC/$s/" "$DST/$s/"
done
mkdir -p "$DST/formula/brands"
cp -n "$SRC/formula/brands/"*.md "$DST/formula/brands/" 2>/dev/null || true

# YouTube voice profile (read by every /yt-* skill); never overwrite an existing one
mkdir -p "$HOME/.claude/youtube"
cp -n "$SRC/yt-voice-template/voice.md" "$HOME/.claude/youtube/voice.md" 2>/dev/null || true

# yt-dlp + gallery-dl in a venv shared by the skills
if ! command -v gallery-dl >/dev/null || ! command -v yt-dlp >/dev/null; then
  python3 -m venv "$DST/.venv"
  "$DST/.venv/bin/pip" install -q --upgrade yt-dlp gallery-dl
fi

command -v ffmpeg >/dev/null || echo "!! ffmpeg not found: brew install ffmpeg (needed for frames, sheets, merging)"
command -v uv >/dev/null || echo "!! uv not found (only needed for /transcribe): brew install uv"
echo "Installed: /dl /formula /transcribe + 11 /yt-* skills -> $DST"
echo "Next: fill in ~/.claude/youtube/voice.md (every /yt-* skill reads it)"
echo "Next: create your brand kit -> cp $DST/formula/brands/_template.md $DST/formula/brands/<brand>.md"
