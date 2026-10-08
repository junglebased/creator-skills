---
name: formula
description: Viral content formula engine. Give it one link (an Instagram account, a saved collection, a single post, a TikTok/YouTube channel or a list of links) and it downloads the content, analyses every post (cover, slides, video frames, transcript, caption, metrics) and writes a "Format DNA" report — hook bank, viral elements with lift scores, design system (palette, type, layout), caption formula, CTA bank, format templates and outliers. Then, given an idea, it produces that idea in the winning format with your own brand kit, designed in Claude Design. Use when the user says "/formula", "analyse this account", "analyse this collection", "reverse-engineer this creator", "build a hook bank", "make this in that format", "competitor / reference analysis".
---

# formula — from reference to formula, from formula to content

Three modes. Read the user's message: one link = `analyze`; link + idea = `analyze` then `make`; idea only = `make` with the latest / best-fitting model.

- Engine: `formula.py` (next to this file). Needs network → run it outside any sandbox.
- Analysis schema: `codebook.md`. Brand kits: `brands/<brand>.md` (copy `brands/_template.md`).
- Sibling skills used: `../dl` (downloads), `../transcribe` (local Whisper, Apple Silicon).
- Model folder: `$FORMULA_HOME/<model-name>/` (default `~/formula-models/`). All models form one library.
- Browser for login cookies: `FORMULA_BROWSER` (default `chrome`). Instagram photos/carousels/saved need the user logged in there.

---

## MODE 1 — analyze `<link>` [--limit 60] [--deep]

### 1. Collect (script, run in background for big sets)
```bash
F=<this skill dir>/formula.py; W="${FORMULA_HOME:-$HOME/formula-models}/<model-name>"
python3 $F fetch "<LINK>" "$W" --limit 60    # account: last 60 posts + reels; collection/saved: all
python3 $F build "$W" [--baseline]           # --deep → --baseline (account-median outlier score, slow)
python3 $F table "$W" --top 40
```
- Already downloaded folder? `ln -s <folder> "$W/media"` instead of fetch.
- Login error → tell the user to log in to the platform in their browser. Never ask for passwords.
- `build` makes a contact sheet per post (`sheets/<id>.jpg`), video frames (0, 1.5, 3 s, 25/50/75 %, end), dominant colors, local transcripts, yt-dlp comment counts. Instagram does not expose view counts this way; ranking falls back to likes.

### 2. Select
From `table`: top ~30 % by outlier / relative score (min 8, max 25) + the bottom 5 as a control group. Small sets: all posts.

### 3. Per-post analysis (parallel agents)
- Groups of 8–13 posts, at most 2 agents at once (a mid-size model is enough). Give each agent: `codebook.md`, the post's `sheets/<id>.jpg` (it must actually LOOK at the image), `transcripts/<id>.timed.txt` (first 40 lines), its `posts.jsonl` line, and a one-line description of each brand in `brands/`.
- Each agent writes `analysis/<id>.json` (codebook schema). Report ≤10 lines.
- No analysis without looking: typography, layout and first frame are verified from the image.

### 4. Synthesis → `FORMAT_DNA.md` (the deliverable)
Numbers first: `python3 $F synth "$W"` → `elements.csv` (feature | all% | top% | low% | lift) and `hook_bank.csv`. Never count by hand.
Then write, from `analysis/*.json` + synth output:
1. **Summary card** — source, post count, date range, medians, the formula in one sentence.
2. **Outliers** — top 10: link, metric, hook, why it worked. Plus what flopped and why.
3. **Rules** — features with lift ≥ 1.5 (top% vs low%). Separate *reach* posts from *lead* posts if the data shows it.
4. **Hook bank** — every hook verbatim + type + performance; the best 10 turned into **fill-in templates**.
5. **Design system** — palette clusters (hex), type class, text placement, accent technique, density, slide count; video length, cut pace, caption style. End with a one-paragraph **Claude Design brief**.
6. **Format templates** — F1..Fn: name, skeleton (beats + slides/seconds), reference posts, when to use.
7. **Caption formula + CTA bank** — verbatim CTAs with type and performance.
8. **Do not copy** — account-specific elements.
9. **Brand adaptation** — per `brands/*.md`: take / transform / leave + the brand's **10x layer** (what none of the references do, from the brand's unfair advantage).
10. **Idea → format map** — idea type → template code.

Caveat honestly in the report: sample size, mixed accounts, missing view counts. Lift is direction, not proof.

### 5. Close
≤8 lines in chat: formula in one sentence, 3 strongest rules (with lift), 3 best hook templates, file path. Ask: "Give me an idea and I'll make it in this format."

---

## MODE 2 — make `<idea>` [--model <name>] [--brand <code>] [--format F#] [--type carousel|reel|post]

1. **Pick the model:** given, or the latest / best match via each model's idea → format map. Several models → merge their strongest rules.
2. **Brand:** read `brands/<code>.md`. Missing fields → ask once, in one message. Never invent facts, numbers, dates or quotes about the brand or its people; leave `[SOURCE?]` / `[YEAR?]`.
3. **Brief:** format code, hook (template from the bank + 3 variants), beat-by-beat flow, per slide/scene: text + visual note (real asset path if one exists), CTA (brand's CTA for this content pillar), caption, hashtags. Run the copy through an anti-AI-writing pass if one is available.
4. **Claude Design:** use the Artifact tool — `action: "quickstart"` with intent `design` (single visual / carousel / reel storyboard) or `slides` (multi-slide carousel). Pass the brand tokens (colors, fonts, logo), the model's Claude Design brief and the slide copy. 4:5 carousel (1080×1350), 9:16 reel cover/storyboard (1080×1920).
5. **Deliver:** artifact link + `<model>/made/<date>_<slug>.md` (brief, caption, sources, `Reference format: F# — <link>`).
6. **Feedback loop:** when the user reports results, append to `$FORMULA_HOME/_performance.csv` (date, brand, format, hook type, metrics). Future `make` runs weigh it.

---

## MODE 3 — library
Scan every model in `$FORMULA_HOME` → `LIBRARY.md`: model list, cross-model rules (lift ≥ 1.5 in 2+ models), merged hook bank tagged by brand fit. Update whenever a model is added.

---

## Rules
- References are for analysis. Never suggest reposting or copying text/visuals verbatim; hooks are abstracted into templates.
- Metrics come from data; missing → "no data". Hidden-like posts are flagged, not ranked.
- Pareto: deep-analyse at most 25 posts per model; the rest count only through captions + metrics.
- Rate limit (HTTP 429) → stop, resume in ~15 min. The browser session is the user's: never log out or change anything there.
