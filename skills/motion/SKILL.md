---
name: motion
description: Motion agent for Regenerative Stories (and later JungleBased) — turns one case or topic plus sourced numbers into a brand-locked animated 9:16 reel (HyperFrames → MP4) with the RS "dalga etkisi" ripple layer. Fills a reel JSON for a preset, renders locally, exports 3 review frames into the Area's 00 Drafts. Draft only, never publishes. Use when the user says "/motion", "motion", "animasyon", "reel animasyonu", "case study animasyonu", "dalga etkisi reel", or wants a film's numbers turned into an animated Reel.
---

# motion — sourced numbers → brand-locked animated reel

SPEC: `docs/SPEC-20261012-motion-agent.md` in creator-skills (presets §4, QA §7). Renderer: **HyperFrames** (HTML + GSAP → headless Chrome → FFmpeg). Fallback: Remotion, only if HyperFrames blocks on a feature.

**Mac gerekli.** Render runs locally: Node + `npx hyperframes@0.8.150`, ffmpeg, Chrome, local port binding (renderer serves on 127.0.0.1), the licensed RS fonts and 4K film stills from `~/Desktop/2 Areas/…`. A cloud session can write/validate the reel JSON, not render it. In Claude Code, run `build.sh` with the sandbox off (port binding).

## Presets
| Id | Status | Use |
|---|---|---|
| `rs-field-glass` | **ready** (`templates/rs-field-glass/`) | 9:16, 18 s: hook → 3 ripple rings, one sourced number each → end card |
| `rs-ripple-rings` | planned | rings-only "dalga etkisi" loop (person → family → village → ecosystem) |
| `rs-footage-to-data` | planned | footage plate match-cuts into a diagram |
| `rs-map-tr` | planned | 3D Türkiye map, pin + region draw-on |
| `jb-process-mono` | planned | JB behind-the-scenes, frame counters, wipes |
| `jb-keynote-glass` | planned | JB tool/workflow posts |

Planned = brief exists in the SPEC, no template yet. Ask before building one; it is a ✨ job, not a fill.

## Flow
1. **Case + numbers.** Pin the film/case and collect candidate numbers from `~/.claude/FACTS.md`, then Notion / transcripts / case studies. Each number goes in `facts[]` with value, scope, date, source (interview timecode, public counter + date). **No source, no number on screen.** Yield/health/carbon/"feeds N" = attributed to the practitioner ("Burhan’ın gözlemi"). Views are views, never people. `~` values in FACTS = re-read at source first.
2. **RS ripple layer (/ripplefx).** Map numbers to rings: person → family/neighbour → village/cooperative/ecosystem. If ring 3 has no sourced number, say so and use a sourced fallback (e.g. film views) rather than invent.
3. **Preset.** `rs-field-glass` for now. Other presets: list them as planned, don't fake.
4. **Fill the reel JSON.** Copy `reels/20261013-mikro-onarim.json` → `reels/YYYYMMDD-<slug>.json`. Fields: `slug`, `area_out` (the Area's `…/00 Drafts`), `stills_dir` + 3 `plates` (`src`, `x` = 9:16 crop offset in a 3840-wide still), `facts[]`, `scene` (label, hook, 3 rings, end card). Ring: `digits` (odometer) or `text` (static), `unit`, `line` (≤5-word headline feel, `<em>` = gold, one word max), optional `attr`, required `source`. Show the filled JSON to Berkay before rendering if any number is new.
5. **Render.** `~/.claude/skills/motion/templates/rs-field-glass/build.sh <reel.json> [out_dir]` → `<Area>/…/00 Drafts/<slug>.mp4` + `-00s.png`, `-08s.png`, `-end.png`. Never overwrites: an existing name becomes `-v2`, `-v3`. Validation aborts if a ring lacks a source.
6. **QA** (SPEC §7, plus `rs-greenshouting-check` on the copy): read the 3 frames, check diacritics, safe zone y 220–1520, gold once, no em dashes/exclamation marks, 1080×1920 / 30 fps / 18 s / <30 MB.
7. **Hand-off.** Paths of MP4 + frames + the facts table. **Yayın yok, onay Berkay’da.** No posting, scheduling or uploading.

Default RS out: `~/Desktop/2 Areas/Regenerative Stories/05 Channels & Social/00 Drafts/`. JB/DC: their own `00 Inbox` or `…/00 Drafts` per PROJECTS.md.

## Files
| Path | Role |
|---|---|
| `templates/rs-field-glass/build.sh` | reel JSON → scratch copy of `composition/` → fonts + plates + `scene.js` → render → frames |
| `templates/rs-field-glass/composition/` | HyperFrames project (`index.html` timeline, `tokens.css`, `scene.js` default, `meta.json`/`hyperframes.json` project meta: don't edit per reel) |
| `templates/rs-field-glass/README.md` | locked brief (BAR · FORMAT · ONE RULE · LOOK · TYPE · MOTION · NEVER) |
| `reels/*.json` | one file per reel (content + sources); the only thing edited per reel |

Env: `HF=/path/to/hyperframes` local CLI, `RS_FONTS=<dir>` other font dir. Lint in place: `cd templates/rs-field-glass/composition && npx hyperframes@0.8.150 check` (needs fonts/plates in `assets/`).
