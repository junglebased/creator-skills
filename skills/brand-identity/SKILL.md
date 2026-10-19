---
name: brand-identity
description: Builds a complete brand identity for any person, studio or client — discovery from existing material, positioning + archetype, voice & messaging, visual identity (palette, type, logo brief), and a finished brand book as HTML + A4 PDF plus a machine-readable brand kit. Use whenever the user says "/brand-identity", "brand identity", "brand book", "brand guidelines for a client", "positioning", "archetype", "brand voice and visuals", "marka kimliği", "marka rehberi", "konumlandırma", or wants one coherent brand for JungleBased, Berkay Tunalı, Regenerative Stories or a client, even if they only say "we have no unified brand" or "make this look like one brand". Reads existing files first and asks only about gaps.
---

# brand-identity — from scattered pieces to one brand book

One flow, any brand. Berkay's own brands and client brands (JB = paid work) run through the same six stages. The point: never invent what a file already says, never ask what material already answers, and end with something a designer or another skill can use without a call.

Sibling consumers of the output: `/formula make` and `cf-*` read `brand-kit.md` (same shape as `formula/brands/_template.md`), `motion` reads the colour/type tokens.

## Setup (once per brand)
1. Pick a brand folder: `<Area>/…/Brand & Positioning/<YYYYMMDD> <Name> Brand/` (or the client's Area). Create `brand/` inside it. Every stage writes one file there, so work survives a session rotation.
2. Create `brand/decisions.md` (append-only: date · decision · why). Anything the user decides goes here; later stages obey it.
3. Two linked brands (e.g. studio + personal): run the stages for each, then add the shared architecture page (`references/positioning.md` → "Brand architecture").

## Stages — do in order, one file each, show the user a 5-line summary after each, move on unless they object
| # | Stage | Reads | Writes |
|---|---|---|---|
| 1 | Discover | `references/interview.md` | `brand/01-discovery.md` |
| 2 | Position + archetype | `references/positioning.md`, `references/archetypes.md` | `brand/02-positioning.md` |
| 3 | Voice + messaging | `references/voice.md` | `brand/03-voice.md` |
| 4 | Visual identity | `references/visual.md` | `brand/04-visual.md` |
| 5 | Brand book | `references/brandbook-spec.md` | `brand/brand.json` → HTML, PDF, `brand-kit.md` |
| 6 | Review gate | checklist below | `brand/06-review.md` |

Read only the reference for the stage you are in; they are long on purpose so this file stays short.

### 1 Discover — inputs first
Collect what exists before asking anything: user-named folders/URLs, `~/.claude/FACTS.md` and `~/.claude/profile/` (for Berkay's brands), site CSS tokens, email signatures, decks, past work, competitor/reference links. For connected platforms use `brand-voice:discover-brand`. Build a **known / gap table** (each row: topic · what we know · source tag · confidence). Then interview only the gaps: max ~12 questions in 2 rounds, batched, multiple-choice where possible. Why: the user's attention is the scarce resource; a brand built on re-asked questions feels like a form.

### 2 Position + archetype
Audience and frame of reference first, then the positioning statement, then the archetype pair (primary + shadow) with a one-line "why this, not the neighbour". Offer 2-3 positioning routes when the material supports more than one; recommend one. Record proof points with sources.

### 3 Voice + messaging
Three voice adjectives each with a do/don't sentence pair taken from the user's own writing where possible; tone map by context; tagline routes (3-5); 10/30/60-second pitches; messaging pillars; banned words. Run every sentence of brand copy through `anthropic-skills:anti-ai-writing-filter`. If the brand writes in two languages, write each natively, not translated.

### 4 Visual identity
Start from existing tokens (site CSS, current logo, signatures) and say what you keep, fix, add. Palette with roles, run `scripts/contrast.py` and fix failures; type pairing with licence/availability note; **logo brief only** (concept routes, rules, clear space, misuse, what the designer must deliver) — no final logo art; imagery, motion and grain rules. Photo direction must match the positioning, not stock taste.

### 5 Brand book
Fill `brand/brand.json` from stages 1-4 (schema in `references/brandbook-spec.md`; example in `fixtures/fixture-brand.json`). Then:
```bash
S=<this skill dir>/scripts
python3 $S/build_book.py brand/brand.json brand/        # → brand-book.html + brand-kit.md
python3 $S/html2pdf.py brand/brand-book.html brand/brand-book.pdf   # A4 portrait via headless Chrome; reports page count
```
Publish the HTML as an artifact when the user wants to share it, and archive per `~/.claude/CLAUDE.md` (artifact rule). Save the PDF/HTML to the brand folder with a `YYYYMMDD` English name; never overwrite (-v2).

### 6 Review gate (write `brand/06-review.md`, fix before delivering)
- Positioning, voice and visuals tell the same story (read the three one-liners side by side).
- Every fact has a source tag (`[FACTS]`, `[site]`, `[interview]`, `[file: …]`); nothing invented.
- Contrast: all text/background pairs ≥ 4.5:1 (large text 3:1).
- PDF: every section starts on its own page, none splits, no orphan heading, no blank page — open and look at every page.
- Anti-AI filter pass done on all copy; banned words absent.
- `brand-kit.md` has no empty fields (or each empty field is marked `TODO(ask)`).

## Rules that keep it good
- Show the user options only where the material truly allows several; otherwise decide and note it in `decisions.md`.
- The user's own words beat polished ones: quote them in voice samples.
- Keep personal-data discipline: no phones, tax IDs, or private emails in the book (FACTS.md "internal only" rules apply).
- Stay in scope: no website build, no print production, no trademark/domain checks. Flag them as next steps.
- Credits for adapted structure are in `references/CREDITS.md`.
