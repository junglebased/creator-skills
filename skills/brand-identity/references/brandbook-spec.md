# Stage 5 — Brand book spec

## Pages (A4 portrait, one section per page, none splits)
1 Cover · 2 Contents + how to use · 3 Story and belief · 4 Positioning · 5 Audience and proof · 6 Archetype and personality · 7 Voice · 8 Tone map · 9 Messaging (taglines, pitches) · 10 Logo brief · 11 Colour · 12 Type · 13 Imagery and motion · 14 Applications · 15 Do and don't · 16 Checklist and next steps (+ architecture page between 4 and 5 when two linked brands). `build_book.py` omits sections whose data is empty and never leaves a heading alone.

## brand.json schema
```
{ "name", "tagline", "language", "date": "YYYYMMDD", "tagline_alts": [],
  "story": "", "belief": "",
  "sources": ["[FACTS] …"],
  "positioning": {"audience","alternatives":[],"frame","statement","plain","promise",
                  "values":[{"name","behaviour"}], "proof":[{"claim","evidence","source"}], "not":[]},
  "archetype": {"primary","shadow","why","example_lines":[]},
  "architecture": {"model","shared":[],"differs":[],"usage":""},   // optional
  "voice": {"adjectives":[{"word","meaning","do","dont"}], "habits":[],
            "tone_map":[{"context","tone","opening"}],
            "pitches":{"s10","s30","s60"}, "pillars":[{"theme","message","proof"}],
            "banned":[]},
  "visual": {"colors":[{"token","hex","role","share"}],
             "pairs":[{"fg":"token","bg":"token","size":"body|large"}],
             "type":[{"layer","font","fallback","note"}],
             "logo":{"routes":[{"idea","expresses"}],"rules":[],"misuse":[],"deliverables":[]},
             "imagery":[], "motion":[], "layout":[]},
  "dos":[], "donts":[], "next_steps":[], "todo":[]
}
```
Missing keys are fine; empty sections drop out.

## Outputs
- `brand-book.html` — self-contained (inline CSS using the brand's own palette/fonts via Google Fonts link with fallback), print CSS with `@page A4`, `break-before:page` on each section, `break-inside:avoid` on cards.
- `brand-book.pdf` — headless Chrome print; script prints page count. Expected pages = number of sections + cover. Mismatch means a section overflowed: shorten text or split the section deliberately.
- `brand-kit.md` — the `formula/brands/_template.md` shape: Identity, Voice, CTA per pillar, Color, Type, Visual rules. Downstream skills read it without edits.

## Look and feel
The book should use the brand it documents (palette as page accents, brand fonts for headings), with a neutral reading layout: 20 mm margins, 11 pt body, generous space. Reference quality bar: RS Brand Kit (`Regenerative Stories/03 Brand & Identity/Brand Kit/RS-Brand-Kit.html`).

## Delivery
Save to the brand folder as `YYYYMMDD <Name> Brand Book.html/.pdf` (English, no overwrite). Tell the user the final path in one line.
