---
name: cf-qa
description: Pre-publish QA for one Content Factory piece (carousel, cover, reel cover) for any brand. Checks slide text against the line-break rules (R1: lines, characters per line, balance, widows), banned words, punctuation, open [SOURCE?] placeholders, numbers without sources, CTA keyword consistency (slide = caption = ManyChat trigger), hashtags/emoji limits, export sizes and count, visual repeats across campaigns, consent and brand-risk frames, shot-type diversity, cover quality and the series look (R3). Writes 04 Export/QA.md with PASS/WARN/FAIL. Use before anything is scheduled or handed over, and when the user says "/cf-qa", "QA", "kontrol et", "yayına hazır mı", "check the carousel".
---

# cf-qa

Pipeline: `brief → source-gate → visual-index/select → copy → design → caption/CTA → **QA** → publish-pack`.
Contract: `docs/CF-PIECE-CONTRACT.md` · rules: `docs/CF-PRODUCTION-RULES.md` (R1–R3).

## Run
```bash
python3 <skill>/scripts/cfqa.py "<piece folder>" \
  --index "<pool>/_Visual Index" --brand-kit ~/.claude/skills/formula/brands/<brand>.md \
  [--size 1080x1350] [--manychat OMB]
```
- Reads `02 Metin/<code>.slides.json`, `<code>.caption.md`, `04 Export/*.png`, the visual index (`index.csv`
  incl. `used_in`, `consent`, `dup_group`) and the brand kit (`chars_per_line`, `banned_words`).
- Writes `04 Export/QA.md` (never overwrites: `QA-v2.md`…). Exit 1 if any FAIL.
- Missing `slides.json`: build it from the copy file first (cf-copy step) — QA on prose is guesswork.

## What it checks
| area | FAIL | WARN |
|---|---|---|
| R1 text | line > limit +15 %, lines > 3 (headline > 4), text as one string, banned word, `[SOURCE?]`, digit without `sources` | line > limit, 4-line headline, unbalanced lines (max/min > 1.8), one-word last line, `!`, em dash, emoji on slide |
| CTA | keyword missing on CTA slide or caption, ManyChat trigger ≠ keyword, CTA slide without `cta_keyword` | trigger not stated, link-in-bio next to keyword CTA |
| caption | hashtags > max, emoji > max, banned word, placeholder | >1 em dash, `!` |
| exports | wrong pixel size, > 20 slides | missing exports, fewer PNGs than still slides |
| visuals | id not in index, `consent: no` (incl. brand/cigarette/alcohol), used in another campaign, same `dup_group` twice | `consent: check`, risk words in notes, quality < 3, < 3 shot types, 3 same shot types in a row, > 40 % from one source, cover < q5 |
| hook / title | none (WARN only) | hook score < 3/4 (slide 1: number or question, <= 12 words, no greeting opener, not ALL CAPS); caption first line > 90 chars, ALL CAPS, > 1 `!`/`?`, clickbait phrase |
| R3 look | look file missing | no look set, no compare grid |

## After the run
1. Fix every FAIL (or get the user's explicit waiver, written into QA.md by hand under "Waivers").
2. Read the WARNs to the user in one short list; they decide.
3. Re-run until 0 FAIL, then hand over to cf-publish-pack.
4. Things the script cannot see — check by eye on the exports: Turkish diacritics rendered (ı İ ğ ş ç ö ü),
   text inside the safe area and not over faces, logo position, the compare grid reads as one film.
