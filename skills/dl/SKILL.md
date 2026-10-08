---
name: dl
description: Free, unlimited media downloader. Downloads Instagram reels/posts/carousels/stories and saved collections, TikTok, YouTube, X/Twitter, Facebook, Vimeo and Pinterest links straight into a target folder, with a caption .txt next to each. Use when the user says "/dl", "download this", "save these links to X", "download my saved posts", or pastes links and wants the media.
---

# dl — link to folder

Engine: `dl.py` next to this file (yt-dlp for video, gallery-dl for photos/carousels/saved, browser login cookies). Needs network → run outside any sandbox.

```bash
D=<this skill dir>/dl.py
python3 $D "<DEST>" URL [URL...]                 # file name = platform id
python3 $D "<DEST>" CODE1=URL1 CODE2=URL2        # file name = CODE_01.ext ...
python3 $D "<DEST>" --list links.txt             # lines: "CODE URL"
python3 $D "<DEST>" --browser firefox URL        # cookie source (default chrome)
```
More than 10 links or a saved collection → run in background.

## Destination
Use the folder the user names. Otherwise infer it from context (the project / content pillar the reference belongs to). Ambiguous → ask one question.

## Instagram saved posts / collections
The account logged in to the browser is the one whose saves come down.
```bash
G=gallery-dl   # or <skills>/.venv/bin/gallery-dl
$G --cookies-from-browser chrome "https://www.instagram.com/<user>/saved/"   # list collections
$G --cookies-from-browser chrome --write-metadata --sleep-request 2-5 \
   --download-archive "<DEST>/.archive.sqlite3" \
   -D "<DEST>/<collection>" -f "{date:%Y%m%d}_{username}_{post_shortcode}_{num:>02}.{extension}" \
   "https://www.instagram.com/<user>/saved/<collection>/<id>/"
```
`post_shortcode` keeps every slide of a carousel under the same post code. `--download-archive` stops duplicates across collections; download the named collections first, `all-posts` last.

## Errors
- `login` → ask the user to log in to that platform in the browser. Never ask for or type passwords.
- HTTP 429 → wait 10–15 min, raise `--sleep-request`.
- Missing tools → `pip install yt-dlp gallery-dl` (needs ffmpeg for merging).

## Rules
- Only the links/lists the user gave. Downloads are for reference and analysis; don't suggest reposting other people's content.
- An existing `CODE_*` file is skipped, never overwritten.
