# Content Factory · production rules (shared by every CF skill)

Source: Berkay, 16 Oct 2026, from the E1 OMB carousel work. Brand-agnostic: brand kits supply fonts, sizes
and colours; these rules supply the method. Every CF skill (visual-index/visual-select, copy, design,
caption/CTA, QA, publish-pack) links here instead of restating them.

## R1 · Slide text line breaks: manual and balanced
- Never let the renderer wrap text. Write each line break yourself.
- Break first at a comma or sentence end, then at a natural phrase boundary (never between an adjective and
  its noun, a number and its unit, a name and surname, or before a one-word last line).
- Keep line lengths close to each other (balanced rag; the longest line ≤ 1.3× the shortest).
- Headline max 3 lines (4 only if unavoidable). Body max 3 lines. If it does not fit: shorten the text first,
  then lower the point size one step, never squeeze tracking.
- Measure, don't guess. 1080 px slide, 72 px side margins (936 px text width):
  - RS display serif (Boska) 76 px ≈ 22–24 characters per line
  - RS body (Satoshi) 44 px ≈ 38–40 characters per line
  - For other brand fonts: set one line in the brand kit's size, count characters that fit 936 px, write the
    number into the brand kit as `chars_per_line` per style.
- QA: count characters per line against the brand kit numbers; flag any line over the limit or any slide over
  the line limit.

## R2 · Carousel delivery: ONE Claude Design canvas
- A carousel is delivered as one Claude Design canvas holding:
  1. one editable artboard per slide (1080×1350 or the brand format), and
  2. a full-page `Swipe.dc.html` (dc-import of the artboards, scroll-snap, ‹ › buttons, dots).
- The share link opens with `launch=focused` in the Swipe view, so the reviewer swipes like on the phone.
- Example: https://claude.ai/artifact/FNqeZCn6ekYpcZxfkEgdL3
- PNG exports (`04 Export/<code>_NN.png`) are made from the same artboards; no separate hand-made copies.

## R3 · Series look: one grade for the whole piece
- Every frame of a carousel or reel (photos, video frames, film stills, the video slot) passes through ONE
  `.cube` for that piece or campaign, with the same white-balance target, contrast and saturation.
- Log sources first get their technical conversion LUT (e.g. Fuji F-Log2 → 709), then the series look.
  Rec709 sources (film masters, JPGs) get only the series look.
- Outliers are fixed before the look (exposure/WB per frame, e.g. −⅓ stop on a bright sky), not by changing
  the look.
- Stills: `visual-index grade` (ffmpeg lut3d) writes graded copies + a before/after compare grid. Video slots:
  the same `.cube` in DaVinci Resolve (match there if a clip still drifts). Save the look next to the piece
  (`03 Tasarım/look/<campaign>.cube`) with the script/notes that produced it.
- QA: one compare grid of all slides side by side before export; any frame that reads as a different
  "film" fails.
