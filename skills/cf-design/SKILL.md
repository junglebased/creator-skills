---
name: cf-design
description: Designs a Content Factory carousel/cover for any brand as ONE Claude Design canvas (rule R2): one editable artboard per slide in the brand format + a full-page Swipe.dc.html (dc-import, scroll-snap, ‹ › buttons, dots) opened with launch=focused, built from slides.json (text with manual line breaks) and the graded picks (rule R3, one .cube per piece). Exports 04 Export/<code>_NN.png from the same artboards. Use when the user says "/cf-design", "tasarla", "Claude Design'da kur", "carousel tasarımı", "swipe görünümü", or after copy is approved.
---

# cf-design

Pipeline: `… → copy → **design** → caption/CTA → QA → publish-pack`.
Contract: `docs/CF-PIECE-CONTRACT.md` · R1–R3: `docs/CF-PRODUCTION-RULES.md`.
Builds on `/formula make` step 4 (Claude Design via the Artifact tool), the brand kit (tokens, fonts, logo),
`visual-index grade` (R3) and, for video slots, `/resolve` (same `.cube`) or `/motion`.

## Inputs
- `02 Metin/<code>.slides.json` (approved text; line breaks are final — do not rewrap).
- Picks: `01 Kaynak Görsel/graded/<id>_graded.jpg` (run `visual-index grade` first with the piece's look);
  crop per `crop_fit` / `text_safe` of each id.
- Brand kit: colours, fonts (files), logo path + corner, format size, safe area.

## Steps
1. **Look (R3).** If `slides.json.look` is empty: make/choose one `.cube` for the campaign, save it to
   `03 Tasarım/look/<campaign>.cube`, run `vindex.py grade <ids in slot order> --lut … --out "01 Kaynak Görsel/graded"`,
   check the compare grid. Video slots get the same `.cube` in Resolve.
2. **Canvas (R2).** Artifact tool → `action: "quickstart"`, intent `design` (or `slides` if the account's
   Slides type fits). One artboard per slot at the brand size (RS 1080×1350), named `<code>_NN`. Upload the graded
   picks as assets. Text exactly as the line arrays (each array item = one line; no auto-wrap: fixed-width boxes
   with `white-space: pre` or explicit `<br>`).
3. **Swipe view.** Add `Swipe.dc.html`: dc-import of the artboards in order, CSS scroll-snap, ‹ › buttons, dot
   indicator; this is the page the review link opens with `launch=focused`.
4. **Brand.** Logo fixed corner, small; one accent word max (RS gold); text on the `text_safe` side, never on a
   face; gradient only if the visual has no clean area.
5. **Export.** PNG per artboard → `04 Export/<code>_NN.png` (exact pixel size). Record canvas + Swipe links in
   `03 Tasarım/links.md`.
6. Run `cf-qa`.

## Gate
All slots rendered from files (no hand-retyped text), exports at exact size, compare grid reads as one look,
one review link (Swipe, launch=focused) sent to the user.
