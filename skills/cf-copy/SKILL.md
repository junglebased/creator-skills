---
name: cf-copy
description: Writes the on-slide text of a Content Factory piece for any brand into 02 Metin/<code>.slides.json with MANUAL, balanced line breaks (rule R1: headline ≤3 lines, body ≤3, characters per line from the brand kit), one idea per slide, every number tied to a source id, banned words and AI tells removed. Builds on /formula make (hook bank, format template), the brand's copy agent (e.g. rs-content-marketing) and the anti-AI writing filter. Use when the user says "/cf-copy", "slayt metni", "carousel metni", "satır kır", "metni sığdır", or after the source gate.
---

# cf-copy

Pipeline: `brief → source-gate → visual-index/select → **copy** → design → …`.
Contract: `docs/CF-PIECE-CONTRACT.md` · R1 in `docs/CF-PRODUCTION-RULES.md`.

## Steps
1. Read the brief (slot list), `sources.md`, the selected visuals (`visual` per slot + `text_safe` from the
   visual index) and the brand kit (`chars_per_line`, banned words, voice).
   RS: run the `rs-content-marketing` agent for the draft; it already follows these rules.
2. Write each slot: headline = the slot's one idea; body = proof (sourced) or the next step. Short opener →
   concrete scene/number → short close across the deck.
3. Break lines by hand (R1): comma/sentence end first, then phrase boundary; similar line lengths; no one-word
   last line; never split number+unit, name+surname, adjective+noun. Count characters against the brand kit;
   over → shorten, then size down one step.
4. Text position follows the picked visual's `text_safe` (cover text never over the face).
5. Anti-AI pass (banned list scan), GreenSHOUTING pass on claims.
6. Write `headline`/`body` as arrays of lines into `slides.json`; `sources` ids per slot.
7. Run `cf-qa` once for the text checks before design (exports will WARN as missing; that's fine).

## Gate
cf-qa shows no R1/banned/source FAIL; the user approved the text (one message with all slides as lines).
