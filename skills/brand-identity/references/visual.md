# Stage 4 — Visual identity

## Audit first
Extract what exists: colour tokens from site CSS, fonts in use, current logo/wordmark, signature layout, photo style. Table: element · current · keep / fix / replace · why.

## Palette
Roles, not just hexes: ink (darkest), paper (lightest), primary accent, secondary accent, support/earth, signal (success/alert if needed). 5-7 colours max. Each: token name · hex · role · use-ratio (e.g. 60/25/10/5) · "never" rule.
Run `python3 scripts/contrast.py brand/brand.json` — it tests every text/background pairing the book declares; fix any < 4.5:1 (large text < 3:1).
Name colours after the brand's world, not "blue 2".

## Type
Heading, body, accent/meta. Prefer fonts the client can actually get (Google Fonts / already owned); note licence and a system fallback. Give a scale (e.g. 12/14/18/28/48), line-height, tracking rule, max line length. Pair by contrast (serif display + neutral sans text is a safe default; justify any other choice).

## Logo brief (brief only)
- Concept routes (2-3): idea · what it expresses · sketch description.
- Must work: one colour, 16 px favicon, on photo, on dark.
- Rules: clear space (x unit), minimum size, lockups (horizontal/stacked/mark only), misuse list (stretch, recolour, shadow, busy background).
- Deliverables for the designer: files, formats, versions.
If a wordmark in the chosen typeface is enough, say so.

## Imagery
Photo direction tied to the positioning (subjects, light, framing, colour grade, what is banned: stock, AI faces, over-saturation). Treatments: grain, overlays, crop ratios, caption style. For film brands: still-frame selection rules and title-card style.

## Motion and layout
Easing, duration range, transitions allowed; grid, margins, spacing unit, corner radius, rule weights. Keep to ten rules or fewer.

## Applications (mock in the book as simple HTML blocks, not images)
Email signature, social post/cover, business card or one-pager header, slide title, site hero.
