---
name: cf-caption-cta
description: Writes the caption, hashtags, CTA keyword and the first DM for one Content Factory piece, for any brand and platform, from the piece's slides.json and sources — and keeps the CTA keyword identical on the CTA slide, in the caption and in the ManyChat (or other DM tool) trigger. Builds on the generic caption-and-cta skill and the brand's voice doc. Output 02 Metin/<code>.caption.md. Use when the user says "/cf-caption-cta", "caption yaz", "CTA", "yorum kelimesi", "ManyChat DM metni", or after the copy step of a carousel/reel.
---

# cf-caption-cta

Pipeline: `… → copy → design → **caption/CTA** → QA → publish-pack`.
Contract: `docs/CF-PIECE-CONTRACT.md` · rules: `docs/CF-PRODUCTION-RULES.md`.

## Inputs (read, in this order)
1. `02 Metin/<code>.slides.json` (what the slides already say; the caption does not repeat them line by line).
2. `02 Metin/<code>.sources.md` (every number/quote in the caption needs a source id there).
3. The brand's voice doc and brand kit: banned words, emoji/hashtag limits, CTA per pillar.
   RS: `~/Desktop/2 Areas/Regenerative Stories/.claude/brand-voice-guidelines.md` (section "Carousel, Caption
   & CTA Rules") + `~/.claude/skills/formula/brands/rs.md`.
4. The generic `caption-and-cta` skill for platform patterns (IG keyword CTA, LinkedIn link, X reply).

## One keyword rule
- One CTA per post, one keyword, upper case, one word (e.g. `OMB`, `BAHÇE`).
- The same keyword in three places: CTA slide text, caption CTA line, DM tool trigger. Write all three into
  `<code>.caption.md` (`keyword`, `manychat_trigger`) so cf-qa can compare them.
- Comment-keyword CTA → no "link in bio" in the same caption. Never require a follow to receive the lead magnet.
- The DM text names what they get (title, pages, format) and carries the link placeholder `{link}`; the actual
  link is filled in the DM tool, not in the caption.

## Caption shape (default; the brand kit may override)
1. Line 1 = the hook restated as a plain sentence (not the cover text verbatim).
2. 2–3 short paragraphs: concrete scene → the sourced number/quote, attributed ("ona göre", "kendisi söylüyor").
3. Share line (who to send it to) — optional.
4. CTA line with the keyword.
5. Hashtags on their own block (RS ≤5, collab 2–3).
Run the anti-AI writing filter / banned-word scan on the result. No `!`, ≤1 emoji, no em-dash piles.

## Output: `02 Metin/<code>.caption.md`
```
## Caption
…
## Hashtags
#… (≤ max)
## CTA
keyword: OMB
manychat_trigger: OMB
dm_text: Merhaba! İşte Onarıcı Mikro Bahçe kurulum rehberi (20 sayfa, PDF): {link}
## Sources used
Q2, V1
```
Then run cf-qa; a mismatch between the three keyword places is a FAIL there.
Collab posts: write the partner's caption variant under `## Collab caption` (soft CTA, their voice, 2–3 tags).
