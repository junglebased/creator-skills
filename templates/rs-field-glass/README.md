# rs-field-glass · RS ripple reel template (HyperFrames)

First prototype of the motion agent (`docs/SPEC-20261012-motion-agent.md` §4, §9, §10).
One 9:16 reel, 1080×1920, 30 fps, 18 s: hook → three ripple rings ("dalga etkisi") → credit end card.
First fill: Mikro Onarım (Burhan Eltan), 13 Oct 2026. Draft only; Berkay approves before anything is posted.

## Locked brief

- **BAR**: reads like a frame from an RS film with one sourced number on it, never like an ad.
- **FORMAT**: 9:16, 18 s. 0-1.9 s hook (name + place over the film plate) · 3 rings × ~4.3 s · 3 s end card.
- **ONE RULE**: one ring, one number, one source line. No source, no number on screen.
- **LOOK**: own film still as plate (slow 7% push, focus-pull to 5px blur when the data lands), humus gradient,
  frosted "field card" in the lower third. Humus/mist neutrals, sprout-400 for the active ring, gold for one word.
- **TYPE**: Clash Display (numbers), Satoshi (lines, labels, sources), Boska italic (names, attribution, titles).
- **MOTION**: stroke draw-on rings, per-digit odometer, low-bounce settle (`back.out(1.15)`), holds ≥1.2 s.
  Dots drop and settle like seeds; no bounce, no shake, no flashes.
- **NEVER**: unsourced yield/health/carbon numbers; views written as people; exclamation marks; stock or AI footage;
  the YouTube clickbait title; em dashes in public copy.

## Files

| File | Role |
|---|---|
| `composition/index.html` | HyperFrames composition. Edit only the `SCENE` block per reel. |
| `composition/tokens.css` | Brand + layout tokens (palette, type sizes, card, safe zone). Fonts load from `assets/fonts/`. |
| `build.sh` | Copies licensed fonts from the RS brand kit, crops 9:16 plates from 4K film stills (`PLATES` list), renders, exports 0 s / 8 s / last frame PNGs. |
| `composition/assets/` | Fonts and plates, gitignored (licensed fonts, own footage). Rebuilt by `build.sh`. |

## Run

```bash
cd templates/rs-field-glass && ./build.sh "$HOME/Desktop/2 Areas/Regenerative Stories/05 Channels & Social/00 Drafts"
```

Needs Node, ffmpeg, Chrome and local port binding (the renderer serves the page on 127.0.0.1).
`HF=/path/to/hyperframes ./build.sh` uses a local CLI install instead of `npx hyperframes@0.8.150`.
`npx hyperframes@0.8.150 check` inside `composition/` runs lint + runtime + layout checks.

## Fill: Mikro Onarım (13 Oct 2026)

| Ring | On screen | Source |
|---|---|---|
| 1 · Bahçe | 30 m² · 4 yatak × 7,5 m² | Burhan Eltan interview, 2 Oct 2026, A 10:02:22 |
| 2 · Aile | 4–6 kişi · bir ailenin sebzesi, tüm gıdası değil · "Burhan'ın gözlemi" | same, A 10:02:34 (vegetables, not all food) |
| 3 · Film | 225.349 kez izlendi, yayından sonraki 15 günde | YouTube public counter, 7 Oct 2026 (case study) |

Plates: film stills 0217 (beds, drone), 0487 (Burhan, interview), 0103 (Kaz Dağları aerial) from
`01 Films/2026 Mikro Onarım/06 Content/_Görsel Havuzu/Film Kareleri (Master 4K)`.

Known gaps: ring 3 should be village/cooperative/ecosystem, but the 2026 interview has no sourced number for it
(no neighbour, trainee or garden count), so it uses film views. No music bed. TR only; EN variant = new `SCENE` text.
