---
name: resolve
description: Drive DaVinci Resolve Studio from Claude Code as an assistant editor — read projects, bins and clips, turn a selects CSV into clip markers or a new rough-cut timeline, snapshot timelines (OTIO/EDL/.drp) and queue renders. Add-only and dry-run by default. Use when the user says "/resolve", "Resolve'da", "DaVinci", "timeline kur", "seçkiyi marker'la", "kaba kurgu", "render al", or works on an RS episode/Reel edit.
---

# Resolve (assistant editor bridge)

SPEC: `~/code/agentic-os/docs/SPEC-20261013-davinci-suite.md`. Plan first, then this skill.

## Before anything
- Resolve **Studio** open, Preferences → System → General → External scripting using = **Local**.
- Run with Python 3.12 and the sandbox disabled (the API talks to the running app):
  `uv run --python 3.12 ~/.claude/skills/resolve/resolve_ctl.py status`

## Commands
| Need | Command | Writes? |
|---|---|---|
| What's open | `status` · `projects` · `timelines` | no |
| What this build can do | `api` (lists methods per object; compare with the README) | no |
| Ingest report | `clips --csv "<Film>/03 Post/01 Ingest/ingest.csv"` | csv only |
| G1 selects on clips | `markers-from-csv selects.csv [--apply]` (ring 1/2/3 → Blue/Green/Yellow) | markers |
| Rough cut | `timeline-from-csv selects.csv --name "R1 v1" [--apply]` (new timeline only) | new timeline |
| Version record | `snapshot --out "<Film>/03 Post/04 Kurgu" [--apply]` (OTIO + EDL + .drp, timestamped) | files |
| Render | `render --preset "<preset>" --out "<Content>/04 Export" --file r1_01 [--apply]` | new file |

`selects.csv`: `clip,in,out,speaker,quote,ring,score,reason` — `in/out` in seconds or source timecode.

## Rules (do not bend)
1. Always run without `--apply` first and show the plan; apply only after the user's OK at a gate (G1 selects, G2 rough cut, G4 final).
2. Never delete, overwrite or rename: no clip/timeline/project deletion, no re-render over an existing file, no moving raw media.
3. Log every write: `--log "<Film>/03 Post/log.jsonl"`.
4. Resolve can't trim/roll, build node trees or Fairlight FX chains by script: say so and leave it to the template project or Berkay.
5. Never publish (Quick Export "EnableUpload" stays off).
