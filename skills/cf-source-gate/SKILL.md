---
name: cf-source-gate
description: Source gate for any Content Factory piece and brand. Every number, quote, award, date and claim that will appear on a slide or in a caption gets an id, a source, a locator (interview timecode, page, URL + date read) and a status in 02 Metin/<code>.sources.md, before copy is final. Pulls verified facts from FACTS.md, transcripts (/transcribe timecodes) and the claim rules of rs-greenshouting-check; blocks [SOURCE?] from reaching design. Use when the user says "/cf-source-gate", "kaynak kontrol", "rakamlar doğru mu", "alıntıyı teyit et", "greenshouting", or between brief and copy.
---

# cf-source-gate

Pipeline: `brief → **source-gate** → visual-index/select → copy → …`.
Contract: `docs/CF-PIECE-CONTRACT.md`. Builds on `rs-greenshouting-check` (claim table, two independent
sources for impact claims, Deny/Delay/Distort flags), `/transcribe` (timecoded quotes), `/motion` facts rule
("no source, no number on screen") and `~/.claude/FACTS.md` (canonical numbers; `~` = re-read at source).

## Output → `02 Metin/<code>.sources.md`
```
| id | claim (as it will be written) | type | source | locator | read on | status |
|----|------|------|--------|---------|---------|--------|
| Q1 | "Gıda ihtiyacı karşılanmaz…" | quote | Burhan interview 2026 | A 10:02:10–10:02:41 | 2026-10-09 | ASR: verify by ear |
| V1 | 250.000+ izleyen | number | YouTube Studio | screenshot 13 Oct | 2026-10-13 | verified |
| F1 | Toprak atmosferin ~2 katı karbon tutar | science | FAO 2017 | p. 2, URL | 2026-10-12 | verified |
```
Types: number · quote · science · award · date · attribution. Status: `verified` · `ASR: verify by ear` ·
`attributed` (practitioner's own observation, written as "ona göre") · `open` (blocks design).

## Rules
1. Numbers come from the canonical store first (FACTS.md or the brand's facts file). A drifting number
   (three different counts across files) → use the freshest dated primary read; say which.
2. Quotes only verbatim from transcript, with timecode; raw ASR quotes stay `ASR: verify by ear` until a human
   listened. Paraphrase is marked as paraphrase, never in quote marks.
3. Impact/yield/health/carbon claims about a practitioner's method → attributed ("Burhan'a göre"), unless
   two independent sources. Views are views, never "people reached".
4. GreenSHOUTING words (kurtarır, mucize, %100, sıfır atık, "iklimi çözer") are rewritten, not sourced.
5. Each slot in `slides.json` lists its source ids; cf-qa fails a slide with digits and no source id.

## Gate (step done)
No row `open`; every number/quote in `slides.json` and the caption maps to a row; ASR rows listed for the
human to check by ear before publishing (cf-publish-pack checklist).
