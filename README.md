# Creator Skills for Claude

Three Claude skills that turn the posts you save into a content system.

| Skill | What it does |
|---|---|
| **`/dl`** | Downloads any link (Instagram reels, carousels, stories, **your saved collections**, TikTok, YouTube, X, Vimeo, Pinterest) into a folder, with the caption next to it. Free, no daily caps, full quality. |
| **`/formula`** | Give it an account, a saved collection or a list of posts. It downloads everything, **looks at every post** (cover, slides, video frames, transcript, caption, metrics) and writes a **Format DNA** report: hook bank, viral elements with lift scores, design system, caption formula, CTA bank, format templates. Then give it an idea and it makes it **in that format with your brand kit**, designed in Claude Design. |
| **`/transcribe`** | Free local transcription on Apple Silicon (Whisper large-v3-turbo via MLX). Text, timecoded, SRT/VTT, paper-edit Markdown. |

Built by a documentary filmmaker ([@junglebased](https://instagram.com/junglebased)) who got tired of a Telegram bot saying "5 downloads a day".

## What a Format DNA report looks like

From a real run on 26 saved posts:

```
Rules (lift = share in top posts / share in bottom posts)
open-loop (answer at the end)       top 75%   low 0%    lift 16.0
community identity                  top 75%   low 12%   lift 4.7
debate trigger                      top 38%   low 0%    lift 8.6
human-scale number                  top 38%   low 0%    lift 8.6
60+ words per slide                 -> only in the flops
```
…plus every hook verbatim and as a fill-in template, palette clusters in hex, type and layout rules, a one-paragraph brief for Claude Design, and F1–F7 format skeletons mapped to idea types.

## Install

Requirements: macOS or Linux, Python 3.10+, `ffmpeg`. `/transcribe` needs Apple Silicon and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/junglebased/creator-skills.git
cd creator-skills
./install.sh            # copies skills to ~/.claude/skills and installs yt-dlp + gallery-dl in a local venv
```

Then in Claude Code:

```
/formula https://www.instagram.com/<account>/
/formula https://www.instagram.com/<you>/saved/<collection>/<id>/
/formula make "my idea" --brand mybrand
/dl ~/refs https://www.instagram.com/reel/XXXX/
```

**Claude.ai / Desktop:** upload the zips from `dist/` under *Settings → Capabilities → Skills*. (`/formula` and `/dl` need a shell with network access, so they work best in Claude Code.)

### Your brand kit
Copy `skills/formula/brands/_template.md` to `~/.claude/skills/formula/brands/<yourbrand>.md` and fill it in: voice, banned words, colors (hex), fonts, CTA per content pillar, your "10x layer". `make` mode reads it. Brand kits stay local and are git-ignored.

### Logins
Instagram photos, carousels and saved collections need you to be logged in to Instagram in your browser (`chrome` by default; set `FORMULA_BROWSER=firefox` etc.). The tools read the browser's cookies locally. Nothing is sent anywhere else, and no passwords are ever asked for.

## How `/formula` works

```
link ──► fetch (gallery-dl / yt-dlp) ──► build: contact sheets, video frames, palette, transcripts, metrics
     ──► select top 30% + bottom 5 ──► parallel agents look at each post (codebook.md schema)
     ──► synth: lift table + hook bank (counted by script, not by vibe)
     ──► FORMAT_DNA.md ──► make: idea → template → brand kit → Claude Design
```

Every analysis is saved, so models pile up into a library (`/formula library`) and your own post results can be fed back (`_performance.csv`).

## Honest limits
- Instagram doesn't expose view counts to these tools; ranking falls back to likes (and comments for video). Use `build --baseline` to normalise by each account's median.
- Small samples give direction, not proof. The report says so.
- Whisper hallucinates on music-only videos; `/formula` filters that out.

## Use responsibly
Download for reference and analysis. Don't repost other people's work. Respect each platform's terms and creators' rights; `/formula` abstracts hooks into templates instead of copying them.

## License
MIT
