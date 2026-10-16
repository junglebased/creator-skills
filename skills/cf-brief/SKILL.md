---
name: cf-brief
description: First step of the Content Factory for any brand and format (carousel, reel, cover, LinkedIn post, deck slide). Turns an idea into a one-page brief with one goal, funnel stage, reference format, a slot list (each slide/scene = what it must SAY + what it must SHOW as visual-index topic tags + text position), one CTA and how success is measured. Writes 02 Metin/<code>.brief.md and the empty slides.json skeleton the later steps fill. Use when the user says "/cf-brief", "brief", "yeni carousel", "bu fikirden içerik", "şunu carousel yap", or before /formula make on a production that has a visual index.
---

# cf-brief

Pipeline: `**brief** → source-gate → visual-index/select → copy → design → caption/CTA → QA → publish-pack`.
Contract: `docs/CF-PIECE-CONTRACT.md`. Builds on `/formula make` (reference formats, hook bank), the Creative
Concept Engine (Persona × Angle × Mechanism + funnel stage) and `/ripplefx` (RS ripple layer).

## Inputs
- The idea (one sentence) + brand code + channel/format. Missing → ask once, in one message.
- Brand kit (`~/.claude/skills/formula/brands/<code>.md`), goal lock if any (`/goal-lock`).
- Reference format: a `/formula` model's F# template + link (never copy text or visuals).
- The production's visual index `topics.md` (so slot visuals use real tags).

## Brief (one page) → `02 Metin/<code>.brief.md`
| field | rule |
|---|---|
| Goal | ONE measurable outcome (e.g. "OMB comments in 48 h"); not "awareness" |
| Funnel stage | discover · trust · convert · retain |
| Persona × angle × mechanism | one line each |
| Reference | `F# — <link>`: what we take / don't take / transform |
| Hook | 3 variants from the hook bank, one chosen |
| Slot list | table: `n · role · says (≤1 sentence) · shows (topic tags) · ratio · text_pos · source ids needed` |
| CTA | one keyword or one link; same as the brand kit's CTA for the pillar |
| Measure | what is read at 48 h and the threshold that means "it works" |
| Out of scope | what this piece will not try to do |

Slot rules: cover = face or hands + the hook (q5 visual); ≥3 shot types across slots; ripple slot before the
CTA for RS (person → family/neighbours → village/ecosystem, every ring sourced); one video slot max 1–2 per
carousel; CTA slot shows the thing they get (lead magnet cover).

## Skeleton
Write `02 Metin/<code>.slides.json` with `code, campaign, brand, format, cta_keyword` and one object per slot
(`n, role, headline: [], body: [], visual: "", text_pos, sources: []`). Later steps fill it; nobody renames
slots.

## Gate (step done)
Slot list complete, each slot has `shows` tags that exist in `topics.md`, one CTA, the user said yes to the
brief (one message: "brief OK?").
